ngrok_api_token_p="2urDwsLw8RhcLSAKwRLqT9Mg1Vn_Ca55uWwkDNc9iu6tcpwk"
import os
import sys
import time
import atexit
import signal
import threading
import argparse
import logging
from typing import Dict, Any, Optional, Set

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import socketio  # python-socketio
from pyngrok import ngrok


# ------------ Logging ------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("mmohost")


class MMOHost:
    def __init__(self, port: int = 8000, host: str = "127.0.0.1", ngrok_authtoken: Optional[str] = None):
        self.port = int(port)
        self.host = host

        self._server_thread: Optional[threading.Thread] = None
        self._uvicorn_server: Optional[uvicorn.Server] = None
        self._ngrok_tunnel = None
        self.public_url: Optional[str] = None
        self._stop_event = threading.Event()

        # --- Game state (simple demo) ---
        self.players: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, Set[str]] = {"lobby": set()}

        # --- FastAPI & Socket.IO ---
        self.app = FastAPI(title="Telegram webhook server", version="0.1.0")
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.asgi_app = socketio.ASGIApp(self.sio, other_asgi_app=self.app)

        # HTTP routes
        @self.app.get("/")
        async def root():
            return {"ok": True, "service": "private-ngrok-app", "public_url": self.public_url}

        @self.app.get("/players")
        async def get_players():
            return JSONResponse(self.players)

        @self.app.get("/healthz")
        async def healthz():
            return {"status": "ok", "time": time.time()}

        # Socket.IO events
        @self.sio.event
        async def connect(sid, environ):
            await self.sio.save_session(sid, {"rooms": set()})
            await self.sio.emit("server_info", {"msg": "connected", "sid": sid}, to=sid)
            log.info("Client connected: %s", sid)

        @self.sio.event
        async def disconnect(sid):
            sess = await self.sio.get_session(sid)
            rooms_to_leave = list(sess.get("rooms", [])) if sess else []
            for r in rooms_to_leave:
                self.rooms.setdefault(r, set()).discard(sid)
                await self.sio.emit("room_info", {"room": r, "event": "left", "sid": sid}, room=r)
            log.info("Client disconnected: %s", sid)

        @self.sio.on("join_room")
        async def on_join_room(sid, data):
            data = data or {}
            room = str(data.get("room", "lobby"))
            player_id = str(data.get("player_id", sid))

            self.rooms.setdefault(room, set()).add(sid)
            sess = await self.sio.get_session(sid)
            if sess is not None:
                rs = set(sess.get("rooms", set()))
                rs.add(room)
                sess["rooms"] = rs
                await self.sio.save_session(sid, sess)

            # Track player
            self.players[player_id] = self.players.get(
                player_id,
                {"player_id": player_id, "room": room, "x": 0.0, "y": 0.0, "z": 0.0},
            )
            self.players[player_id]["room"] = room

            await self.sio.emit(
                "room_info",
                {"room": room, "event": "joined", "sid": sid, "player_id": player_id},
                room=room,
            )
            log.debug("Player %s joined room %s (sid=%s)", player_id, room, sid)

        @self.sio.on("leave_room")
        async def on_leave_room(sid, data):
            data = data or {}
            room = str(data.get("room", "lobby"))
            self.rooms.setdefault(room, set()).discard(sid)

            sess = await self.sio.get_session(sid)
            if sess is not None:
                rs = set(sess.get("rooms", set()))
                rs.discard(room)
                sess["rooms"] = rs
                await self.sio.save_session(sid, sess)

            await self.sio.emit("room_info", {"room": room, "event": "left", "sid": sid}, room=room)
            log.debug("sid=%s left room %s", sid, room)

        @self.sio.on("state_update")
        async def on_state_update(sid, data):
            data = data or {}
            player_id = str(data.get("player_id", sid))

            # Safe numeric parsing
            def _f(v, default=0.0):
                try:
                    return float(v)
                except Exception:
                    return float(default)

            x = _f(data.get("x", 0))
            y = _f(data.get("y", 0))
            z = _f(data.get("z", 0))

            extra = {k: v for k, v in data.items() if k not in {"player_id", "x", "y", "z"}}
            p = self.players.setdefault(player_id, {"player_id": player_id, "room": "lobby"})
            p.update({"x": x, "y": y, "z": z, **extra})
            room = p.get("room", "lobby")
            await self.sio.emit("state_update", p, room=room, skip_sid=sid)

        @self.sio.on("chat")
        async def on_chat(sid, data):
            data = data or {}
            player_id = str(data.get("player_id", sid))
            msg = str(data.get("message", ""))
            room = str(data.get("room", self.players.get(player_id, {}).get("room", "lobby")))
            await self.sio.emit("chat", {"player_id": player_id, "message": msg, "ts": time.time()}, room=room)

        # --- Configure ngrok auth token (ENV first) ---
        token = ngrok_authtoken or ngrok_api_token_p
        if token:
            try:
                ngrok.set_auth_token(token)
            except Exception as e:
                log.warning("Failed to set ngrok auth token: %s", e)

    # --- Public API ---
    def start(self) -> str:
        """Start uvicorn server in background and open ngrok tunnel. Returns public URL."""
        if self._server_thread and self._server_thread.is_alive():
            return self.public_url or ""

        config = uvicorn.Config(self.asgi_app, host=self.host, port=self.port, log_level="info")
        self._uvicorn_server = uvicorn.Server(config)

        def run_server():
            try:
                self._uvicorn_server.run()
            except Exception as e:
                log.exception("Uvicorn crashed: %s", e)

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

        # Give server a moment to boot
        time.sleep(0.8)

        # Open ngrok tunnel with retries
        last_err = None
        for attempt in range(1, 6):  # up to 5 tries
            try:
                self._ngrok_tunnel = ngrok.connect(addr=self.port, proto="http")
                self.public_url = self._ngrok_tunnel.public_url
                break
            except Exception as e:
                last_err = e
                log.warning("ngrok connect failed (attempt %s/5): %s", attempt, e)
                time.sleep(0.8 * attempt)
        if not self.public_url:
            log.error("Could not start ngrok tunnel after retries")
            if last_err:
                raise last_err
            raise RuntimeError("ngrok.connect failed")

        log.info("Local server: http://%s:%s", self.host, self.port)
        log.info("Public URL via ngrok: %s", self.public_url)

        # Ensure we stop on process exit
        atexit.register(self.stop)
        return self.public_url

    def stop(self):
        """Stop ngrok tunnel and server."""
        if self._stop_event.is_set():
            return
        self._stop_event.set()

        # Close ngrok
        try:
            if self._ngrok_tunnel is not None:
                url = getattr(self._ngrok_tunnel, "public_url", None)
                if url:
                    ngrok.disconnect(url)
                ngrok.kill()  # ensure all processes cleaned up
                self._ngrok_tunnel = None
        except Exception as e:
            log.warning("ngrok disconnect error: %s", e)

        # Stop uvicorn
        try:
            if self._uvicorn_server is not None:
                self._uvicorn_server.should_exit = True
            if self._server_thread is not None and self._server_thread.is_alive():
                self._server_thread.join(timeout=2.5)
        except Exception as e:
            log.warning("server stop error: %s", e)

        log.info("Stopped MMOHost")


# --- Signal handling for graceful shutdown ---
def _install_signal_handlers(host: MMOHost):
    def _handler(signum, frame):
        log.info("Received signal %s, shutting down...", signum)
        host.stop()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, _handler)
        except Exception:
            # On some platforms (e.g., Windows), not all signals are available
            pass


# --- CLI Entrypoint ---
def _main():
    parser = argparse.ArgumentParser(description="Ngrok MMO Web Host SDK")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--ngrok-token", type=str, default=None, help="(optional) ngrok authtoken; otherwise uses NGROK_AUTHTOKEN env")
    args = parser.parse_args()

    host = MMOHost(port=args.port, host=args.host, ngrok_authtoken=args.ngrok_token)
    _install_signal_handlers(host)

    public_url = host.start()
    print(f"Public URL: {public_url}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        host.stop()


if __name__ == "__main__":
    _main()
