"""Cửa sổ chơi trực tiếp bằng TRÌNH DUYỆT, chỉ dùng thư viện chuẩn Python.

    python3 -m chonoi.live --mode gather|quan|day [--seed N] [--port 8000]

Mode day có menu, 5 Ngày, Shop và pause; gather độc lập tự chuyển sang quan
(không phải vòng ngày); dùng `--no-auto-transition` để tắt.

Máy chủ HTTP nhỏ (ThreadingHTTPServer) phục vụ `chonoi/web/index.html` và hai API:
    GET  /state  -> snapshot JSON hiện tại (cùng trường như dòng snapshot của headless) + `meta` + `events`
    POST /input  -> {"move": [a, b], "interact": bool, "catch": bool}   (trạng thái phím đang giữ)
    POST /restart -> chơi lại từ mode ban đầu (cùng seed, cùng scenario)

Mô phỏng chạy 60 tick/s trong một luồng nền, dùng CÙNG lớp sim như headless (qua `runner.Session`).
Client chỉ ĐỌC snapshot và tự bỏ qua trường chưa có, nên luật do nhóm viết thêm trường nào cũng không vỡ.
Ngẫu nhiên vẫn đi qua `Streams` (seed); chỉ nhịp chạy theo đồng hồ thật, không đi vào luật.
"""

import argparse
import json
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .contract import load_contract
from .errors import BadInput
from .inputs import LiveInputs, BUTTONS_V11
from .inventory import read_inventory
from .runner import Session
from .scenario import load_scenario

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
TICK_S = 1.0 / 60.0
MAX_BODY = 4096
RECENT_EVENTS = 40


class LiveGame:
    """Một lượt chơi + luồng nền bước 60 tick/s. Mọi truy cập trạng thái đi qua khóa."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None, inventory_out=None, auto_transition=True, days=5):
        self._args = (mode, tuning, scenario, seed, inventory)
        self.days = days
        self._seed = seed
        self.auto_transition = auto_transition
        self.mode = mode
        self.tuning = tuning
        self.inventory_out = inventory_out
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self._bench_started = time.perf_counter()
        self._bench_ticks = 0
        self._reset()

    def _reset(self):
        self.mode = self._args[0]
        self.session = Session(*self._args, days=self.days)
        self.inputs = LiveInputs(BUTTONS_V11)
        self.events = []
        self._saved = False
        self.error = None
        self.screen = "menu" if self.mode == "day" else "playing"
        self.intro_left = 0

    # --- luồng nền ----------------------------------------------------------------
    def start(self):
        self._thread = threading.Thread(target=self._loop, name="chonoi-sim", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _loop(self):
        nxt = time.perf_counter()
        while not self._stop.is_set():
            nxt += TICK_S
            self._bench_ticks += 1
            with self._lock:
                try:
                    self._tick_once()
                except Exception:  # luật của nhóm lỗi: báo ra terminal + client, dừng bước (restart để chơi lại)
                    self.error = traceback.format_exc()
                    sys.stderr.write(self.error)
                    self.session.sim.done = True
                    self.session.sim.reason = "error"
            delay = nxt - time.perf_counter()
            if delay > 0:
                self._stop.wait(delay)
            elif delay < -0.25:  # chạy chậm quá thì bỏ bù, tránh chạy dồn
                nxt = time.perf_counter()

    def _tick_once(self):
        s = self.session
        if s.done:
            return
        if self.screen in ("menu", "summary"):
            return
        inp = self.inputs.advance()
        old_phase = s.sim.phase
        old_day = getattr(s.sim, "day", None)
        presentation = self.screen != "playing"
        self.events.extend(s.step(inp, gameplay=not presentation))
        if presentation:
            if not s.paused and self.screen in ("dayintro", "eveningintro"):
                self.intro_left -= 1
                if self.intro_left <= 0 or inp.pressed("interact") or inp.pressed("catch") or any(inp.move):
                    self.screen = "playing"
            return
        if self.mode == "day":
            if s.done:
                self.screen = "summary"
            elif s.sim.day != old_day:
                self.screen, self.intro_left = "dayintro", 240
            elif s.sim.phase != old_phase:
                self.screen = "eveningintro" if s.sim.phase == "quan" else "dayresult"
                self.intro_left = 240
        del self.events[:-RECENT_EVENTS]
        if s.done and not self._saved:
            self._saved = True
            if self.inventory_out and self.mode == "gather":
                try:
                    s.write_inventory_if_done(self.inventory_out)
                except OSError as e:
                    sys.stderr.write(f"lỗi ghi kho: {e}\n")
            if self.auto_transition and self.mode == "gather":
                inventory = s.sim.inventory_items()
                self.mode = "quan"
                self.session = Session("quan", self.tuning, {}, self._seed, inventory)
                self.inputs = LiveInputs(BUTTONS_V11)
                self.events = []
                self._saved = False

    # --- API cho handler -----------------------------------------------------------
    def state_json(self) -> bytes:
        with self._lock:
            snap = self.session.snapshot()
            phase = self.session.sim.phase
            effective = getattr(self.session.sim, "effective_tuning", self.tuning)
            snap["meta"] = effective[phase]
            snap["screen"] = self.screen
            snap["menu"] = self.tuning["menu"]
            snap["intro_left_ticks"] = self.intro_left
            snap["events"] = list(self.events)
            snap["finished"] = self.session.done
            snap["reason"] = self.session.sim.reason if self.session.done else None
            snap["error"] = self.error
            snap["live_metrics"] = {
                "uptime_s": round(time.perf_counter() - self._bench_started, 3),
                "ticks": self._bench_ticks,
            }
            return json.dumps(snap, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    def set_input(self, body: dict):
        move = body.get("move")
        if move is not None:
            ok = (isinstance(move, list) and len(move) == 2 and
                  all(isinstance(c, (int, float)) and not isinstance(c, bool) and abs(c) <= 1 for c in move))
            if not ok:
                raise ValueError("move phải là [a, b] trong [-1, 1]")
        buttons = {}
        for b in BUTTONS_V11:
            if b in body:
                if not isinstance(body[b], bool):
                    raise ValueError(f"{b} phải là boolean")
                buttons[b] = body[b]
        buy = body.get("buy")
        if buy is not None and (not isinstance(buy, str) or not buy):
            raise ValueError("buy phải là chuỗi khác rỗng")
        with self._lock:
            self.inputs.set(move, buy=buy, **buttons)

    def restart(self):
        with self._lock:
            self._reset()

    def navigate(self, action):
        with self._lock:
            if action == "play":
                self._reset()
                self.screen = "dayintro" if self.mode == "day" else "playing"
                self.intro_left = 240
            elif action == "menu":
                self.screen = "menu"
                self.session.paused = False
                self.inputs = LiveInputs(BUTTONS_V11)
            elif action == "continue":
                if self.screen in ("dayintro", "eveningintro", "dayresult") and not self.session.paused:
                    # Keep button latches; an already-held key must not become an edge.
                    self.screen = "playing"
                elif self.session.paused:
                    self.inputs.set(pause=False)
                    self.inputs.set(pause=True)
                    self.inputs.set(pause=False)
            else:
                raise ValueError("điều hướng không hợp lệ")


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    game: LiveGame = None  # gán trên lớp con trong make_server

    def log_message(self, fmt, *args):  # yên lặng
        pass

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/state":
            self._send(200, self.game.state_json())
        elif path == "/metrics":
            state = json.loads(self.game.state_json().decode("utf-8"))
            self._send(200, json.dumps({"live_metrics": state["live_metrics"]},
                                       ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        elif path in ("/", "/index.html"):
            try:
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                self._send(404, b'{"error":"thieu index.html"}')
        else:
            self._send(404, b'{"error":"khong co"}')

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            self._send(400, b'{"error":"body sai"}')
            return
        raw = self.rfile.read(n) if n else b""
        try:
            if path == "/input":
                body = json.loads(raw.decode("utf-8") or "{}")
                if not isinstance(body, dict):
                    raise ValueError("body phải là object")
                self.game.set_input(body)
            elif path in ("/play", "/continue", "/menu"):
                self.game.navigate(path[1:])
            elif path == "/restart":
                self.game.restart()
            else:
                self._send(404, b'{"error":"khong co"}')
                return
        except (ValueError, UnicodeDecodeError) as e:
            self._send(400, json.dumps({"error": str(e)}).encode("utf-8"))
            return
        self._send(200, b'{"ok":true}')


class LiveServer:
    """Máy chủ + mô phỏng. port=0 -> cổng ngẫu nhiên (đọc `.port`)."""

    def __init__(self, game: LiveGame, host="127.0.0.1", port=8000):
        handler = type("Handler", (_Handler,), {"game": game})
        self.game = game
        self.httpd = ThreadingHTTPServer((host, port), handler)
        self.httpd.daemon_threads = True
        self.host = host
        self.port = self.httpd.server_address[1]
        self._thread = None

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/"

    def start(self):
        self.game.start()
        self._thread = threading.Thread(target=self.httpd.serve_forever, name="chonoi-http", daemon=True)
        self._thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        if self._thread:
            self._thread.join(timeout=2)
        self.game.stop()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.live", description="Chơi trực tiếp trên trình duyệt (starter).")
    p.add_argument("--mode", required=True, choices=["gather", "quan", "day"])
    p.add_argument("--days", type=int, default=None)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--port", type=int, default=8000, help="0 = cổng ngẫu nhiên")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--scenario")
    p.add_argument("--inventory", help="chỉ với quan: nạp kho từ file")
    p.add_argument("--inventory-out", dest="inventory_out", help="chỉ với gather: ghi kho khi kết thúc buổi")
    p.add_argument("--no-auto-transition", action="store_true",
                   help="giữ màn gather sau khi buổi sáng kết thúc")
    a = p.parse_args(argv)
    try:
        if a.days is not None and (a.mode != "day" or not 1 <= a.days <= 5):
            raise BadInput("--days chỉ với day, trong [1,5]")
        if a.inventory and a.mode != "quan":
            raise BadInput("--inventory chỉ dùng với quan")
        if a.inventory_out and a.mode != "gather":
            raise BadInput("--inventory-out chỉ dùng với gather")
        tuning = load_contract()["tuning"]
        scenario = load_scenario(a.scenario, a.mode, tuning)
        inventory = read_inventory(a.inventory) if a.inventory else None
        if inventory is not None and "stock" in scenario:
            raise BadInput("vừa có quan.stock vừa có --inventory")
        game = LiveGame(a.mode, tuning, scenario, a.seed, inventory, a.inventory_out,
                        auto_transition=not a.no_auto_transition, days=a.days or 5)
        server = LiveServer(game, a.host, a.port)
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"không mở được cổng {a.port}: {e}\n")
        return 1
    server.start()
    print(f"Mở trình duyệt tại {server.url}  (chế độ {a.mode}, seed {a.seed}). Ctrl+C để dừng.", flush=True)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
