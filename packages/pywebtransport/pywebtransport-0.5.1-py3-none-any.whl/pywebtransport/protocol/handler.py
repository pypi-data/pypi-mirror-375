"""
WebTransport Protocol Handler.
"""

from __future__ import annotations

import asyncio
import weakref
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Self

from aioquic.quic.connection import QuicConnection, QuicConnectionState
from aioquic.quic.events import QuicEvent, StreamReset

from pywebtransport.events import Event, EventEmitter
from pywebtransport.exceptions import ConnectionError, ProtocolError, TimeoutError
from pywebtransport.protocol import utils as protocol_utils
from pywebtransport.protocol.events import (
    DatagramReceived,
    DataReceived,
    H3Event,
    HeadersReceived,
    WebTransportStreamDataReceived,
)
from pywebtransport.protocol.h3_engine import WebTransportH3Engine
from pywebtransport.protocol.session_info import StreamInfo, WebTransportSessionInfo
from pywebtransport.types import (
    ConnectionState,
    Data,
    EventType,
    Headers,
    SessionId,
    SessionState,
    StreamDirection,
    StreamId,
    StreamState,
)
from pywebtransport.utils import (
    Timer,
    ensure_bytes,
    generate_session_id,
    get_logger,
    get_timestamp,
    validate_session_id,
    validate_stream_id,
)

if TYPE_CHECKING:
    from pywebtransport.connection import WebTransportConnection


__all__ = ["WebTransportProtocolHandler"]

logger = get_logger(name="protocol.handler")


class WebTransportProtocolHandler(EventEmitter):
    """Orchestrates WebTransport sessions and streams over a QUIC connection."""

    def __init__(
        self,
        *,
        quic_connection: QuicConnection,
        is_client: bool = True,
        connection: WebTransportConnection | None = None,
    ):
        """Initialize the WebTransport protocol handler."""
        super().__init__()
        self._quic = quic_connection
        self._is_client = is_client
        self._connection_ref = weakref.ref(connection) if connection else None
        self._h3: WebTransportH3Engine = WebTransportH3Engine(quic=self._quic, enable_webtransport=True)
        self._sessions: dict[SessionId, WebTransportSessionInfo] = {}
        self._streams: dict[StreamId, StreamInfo] = {}
        self._session_control_streams: dict[StreamId, SessionId] = {}
        self._data_stream_to_session: dict[StreamId, SessionId] = {}
        self._session_owned_streams: dict[SessionId, set[StreamId]] = defaultdict(set)
        self._connection_state: ConnectionState = ConnectionState.IDLE
        self._last_activity = get_timestamp()
        self._stats: dict[str, Any] = {
            "bytes_sent": 0,
            "bytes_received": 0,
            "sessions_created": 0,
            "streams_created": 0,
            "datagrams_sent": 0,
            "datagrams_received": 0,
            "errors": 0,
            "connected_at": None,
        }
        logger.debug("WebTransport protocol handler initialized (client=%s)", is_client)

    @classmethod
    def create(
        cls,
        *,
        quic_connection: QuicConnection,
        is_client: bool = True,
        connection: WebTransportConnection | None = None,
    ) -> Self:
        """Factory method to create a new WebTransport protocol handler instance."""
        return cls(quic_connection=quic_connection, is_client=is_client, connection=connection)

    @property
    def is_connected(self) -> bool:
        """Check if the underlying connection is established."""
        return self._connection_state == ConnectionState.CONNECTED

    @property
    def connection(self) -> WebTransportConnection | None:
        """Get the parent WebTransportConnection via a weak reference."""
        return self._connection_ref() if self._connection_ref else None

    @property
    def connection_state(self) -> ConnectionState:
        """Get the current state of the underlying connection."""
        return self._connection_state

    @property
    def quic_connection(self) -> QuicConnection:
        """Get the underlying aioquic QuicConnection object."""
        return self._quic

    @property
    def stats(self) -> dict[str, Any]:
        """Get a copy of the protocol handler's statistics."""
        return self._stats.copy()

    async def close(self) -> None:
        """Close the protocol handler and clean up its resources."""
        if self._connection_state == ConnectionState.CLOSED:
            return
        self._connection_state = ConnectionState.CLOSED

        await super().close()

    def connection_established(self) -> None:
        """Signal that the QUIC connection is established."""
        if self._connection_state in [ConnectionState.IDLE, ConnectionState.CONNECTING]:
            self._connection_state = ConnectionState.CONNECTED
            self._stats["connected_at"] = get_timestamp()
            logger.info("Connection established.")
            self._trigger_transmission()

    def abort_stream(self, *, stream_id: StreamId, error_code: int) -> None:
        """Abort a stream immediately."""
        logger.warning("Aborting stream %d with error code %d", stream_id, error_code)
        self._quic.reset_stream(stream_id=stream_id, error_code=error_code)
        self._trigger_transmission()
        self._cleanup_stream(stream_id=stream_id)

    def accept_webtransport_session(self, *, stream_id: StreamId, session_id: SessionId) -> None:
        """Accept a pending WebTransport session (server-only)."""
        if self._is_client:
            raise ProtocolError("Only servers can accept WebTransport sessions")

        session_info = self._sessions.get(session_id)
        if not session_info or session_info.stream_id != stream_id:
            raise ProtocolError(f"No pending session found for stream {stream_id} and id {session_id}")

        self._h3.send_headers(stream_id=stream_id, headers={":status": "200"})
        session_info.state = SessionState.CONNECTED
        session_info.ready_at = get_timestamp()

        self._trigger_transmission()
        asyncio.create_task(self.emit(event_type=EventType.SESSION_READY, data=session_info.to_dict()))
        logger.info("Accepted WebTransport session: %s", session_id)

    def close_webtransport_session(self, *, session_id: SessionId, code: int = 0, reason: str | None = None) -> None:
        """Close a specific WebTransport session."""
        session_info = self._sessions.get(session_id)
        if not session_info or session_info.state == SessionState.CLOSED:
            return

        logger.info("Closing WebTransport session: %s (code=%d)", session_id, code)
        self._quic.reset_stream(stream_id=session_info.stream_id, error_code=code)
        self._trigger_transmission()
        self._cleanup_session(session_id=session_id)
        asyncio.create_task(
            self.emit(
                event_type=EventType.SESSION_CLOSED,
                data={"session_id": session_id, "code": code, "reason": reason},
            )
        )

    async def create_webtransport_session(
        self, *, path: str, headers: Headers | None = None
    ) -> tuple[SessionId, StreamId]:
        """Initiate a new WebTransport session (client-only)."""
        if not self._is_client:
            raise ProtocolError("Only clients can create WebTransport sessions")

        session_id = generate_session_id()
        headers_dict = headers or {}
        server_name = self._quic.configuration.server_name
        authority = headers_dict.get("host") or server_name or "localhost"

        connect_headers: Headers = {
            ":method": "CONNECT",
            ":protocol": "webtransport",
            ":scheme": "https",
            ":path": path,
            ":authority": authority,
            **headers_dict,
        }

        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=False)
        self._h3.send_headers(stream_id=stream_id, headers=connect_headers, end_stream=False)

        session_info = WebTransportSessionInfo(
            session_id=session_id,
            stream_id=stream_id,
            state=SessionState.CONNECTING,
            created_at=get_timestamp(),
            path=path,
            headers=headers_dict,
        )
        self._register_session(session_id=session_id, session_info=session_info)
        self._trigger_transmission()
        logger.info(
            "Initiated WebTransport session: %s on control stream %d",
            session_id,
            stream_id,
        )
        return session_id, stream_id

    def create_webtransport_stream(self, *, session_id: SessionId, is_unidirectional: bool = False) -> StreamId:
        """Create a new WebTransport data stream for a session."""
        session_info = self._sessions.get(session_id)
        if not session_info or session_info.state != SessionState.CONNECTED:
            raise ProtocolError(f"Session {session_id} not found or not ready")

        stream_id = self._h3.create_webtransport_stream(
            session_id=session_info.stream_id, is_unidirectional=is_unidirectional
        )
        direction = StreamDirection.SEND_ONLY if is_unidirectional else StreamDirection.BIDIRECTIONAL
        self._register_stream(session_id=session_id, stream_id=stream_id, direction=direction)

        self._trigger_transmission()
        logger.debug("Created WebTransport stream %d (%s)", stream_id, direction)
        return stream_id

    async def establish_session(
        self, *, path: str, headers: Headers | None = None, timeout: float = 30.0
    ) -> tuple[SessionId, StreamId]:
        """Establish a WebTransport session with a specified timeout."""
        if not self.is_connected:
            raise ConnectionError("Protocol not connected")
        with Timer(name="establish_session") as timer:
            session_id, stream_id = await asyncio.wait_for(
                self.create_webtransport_session(path=path, headers=headers),
                timeout=timeout,
            )

            def session_ready_condition(event: Event) -> bool:
                return isinstance(event.data, dict) and event.data.get("session_id") == session_id

            await self.wait_for(
                event_type=EventType.SESSION_READY,
                timeout=timeout,
                condition=session_ready_condition,
            )
            logger.info(
                "WebTransport session established in %.2fs: %s",
                timer.elapsed,
                session_id,
            )
            return session_id, stream_id

    async def handle_quic_event(self, *, event: QuicEvent) -> None:
        """Process a QUIC event through the H3 engine and handle results."""
        if self._connection_state == ConnectionState.CLOSED:
            return

        if isinstance(event, StreamReset):
            await self._handle_stream_reset(event=event)

        h3_events = self._h3.handle_event(event=event)
        for h3_event in h3_events:
            await self._handle_h3_event(h3_event=h3_event)
        self._trigger_transmission()

    def send_webtransport_datagram(self, *, session_id: SessionId, data: bytes) -> None:
        """Send a WebTransport datagram for a session."""
        session_info = self._sessions.get(session_id)
        if not session_info or session_info.state != SessionState.CONNECTED:
            raise ProtocolError(f"Session {session_id} not found or not ready")

        self._h3.send_datagram(stream_id=session_info.stream_id, data=data)
        self._stats["bytes_sent"] += len(data)
        self._stats["datagrams_sent"] += 1
        self._trigger_transmission()

    def send_webtransport_stream_data(self, *, stream_id: StreamId, data: bytes, end_stream: bool = False) -> None:
        """Send data on a specific WebTransport stream."""
        stream_info = self._streams.get(stream_id)
        if not stream_info or stream_info.state in (
            StreamState.HALF_CLOSED_LOCAL,
            StreamState.CLOSED,
        ):
            raise ProtocolError(f"Stream {stream_id} not found or not writable")

        self._h3.send_data(stream_id=stream_id, data=data, end_stream=end_stream)
        self._stats["bytes_sent"] += len(data)
        stream_info.bytes_sent += len(data)
        self._trigger_transmission()
        if end_stream:
            self._update_stream_state_on_send_end(stream_id=stream_id)

    def get_all_sessions(self) -> list[WebTransportSessionInfo]:
        """Get a list of all current sessions."""
        return list(self._sessions.values())

    def get_health_status(self) -> dict[str, Any]:
        """Get the overall health status of the protocol handler."""
        stats = self.stats
        sessions = self.get_all_sessions()
        streams = list(self._streams.values())
        active_sessions = sum(1 for s in sessions if s.state == SessionState.CONNECTED)
        active_streams = sum(1 for s in streams if s.state == StreamState.OPEN)
        error_rate = stats.get("errors", 0) / max(1, stats.get("sessions_created", 1))

        health_status = "healthy"
        if error_rate > 0.1:
            health_status = "degraded"
        elif not self.is_connected:
            health_status = "unhealthy"

        return {
            "status": health_status,
            "connection_state": self.connection_state,
            "active_sessions": active_sessions,
            "active_streams": active_streams,
            "total_sessions": len(sessions),
            "total_streams": len(streams),
            "error_rate": error_rate,
            "last_activity": stats.get("last_activity"),
            "uptime": (get_timestamp() - stats["connected_at"]) if stats.get("connected_at") else 0.0,
        }

    def get_session_info(self, *, session_id: SessionId) -> WebTransportSessionInfo | None:
        """Get information about a specific session."""
        return self._sessions.get(session_id)

    async def read_stream_complete(self, *, stream_id: StreamId, timeout: float = 30.0) -> bytes:
        """Receive all data from a stream until it is ended."""
        chunks: list[bytes] = []
        future = asyncio.get_running_loop().create_future()

        async def data_handler(event: Event) -> None:
            if future.done():
                return
            if event.data:
                chunks.append(event.data.get("data", b""))
                if event.data.get("end_stream"):
                    future.set_result(None)

        event_name = f"stream_data_received:{stream_id}"
        self.on(event_type=event_name, handler=data_handler)
        try:
            await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout waiting for stream {stream_id} to end") from None
        finally:
            self.off(event_type=event_name, handler=data_handler)
        return b"".join(chunks)

    async def recover_session(self, *, session_id: SessionId, max_retries: int = 3) -> bool:
        """Attempt to recover a failed session by creating a new one."""
        validate_session_id(session_id=session_id)
        session_info = self.get_session_info(session_id=session_id)
        if not session_info:
            return False
        for attempt in range(max_retries):
            try:
                new_session_id, _ = await self.create_webtransport_session(
                    path=session_info.path, headers=session_info.headers
                )
                logger.info(
                    "Recovered session %s as new session %s (attempt %d)",
                    session_id,
                    new_session_id,
                    attempt + 1,
                )
                return True
            except Exception as e:
                logger.warning(
                    "Session recovery attempt %d failed: %s",
                    attempt + 1,
                    e,
                    exc_info=True,
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
        return False

    def write_stream_chunked(self, *, stream_id: StreamId, data: Data, chunk_size: int = 8192) -> int:
        """Send data on a stream in managed chunks."""
        validate_stream_id(stream_id=stream_id)
        data_bytes = ensure_bytes(data=data)
        total_sent = 0
        for i in range(0, len(data_bytes), chunk_size):
            chunk = data_bytes[i : i + chunk_size]
            is_last_chunk = (i + chunk_size) >= len(data_bytes)
            try:
                self.send_webtransport_stream_data(stream_id=stream_id, data=chunk, end_stream=is_last_chunk)
                total_sent += len(chunk)
            except Exception as e:
                logger.error(
                    "Error sending chunk %d for stream %d: %s",
                    i // chunk_size + 1,
                    stream_id,
                    e,
                    exc_info=True,
                )
                break
        return total_sent

    def _cleanup_session(self, *, session_id: SessionId) -> None:
        """Remove a session and all its associated streams."""
        if session_info := self._sessions.pop(session_id, None):
            self._session_control_streams.pop(session_info.stream_id, None)
            stream_ids_to_remove = list(self._session_owned_streams.pop(session_id, set()))
            for stream_id in stream_ids_to_remove:
                self._cleanup_stream(stream_id=stream_id)
            logger.info("Cleaned up session %s and its associated streams.", session_id)

    def _cleanup_stream(self, *, stream_id: StreamId) -> None:
        """Remove a single stream from internal tracking."""
        if self._streams.pop(stream_id, None):
            session_id = self._data_stream_to_session.pop(stream_id, None)
            if session_id and session_id in self._session_owned_streams:
                self._session_owned_streams[session_id].discard(stream_id)
            asyncio.create_task(self.emit(event_type=f"stream_closed:{stream_id}"))

    async def _handle_datagram_received(self, *, event: DatagramReceived) -> None:
        """Handle a datagram received from the H3 engine."""
        if connection := self.connection:
            if hasattr(connection, "record_activity"):
                connection.record_activity()
        self._last_activity = get_timestamp()
        self._stats["bytes_received"] += len(event.data)
        self._stats["datagrams_received"] += 1

        if session_id := self._session_control_streams.get(event.stream_id):
            if self._sessions.get(session_id):
                await self.emit(
                    event_type=EventType.DATAGRAM_RECEIVED,
                    data={"session_id": session_id, "data": event.data},
                )

    async def _handle_h3_event(self, *, h3_event: H3Event) -> None:
        """Route H3 events to their specific handlers."""
        match h3_event:
            case HeadersReceived():
                await self._handle_session_headers(event=h3_event)
            case WebTransportStreamDataReceived():
                await self._handle_webtransport_stream_data(event=h3_event)
            case DatagramReceived():
                await self._handle_datagram_received(event=h3_event)
            case DataReceived():
                pass
            case _:
                logger.debug("Ignoring unhandled H3 event: %s", type(h3_event))

    async def _handle_session_headers(self, *, event: HeadersReceived) -> None:
        """Handle HEADERS frames for session negotiation."""
        if connection := self.connection:
            if hasattr(connection, "record_activity"):
                connection.record_activity()
        self._last_activity = get_timestamp()
        headers_dict = event.headers
        logger.debug("H3 headers received on stream %d: %s", event.stream_id, headers_dict)

        if self._is_client:
            if session_id := self._session_control_streams.get(event.stream_id):
                if session_id in self._sessions and headers_dict.get(":status") == "200":
                    session = self._sessions[session_id]
                    session.state = SessionState.CONNECTED
                    session.ready_at = get_timestamp()
                    logger.info("Client session %s is ready.", session_id)
                    await self.emit(event_type=EventType.SESSION_READY, data=session.to_dict())
                elif session_id:
                    status = headers_dict.get(":status", "unknown")
                    logger.error("Session %s creation failed with status %s", session_id, status)
                    await self.emit(
                        event_type=EventType.SESSION_CLOSED,
                        data={
                            "session_id": session_id,
                            "code": 1,
                            "reason": f"HTTP status {status}",
                        },
                    )
                    self._cleanup_session(session_id=session_id)
        elif headers_dict.get(":method") == "CONNECT" and headers_dict.get(":protocol") == "webtransport":
            session_id = generate_session_id()
            app_headers = headers_dict
            session_info = WebTransportSessionInfo(
                session_id=session_id,
                stream_id=event.stream_id,
                state=SessionState.CONNECTING,
                created_at=get_timestamp(),
                path=app_headers.get(":path", "/"),
                headers=app_headers,
            )
            self._register_session(session_id=session_id, session_info=session_info)
            event_data = session_info.to_dict()
            if connection := self.connection:
                event_data["connection"] = connection
            logger.info(
                "Received WebTransport session request: %s for path '%s'",
                session_id,
                session_info.path,
            )
            await self.emit(event_type=EventType.SESSION_REQUEST, data=event_data)

    async def _handle_stream_reset(self, *, event: StreamReset) -> None:
        """Handle a reset stream event."""
        if session_id := self._session_control_streams.get(event.stream_id):
            logger.info(
                "Session %s closed due to control stream %d reset.",
                session_id,
                event.stream_id,
            )
            await self.emit(
                event_type=EventType.SESSION_CLOSED,
                data={
                    "session_id": session_id,
                    "code": event.error_code,
                    "reason": "Control stream reset",
                },
            )
            self._cleanup_session(session_id=session_id)

    async def _handle_webtransport_stream_data(self, *, event: WebTransportStreamDataReceived) -> None:
        """Handle data received on a WebTransport data stream."""
        if connection := self.connection:
            if hasattr(connection, "record_activity"):
                connection.record_activity()
        stream_id = event.stream_id
        session_stream_id = event.session_id

        if stream_id not in self._data_stream_to_session:
            if not (session_id := self._session_control_streams.get(session_stream_id)):
                if self._quic._state not in (
                    QuicConnectionState.CLOSING,
                    QuicConnectionState.DRAINING,
                ):
                    logger.error(
                        "No session mapping found for session_stream_id %d on new stream %d.",
                        session_stream_id,
                        stream_id,
                    )
                return

            direction = protocol_utils.get_stream_direction_from_id(stream_id=stream_id, is_client=self._is_client)
            self._register_stream(session_id=session_id, stream_id=stream_id, direction=direction)

            event_data = self._streams[stream_id].to_dict()
            event_data["initial_payload"] = {
                "data": event.data,
                "end_stream": event.stream_ended,
            }
            await self.emit(event_type=EventType.STREAM_OPENED, data=event_data)
        else:
            await self.emit(
                event_type=f"stream_data_received:{stream_id}",
                data={"data": event.data, "end_stream": event.stream_ended},
            )

    def _register_session(self, *, session_id: SessionId, session_info: WebTransportSessionInfo) -> None:
        """Add a new session to internal tracking."""
        self._sessions[session_id] = session_info
        self._session_control_streams[session_info.stream_id] = session_id
        self._stats["sessions_created"] += 1

    def _register_stream(self, *, session_id: SessionId, stream_id: StreamId, direction: StreamDirection) -> StreamInfo:
        """Add a new stream to internal tracking."""
        stream_info = StreamInfo(
            stream_id=stream_id,
            session_id=session_id,
            direction=direction,
            state=StreamState.OPEN,
            created_at=get_timestamp(),
        )
        self._streams[stream_id] = stream_info
        self._data_stream_to_session[stream_id] = session_id
        self._session_owned_streams[session_id].add(stream_id)
        self._stats["streams_created"] += 1
        logger.debug("Registered %s stream %d for session %s", direction, stream_id, session_id)
        return stream_info

    def _trigger_transmission(self) -> None:
        """Trigger the underlying QUIC connection to send pending data."""
        if connection := self.connection:
            if hasattr(connection, "_transmit"):
                connection._transmit()

    def _update_stream_state_on_receive_end(self, *, stream_id: StreamId) -> None:
        """Update stream state when its receiving side is closed."""
        if not (stream_info := self._streams.get(stream_id)):
            return
        new_state = StreamState.HALF_CLOSED_REMOTE
        if stream_info.state == StreamState.HALF_CLOSED_LOCAL:
            new_state = StreamState.CLOSED
        stream_info.state = new_state
        if new_state == StreamState.CLOSED:
            self._cleanup_stream(stream_id=stream_id)

    def _update_stream_state_on_send_end(self, *, stream_id: StreamId) -> None:
        """Update stream state when its sending side is closed."""
        if not (stream_info := self._streams.get(stream_id)):
            return
        new_state = StreamState.HALF_CLOSED_LOCAL
        if stream_info.state == StreamState.HALF_CLOSED_REMOTE:
            new_state = StreamState.CLOSED
        stream_info.state = new_state
        if new_state == StreamState.CLOSED:
            self._cleanup_stream(stream_id=stream_id)
