#!/usr/bin/env python3
"""Bot tất định chạy soak test 10 Ngày (gather → quan → shop, D1–D5 lặp ở Ngày 6–10).

Xuất file soak.json với các trường:
  - days: số ngày mục tiêu (10)
  - days_completed: số ngày hoàn thành thực tế
  - crashes: số lần crash (0 nếu ổn định)
  - results: mảng kết quả từng ngày
  - duration_s: tổng thời gian chạy (giây)
"""

import argparse
from copy import deepcopy
import json
import math
import os
import sys
import time

# Đảm bảo import được module chonoi
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.day import DaySim


def move_towards(curr, target):
    """Tính vector hướng chuẩn hóa và khoảng cách Euclid tới mục tiêu."""
    dx = target[0] - curr[0]
    dz = target[1] - curr[1]
    dist = math.hypot(dx, dz)
    if dist < 0.05:
        return (0.0, 0.0), dist
    return (dx / dist, dz / dist), dist


def run_soak(days=10, seed=42, contract_path=None):
    if contract_path is None:
        contract_path = os.path.join(ROOT_DIR, "game.contract.json")
    with open(contract_path, encoding="utf-8") as f:
        contract = json.load(f)
    tuning = contract["tuning"]

    # Kế hoạch 10 ngày: D1-D5 lặp ở Ngày 6-10
    base_plans = tuning["day_plan"]
    day_plan = [
        dict(deepcopy(base_plans[(i - 1) % len(base_plans)]), day=i)
        for i in range(1, days + 1)
    ]
    scenario = {"day": {"day_plan": day_plan}}

    streams = Streams(seed)
    ids = IdAllocator()
    sim = DaySim(tuning, scenario, streams, ids, days=days)

    results = []
    crashes = 0
    t0 = time.time()

    # Thống kê từng ngày từ sự kiện
    curr_day_stats = {
        "served": 0,
        "left": 0,
        "money_earned": 0,
        "tips": 0,
    }

    try:
        while not sim.done and crashes == 0:
            phase = sim.phase
            inp = InputState((0.0, 0.0), set(), set())

            if phase == "gather":
                g = sim.active
                # Chiến thuật lặn: hái rau gần nhất N1 [12, 0] hoặc N3 [44, 0]
                if len(g.hold) < 6 and g.time_left_ticks > 600:
                    target_node = g.nodes[0]["pos"] if g.nodes[0]["regrow_ticks"] == 0 else g.nodes[2]["pos"]
                    mv, d = move_towards(g.pos, target_node)
                    if d <= 1.8:
                        inp = InputState((0.0, 0.0), set(), {"interact"})
                    else:
                        inp = InputState(mv, set(), set())
                else:
                    # Quay về bến cập bến
                    mv, d = move_towards(g.pos, tuning["gather"]["dock_pos"])
                    if d <= 2.5:
                        inp = InputState((0.0, 0.0), set(), {"interact"})
                    else:
                        inp = InputState(mv, set(), set())

            elif phase == "quan":
                q = sim.active
                # Chiến thuật quán: phục vụ món ăn
                if q.hand is not None:
                    order_id = q.hand["order_id"]
                    cust = next((c for c in q.customers if c["id"] == order_id), None)
                    if cust:
                        tb = next(tb for tb in q.tables if tb["id"] == cust["table_id"])
                        mv, d = move_towards(q.pos, tb["pos"])
                        if d <= 1.2:
                            inp = InputState((0.0, 0.0), set(), {"interact"})
                        else:
                            inp = InputState(mv, set(), set())
                else:
                    ready_stove = next((s for s in q.stoves if s["state"] == "ready"), None)
                    if ready_stove:
                        mv, d = move_towards(q.pos, ready_stove["pos"])
                        if d <= 1.2:
                            inp = InputState((0.0, 0.0), set(), {"interact"})
                        else:
                            inp = InputState(mv, set(), set())
                    else:
                        done_cust = next((c for c in q.customers if c["state"] == "done"), None)
                        if done_cust:
                            tb = next(tb for tb in q.tables if tb["id"] == done_cust["table_id"])
                            mv, d = move_towards(q.pos, tb["pos"])
                            if d <= 1.2:
                                inp = InputState((0.0, 0.0), set(), {"interact"})
                            else:
                                inp = InputState(mv, set(), set())
                        else:
                            idle_stove = next((s for s in q.stoves if s["state"] == "idle"), None)
                            wait_cust = next((c for c in q.customers if c["state"] == "waiting" and c["order_status"] == "reserved"), None)
                            if idle_stove and wait_cust:
                                mv, d = move_towards(q.pos, idle_stove["pos"])
                                if d <= 1.2:
                                    inp = InputState((0.0, 0.0), set(), {"interact"})
                                else:
                                    inp = InputState(mv, set(), set())

            elif phase == "shop":
                # Nâng cấp oxy / máu nếu đủ tiền
                buy = None
                if sim.upgrades.get("oxygen", 0) == 0 and sim.money >= 200:
                    buy = "oxygen"
                elif sim.upgrades.get("hp", 0) == 0 and sim.money >= 250:
                    buy = "hp"
                inp = InputState((0.0, 0.0), set(), {"shop_done"}, buy=buy)

            evs = sim.step(inp)
            for e in evs:
                name = e.get("name")
                if name == "served":
                    curr_day_stats["served"] += 1
                elif name == "customer_left":
                    curr_day_stats["left"] += 1
                elif name == "paid":
                    data = e.get("data", {})
                    curr_day_stats["money_earned"] += data.get("amount", 0)
                    curr_day_stats["tips"] += data.get("tip", 0)
                elif name == "shop_end":
                    day_idx = e.get("day", len(results) + 1)
                    results.append({
                        "day": day_idx,
                        "served": curr_day_stats["served"],
                        "left": curr_day_stats["left"],
                        "money": sim.money,
                        "tips": curr_day_stats["tips"],
                        "reputation": round(sim.reputation, 2),
                        "upgrades": dict(sim.upgrades),
                        "sales": dict(sim.sales),
                    })
                    curr_day_stats = {
                        "served": 0,
                        "left": 0,
                        "money_earned": 0,
                        "tips": 0,
                    }

    except Exception as ex:
        crashes += 1
        print(f"[SOAK ERROR] Crash at day {sim.day}, phase {sim.phase}: {ex}", file=sys.stderr)

    duration_s = round(time.time() - t0, 3)
    return {
        "days": days,
        "days_completed": sim.days_completed,
        "crashes": crashes,
        "results": results,
        "duration_s": duration_s,
    }


def main():
    parser = argparse.ArgumentParser(description="Chạy soak test tất định 10 ngày")
    parser.add_argument("--days", type=int, default=10, help="Số ngày mô phỏng (mặc định 10)")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên (mặc định 42)")
    parser.add_argument("--out", type=str, default="soak.json", help="File kết quả JSON (mặc định soak.json)")
    args = parser.parse_args()

    data = run_soak(days=args.days, seed=args.seed)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Soak completed: {data['days_completed']}/{data['days']} days in {data['duration_s']}s (crashes: {data['crashes']})")
    if data["crashes"] > 0 or data["days_completed"] < data["days"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
