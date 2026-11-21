"""Benchmark đầu ra UI live bằng máy chủ /state.

Làm nóng, đo 30 giây tại seed 42 và vị trí Út Sen ở bến.
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def percentile_low(values, percentile=0.01):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * percentile)))
    return float(ordered[index])


def run_bench(seed=42, warmup_s=3.0, measure_s=30.0, width=1280, height=720):
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
        warmup_end = time.perf_counter() + max(0.0, warmup_s)
        while time.perf_counter() < warmup_end:
            with urllib.request.urlopen(url, timeout=2) as response:
                response.read()

        counts = {}
        loads = []
        frames = 0
        start = time.perf_counter()
        deadline = start + max(0.001, measure_s)
        while time.perf_counter() < deadline:
            poll_start = time.perf_counter()
            with urllib.request.urlopen(url, timeout=2) as response:
                response.read()
            elapsed_load = (time.perf_counter() - poll_start) * 1000.0
            loads.append(elapsed_load)
            frames += 1
            second = int(time.perf_counter() - start)
            counts[second] = counts.get(second, 0) + 1
        measured = time.perf_counter() - start

        complete_seconds = int(measured)
        per_second = [counts.get(second, 0) for second in range(complete_seconds)]
        avg_fps = frames / measured if measured > 0 else 0.0
        load_ms = sum(loads) / len(loads) if loads else 0.0
        return {
            "avg_fps": round(avg_fps, 2),
            "p1_low_fps": round(percentile_low(per_second), 2),
            "frames": frames,
            "measured_s": round(measured, 3),
            "load_ms": round(load_ms, 3),
            "resolution": [int(width), int(height)],
            "seed": int(seed),
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
    parser.add_argument("--measure-s", type=float, default=30.0)
    parser.add_argument("--out", default="bench.json")
    args = parser.parse_args(argv)
    if args.width != 1280 or args.height != 720:
        parser.error("--width/--height chỉ hỗ trợ 1280x720 cho benchmark chuẩn")
    if args.seed < 0 or args.warmup_s < 0 or args.measure_s <= 0:
        parser.error("tham số benchmark ngoài miền")
    result = run_bench(args.seed, args.warmup_s, args.measure_s, args.width, args.height)
    write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
