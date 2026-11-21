"""Benchmark tốc độ đọc cảnh lặn qua HTTP /state, không đo render trình duyệt.

Mỗi phản hồi hoàn tất được tính là một khung; FPS gồm chi phí HTTP và đọc
trạng thái trong khi mô phỏng live chạy. Không mở trình duyệt hay cửa sổ:
1280×720 là cấu hình chuẩn, không phải độ phân giải render được đo.
Mặc định seed 42, Út Sen ở bến, làm nóng 3 s rồi đo 30 s.
load_ms tính từ khởi chạy script tới phản hồi cảnh đầu tiên (kể cả làm nóng),
không phải thời gian tải trang/asset hay thời gian của một request trung bình.
"""

import time

LAUNCH_STARTED = time.perf_counter()

import argparse
import json
import math
import os
import sys
import tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def percentile_low(frame_times, percentile=0.01):
    """Nghịch đảo thời gian trung bình của ceil(1% số khung) chậm nhất."""
    if not frame_times:
        return 0.0
    count = max(1, math.ceil(len(frame_times) * percentile))
    slowest = sorted(frame_times, reverse=True)[:count]
    return len(slowest) / sum(slowest)


def run_bench(seed=42, warmup_s=3.0, measure_s=30.0, width=1280, height=720,
              launch_started=None):
    if launch_started is None:
        launch_started = time.perf_counter()
    tuning = load_contract()["tuning"]
    dock = tuning["gather"]["dock_pos"]
    scenario = {
        "player": {"pos": list(dock)},
        "random_fish": False,
        "fish": [],
        "monsters": [],
    }
    game = LiveGame("gather", tuning, scenario, seed, auto_transition=False)
    server = LiveServer(game, host="127.0.0.1", port=0)
    server.start()
    try:
        url = server.url + "state"
        first_frame = None
        warmup_end = time.perf_counter() + max(0.0, warmup_s)
        while time.perf_counter() < warmup_end:
            with urllib.request.urlopen(url, timeout=2) as response:
                response.read()
            if first_frame is None:
                first_frame = time.perf_counter()

        frame_times = []
        start = time.perf_counter()
        previous_frame = start
        deadline = start + max(0.001, measure_s)
        while not frame_times or time.perf_counter() < deadline:
            with urllib.request.urlopen(url, timeout=2) as response:
                response.read()
            completed = time.perf_counter()
            if first_frame is None:
                first_frame = completed
            frame_times.append(completed - previous_frame)
            previous_frame = completed
        measured = previous_frame - start
        frames = len(frame_times)

        avg_fps = frames / measured if measured > 0 else 0.0
        load_ms = (first_frame - launch_started) * 1000.0
        return {
            "avg_fps": avg_fps,
            "p1_low_fps": percentile_low(frame_times),
            "frames": frames,
            "measured_s": measured,
            "load_ms": load_ms,
        }
    finally:
        server.stop()


def write_json(path, data):
    path = os.path.abspath(path)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".bench-", suffix=".tmp", dir=directory or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="Benchmark cổng live /state.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--warmup-s", type=float, default=3.0)
    parser.add_argument("--duration", "--measure-s", dest="duration", type=float,
                        default=30.0, help="số giây đo (mặc định 30)")
    parser.add_argument("--out", default="bench.json")
    args = parser.parse_args(argv)
    if args.width != 1280 or args.height != 720:
        parser.error("--width/--height chỉ hỗ trợ 1280x720 cho benchmark chuẩn")
    if (args.seed < 0 or not math.isfinite(args.warmup_s) or args.warmup_s < 0
            or not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("tham số benchmark ngoài miền")
    result = run_bench(args.seed, args.warmup_s, args.duration, args.width, args.height,
                       launch_started=LAUNCH_STARTED)
    write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
