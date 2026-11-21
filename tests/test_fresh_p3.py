"""AC-P3-xx: hộp đen v1.2, chỉ CLI headless và JSONL/file công khai.

Không import sim/fresh/runner, không skip khi các lát A–D chưa tích hợp.
Mã AC bên dưới là ánh xạ QA cục bộ cho PRD docs/prd/phase-3.md.
"""

import json
import math
import os
import shlex
import subprocess
import sys
import unittest
from fractions import Fraction

from helpers import ROOT, Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
    CONTRACT = json.load(f)
T = CONTRACT["tuning"]
G, Q, MENU, HZ = T["gather"], T["quan"], T["menu"], T["tick_hz"]
SINGLE = next(d for d in sorted(MENU) if sum(MENU[d]["recipe"].values()) == 1)
KIND = next(iter(MENU[SINGLE]["recipe"]))
STOVE, TABLE = Q["stoves"][0], Q["tables"][0]
PRESS = [{"tick": 0, "interact": True}]


def item(ident="I1", kind=KIND, fresh=100):
    # Giá trị fixture; initial/threshold/decay kỳ vọng luôn lấy từ contract.
    return {"id": ident, "kind": kind, "fresh": fresh}


def gather(**kw):
    return dict({"random_fish": False, "fish": [], "nodes": [], "monsters": []}, **kw)


def quan(**kw):
    return dict({"random_customers": False, "customers": []}, **kw)


def customer(**kw):
    return dict({"id": "C1", "table_id": TABLE["id"], "dish_id": SINGLE,
                 "order_tick": 0, "state": "waiting", "order_status": "reserved"}, **kw)


class FreshP3(unittest.TestCase):
    def freshness(self):
        self.assertTrue("freshness" in T, "Chờ lát A: tuning.freshness của contract v1.2")
        return T["freshness"]

    def run_scene(self, mode, scene, ticks=1, inputs=None, days=None):
        with Workdir() as w:
            args = ["--mode", mode, "--seed", "1", "--ticks", str(ticks),
                    "--snapshot-every", "1", "--out", w.path("out.jsonl"),
                    "--scenario", write_json(w.path("scenario.json"), scene)]
            if inputs is not None:
                args += ["--inputs", write_json(w.path("inputs.json"), frames(*inputs))]
            if days is not None:
                args += ["--days", str(days)]
            code, err = run_headless(*args)
            self.assertEqual(code, 0, err)
            return read_jsonl(w.path("out.jsonl"))

    def inventory_code(self, inventory, expected):
        with Workdir() as w:
            out = w.path("out.jsonl")
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0",
                                     "--out", out, "--inventory",
                                     write_json(w.path("inventory.json"), inventory))
            self.assertEqual(code, expected, err)
            if expected == 2:
                self.assertFalse(os.path.exists(out), "Input sai phải bị chặn trước ghi JSONL")
                return []
            return read_jsonl(out)

    def assert_items(self, actual, expected):
        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), len(expected))
        for got, want in zip(actual, expected):
            self.assertEqual(set(got), {"id", "kind", "fresh"})
            self.assertEqual((got["id"], got["kind"]), (want["id"], want["kind"]))
            self.assertAlmostEqual(got["fresh"], want["fresh"], delta=0.01)

    def test_ac_p3_01_contract_v12(self):
        # P4 [THAY THẾ]: contract 1.3, gameplay/kho/JSONL giữ v1.2
        self.assertEqual(CONTRACT["contract_version"], "1.3")
        self.freshness()

    def test_ac_p3_02_prd_threshold_fixture_spoiled_tick_one_exact_data(self):
        threshold = self.freshness()["spoiled_below"]
        rows = self.run_scene("gather", {"gather": gather(hold=[item(kind="ca_linh", fresh=threshold)])})
        self.assertEqual(events(rows, "spoiled"), [{"type": "event", "tick": 1, "phase": "gather",
                         "name": "spoiled", "data": {"item_id": "I1", "kind": "ca_linh", "location": "hold"}}])

    def test_ac_p3_03_gather_file_quan_smoke_preserves_id_kind_fresh(self):
        fresh = self.freshness()["initial"]
        with Workdir() as w:
            inv = w.path("inventory.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "1",
                "--out", w.path("g.jsonl"), "--inventory-out", inv, "--scenario",
                write_json(w.path("sc.json"), {"gather": gather(hold=[item("I10", fresh=fresh), item("I2", fresh=fresh)])}),
                "--inputs", write_json(w.path("in.json"), frames(*PRESS)))
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(set(saved), {"items"})
            expected = [item(i, fresh=fresh - self.freshness()["gather_decay_per_s"] / HZ) for i in ("I2", "I10")]
            self.assert_items(saved["items"], expected)
            self.assertEqual(events(read_jsonl(w.path("g.jsonl")), "gather_end")[0]["data"]["inventory"], saved)
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0",
                                     "--inventory", inv, "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assert_items(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], saved["items"])

    def test_ac_p3_04_v11_count_inventory_rejected_code_two(self):
        self.inventory_code({"items": {KIND: 1}}, 2)

    def test_ac_p3_05_wrong_schema_rejected_code_two(self):
        for bad in ({}, [], {"items": None}, {"items": [], "extra": 1},
                    {"items": [KIND]}, {"items": [{"id": "I1", "kind": KIND}]},
                    {"items": [dict(item(), extra=1)]}, {"items": [item("")]},
                    {"items": [item(1)]}, {"items": [item(fresh=True)]}):
            with self.subTest(inventory=bad):
                self.inventory_code(bad, 2)

    def test_ac_p3_06_unknown_kind_rejected_code_two(self):
        self.inventory_code({"items": [item(kind="unknown_ingredient")]}, 2)

    def test_ac_p3_07_duplicate_id_rejected_code_two(self):
        self.inventory_code({"items": [item(), item()]}, 2)

    def test_ac_p3_08_out_of_range_or_nonfinite_fresh_rejected_code_two(self):
        for fresh in (-0.01, 100.01, float("nan"), float("inf"), -float("inf")):
            with self.subTest(fresh=fresh):
                self.inventory_code({"items": [item(fresh=fresh)]}, 2)

    def test_ac_p3_09_empty_inventory_valid(self):
        rows = self.inventory_code({"items": []}, 0)
        self.assertEqual(snapshots(rows)[0]["stock"], [])

    def test_ac_p3_10_gather_decay_per_second(self):
        f = self.freshness()
        rows = self.run_scene("gather", {"gather": gather(hold=[item(fresh=f["initial"])])}, ticks=HZ)
        self.assert_items(snapshots(rows)[-1]["hold"], [item(fresh=f["initial"] - f["gather_decay_per_s"])])

    def test_ac_p3_11_quan_decay_including_reserved_stock(self):
        f = self.freshness()
        rows = self.run_scene("quan", {"quan": quan(stock=[item(fresh=f["initial"])],
                              customers=[customer(reserved=["I1"])])}, ticks=HZ)
        self.assert_items(snapshots(rows)[-1]["stock"], [item(fresh=f["initial"] - f["quan_decay_per_s"])])
        self.assertEqual(snapshots(rows)[-1]["customers"][0]["reserved"], ["I1"])

    def test_ac_p3_12_spoiled_once_in_id_order_in_each_phase(self):
        threshold = self.freshness()["spoiled_below"]
        for mode, field, location in (("gather", "hold", "hold"), ("quan", "stock", "stock")):
            with self.subTest(mode=mode):
                stock = [item("I10", fresh=threshold), item("I2", fresh=threshold), item("I1", fresh=0)]
                scene = (gather if mode == "gather" else quan)(**{field: stock})
                rows = self.run_scene(mode, {mode: scene}, ticks=HZ)
                self.assertEqual([(e["tick"], e["data"]) for e in events(rows, "spoiled")],
                    [(1, {"item_id": i, "kind": KIND, "location": location}) for i in ("I2", "I10")])
                final = snapshots(rows)[-1][field]
                self.assertEqual(next(it["fresh"] for it in final if it["id"] == "I1"), 0)

    def test_ac_p3_13_threshold_uses_unrounded_value(self):
        f = self.freshness()
        for mode, field in (("gather", "hold"), ("quan", "stock")):
            with self.subTest(mode=mode):
                start = f["spoiled_below"] + f[mode + "_decay_per_s"] / HZ
                scene = (gather if mode == "gather" else quan)(**{field: [item(fresh=start)]})
                rows = self.run_scene(mode, {mode: scene}, ticks=3)
                self.assertEqual([e["tick"] for e in events(rows, "spoiled")], [2])

    def test_ac_p3_14_reserved_ids_freshest_then_numeric_id(self):
        stock = [item("I1", fresh=70), item("I10", fresh=90), item("I2", fresh=90)]
        rows = self.run_scene("quan", {"quan": quan(stock=stock, customers=[customer()])}, ticks=0)
        self.assertEqual(snapshots(rows)[0]["customers"][0]["reserved"], ["I2"])

    def test_ac_p3_15_explicit_reserved_id_is_consumed_even_if_fresher_exists(self):
        rows = self.run_scene("quan", {"quan": quan(stock=[item("I1", fresh=60), item("I2", fresh=90)],
            customers=[customer(reserved=["I1"])], player={"pos": STOVE["pos"]})}, inputs=PRESS)
        used = events(rows, "cook_started")
        self.assertEqual(len(used), 1)
        self.assertEqual([it["id"] for it in used[0]["data"]["items"]], ["I1"])
        self.assertEqual([it["id"] for it in snapshots(rows)[-1]["stock"]], ["I2"])

    def test_ac_p3_16_spoiled_reservation_released_and_replaced_before_cook(self):
        f = self.freshness()
        rows = self.run_scene("quan", {"quan": quan(stock=[item("I1", fresh=f["spoiled_below"]), item("I2", fresh=90)],
            customers=[customer(reserved=["I1"])], player={"pos": STOVE["pos"]})}, inputs=PRESS)
        es = events(rows)
        self.assertEqual([e["name"] for e in es], ["spoiled", "cook_started"])
        self.assertEqual([it["id"] for it in es[1]["data"]["items"]], ["I2"])

    def test_ac_p3_17_spoiled_reservation_insufficient_unfulfillable_stays_waiting(self):
        rows = self.run_scene("quan", {"quan": quan(stock=[item(fresh=self.freshness()["spoiled_below"])],
            customers=[customer(reserved=["I1"])], player={"pos": STOVE["pos"]})}, inputs=PRESS, ticks=2)
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["reserved"], c["order_status"], c["state"]), ([], "unfulfillable", "waiting"))
        self.assertEqual(events(rows, "cook_started"), [])
        self.assertEqual(events(rows, "customer_left"), [])

    def test_ac_p3_18_cook_items_kind_then_numeric_id_and_mean_fresh_price(self):
        f = self.freshness()
        dish = max(sorted(MENU), key=lambda d: sum(MENU[d]["recipe"].values()))
        stock = []
        for kind, count in sorted(MENU[dish]["recipe"].items()):
            for _ in range(count):
                stock.append(item("I" + str(2 + 8 * len(stock)), kind, 60 + len(stock)))
        rows = self.run_scene("quan", {"quan": quan(stock=list(reversed(stock)),
            customers=[customer(dish_id=dish, reserved=[it["id"] for it in stock])],
            player={"pos": STOVE["pos"]})}, inputs=PRESS)
        es = events(rows, "cook_started")
        self.assertEqual(len(es), 1)
        data = es[0]["data"]
        expected = [dict(it, fresh=it["fresh"] - f["quan_decay_per_s"] / HZ) for it in stock]
        self.assert_items(data["items"], expected)
        mean = sum(Fraction(str(it["fresh"])) for it in stock) / len(stock)
        mean -= Fraction(str(f["quan_decay_per_s"])) / HZ
        self.assertEqual(data["base_price"], math.floor(MENU[dish]["price"] * mean / 100))
        self.assertEqual(snapshots(rows)[-1]["stock"], [])

    def test_ac_p3_19_tip_on_locked_price_through_cook_pick_serve_pay(self):
        f = self.freshness()
        cook = round(MENU[SINGLE]["cook_s"] * HZ)
        travel = math.ceil(2 * Q["interact_radius"] / Q["walk_speed"] * HZ) + Q["ramp_max_ticks"]
        serve_frame = cook + 1 + travel
        table_pos = [STOVE["pos"][0], STOVE["pos"][1] - 2 * Q["interact_radius"]]
        inputs = [*PRESS, {"tick": 1, "interact": False}, {"tick": cook, "interact": True},
                  {"tick": cook + 1, "interact": False, "move": [0, -1]},
                  {"tick": serve_frame, "move": [0, 0], "interact": True}]
        rows = self.run_scene("quan", {"quan": quan(stock=[item(fresh=75)], customers=[customer()],
            player={"pos": STOVE["pos"]}, tables=[{"id": TABLE["id"], "pos": table_pos}])},
            ticks=serve_frame + 1 + round(Q["eat_s"] * HZ), inputs=inputs)
        base = math.floor(MENU[SINGLE]["price"] * (Fraction(75) - Fraction(str(f["quan_decay_per_s"])) / HZ) / 100)
        tip = math.floor(base * Fraction(str(Q["tip_rate"])))
        for name in ("cook_started", "dish_picked", "served", "paid"):
            self.assertEqual(len(events(rows, name)), 1, name)
        for name in ("cook_started", "served", "paid"):
            self.assertEqual(events(rows, name)[0]["data"]["base_price"], base)
        self.assertEqual(events(rows, "served")[0]["data"]["tip"], tip)
        self.assertEqual(events(rows, "paid")[0]["data"]["amount"], base + tip)

    def test_ac_p3_20_day_handoff_same_tick_no_extra_decay_and_ids_increase(self):
        f = self.freshness()
        scene = {"gather": gather(time_left_ticks=1, hold=[item("I10", fresh=f["initial"])]),
                 "quan": quan(time_left_ticks=1)}
        rows = self.run_scene("day", scene, ticks=5, days=2, inputs=[{"tick": 2, "shop_done": True}])
        ss = {s["tick"]: s for s in snapshots(rows)}
        self.assertEqual((ss[0]["day"], ss[0]["hold"][0]["id"]), (1, "I10"))
        self.assertEqual((ss[1]["phase"], ss[1]["phase_tick"]), ("quan", 0))
        end = events(rows, "gather_end")
        self.assertEqual(len(end), 2)
        for tick, event in ((1, end[0]), (4, end[1])):
            self.assertEqual(event["tick"], tick)
            self.assertEqual(ss[tick]["stock"], event["data"]["inventory"]["items"], "Cùng tick phải bàn giao nguyên độ tươi")
            self.assertAlmostEqual(ss[tick]["stock"][0]["fresh"], f["initial"] - f["gather_decay_per_s"] / HZ, delta=0.01)
        self.assertEqual((ss[3]["phase"], ss[3]["day"], ss[3]["hold"][0]["id"]), ("gather", 2, "I11"))
        self.assert_items(ss[3]["hold"], [item("I11", fresh=f["initial"])])
        self.assertAlmostEqual(ss[2]["stock"][0]["fresh"],
            ss[1]["stock"][0]["fresh"] - f["quan_decay_per_s"] / HZ, delta=0.01)

    def test_ac_p3_21_pause_stops_freshness_resume_decays_once(self):
        f = self.freshness()
        for mode, field in (("gather", "hold"), ("quan", "stock")):
            with self.subTest(mode=mode):
                scene = (gather if mode == "gather" else quan)(**{field: [item(fresh=f["initial"])]})
                rows = self.run_scene(mode, {mode: scene}, ticks=HZ + 1,
                    inputs=[{"tick": 0, "pause": True}, {"tick": 1, "pause": False}, {"tick": HZ, "pause": True}])
                ss = snapshots(rows)
                self.assert_items(ss[-2][field], [item(fresh=f["initial"])])
                self.assertEqual(ss[-2]["sim_tick"], 0)
                self.assertEqual(ss[-1]["sim_tick"], 1)
                self.assert_items(ss[-1][field], [item(fresh=f["initial"] - f[mode + "_decay_per_s"] / HZ)])
                self.assertAlmostEqual(ss[-1][field][0]["fresh"],
                    f["initial"] - f[mode + "_decay_per_s"] / HZ, delta=0.000001)

    def test_ac_p3_22_replacing_reservation_releases_entire_recipe(self):
        f = self.freshness()
        dish = next(d for d in sorted(MENU) if len(MENU[d]["recipe"]) == 1 and sum(MENU[d]["recipe"].values()) == 2)
        kind = next(iter(MENU[dish]["recipe"]))
        stock = [item("I1", kind, f["spoiled_below"]), item("I2", kind, 90),
                 item("I3", kind, 95), item("I4", kind, 80)]
        rows = self.run_scene("quan", {"quan": quan(stock=stock,
            customers=[customer(dish_id=dish, reserved=["I1", "I2"])])}, ticks=2)
        c = snapshots(rows)[-1]["customers"][0]
        self.assertIsInstance(c["reserved"], list)
        self.assertEqual(set(c["reserved"]), {"I2", "I3"})
        self.assertEqual(c["order_status"], "reserved")

    def test_ac_p3_23_affected_orders_reallocate_in_table_id_order(self):
        f = self.freshness()
        tables = Q["tables"][:2]
        cs = [customer(id="C2", table_id=tables[0]["id"], reserved=["I1"]),
              customer(id="C1", table_id=tables[1]["id"], reserved=["I2"])]
        stock = [item("I1", fresh=f["spoiled_below"]), item("I2", fresh=f["spoiled_below"]), item("I20", fresh=90)]
        rows = self.run_scene("quan", {"quan": quan(stock=stock, customers=list(reversed(cs)))})
        by_id = {c["id"]: c for c in snapshots(rows)[-1]["customers"]}
        self.assertEqual(by_id["C2"]["reserved"], ["I20"])
        self.assertEqual((by_id["C1"]["reserved"], by_id["C1"]["order_status"]), ([], "unfulfillable"))

    def test_ac_p3_24_conflicting_or_spoiled_reserved_ids_rejected_code_two(self):
        cases = [([item()], [customer(reserved=reserved)])
                 for reserved in (["missing"], ["I1", "I1"], {KIND: 1})]
        # Fresh 0 chắc chắn ươn theo miền contract; không dùng fixture float sát ngưỡng ở kiểm schema.
        cases.append(([item(fresh=0)], [customer(reserved=["I1"])]))
        cases.append(([item()], [customer(reserved=["I1"]),
            customer(id="C2", table_id=Q["tables"][1]["id"], reserved=["I1"])]))
        for stock, cs in cases:
            with self.subTest(stock=stock, customers=cs), Workdir() as w:
                code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--out", w.path("o.jsonl"),
                    "--scenario", write_json(w.path("s.json"), {"quan": quan(stock=stock, customers=cs)}))
                self.assertEqual(code, 2, err)
                self.assertFalse(os.path.exists(w.path("o.jsonl")))


class SoakP4(unittest.TestCase):
    def test_soak_cli_two_days_results_and_determinism(self):
        cmd = shlex.split(CONTRACT["soak_cmd"])
        if sys.platform == "win32" and cmd and cmd[0] == "python3":
            cmd[0] = sys.executable
        runs = []
        with Workdir() as w:
            for run in range(2):
                out = w.path("soak-{}.json".format(run))
                proc = subprocess.run(
                    [*cmd, "--seed", "7", "--days", "2", "--out", out],
                    cwd=ROOT, capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                with open(out, encoding="utf-8") as f:
                    data = json.load(f)
                self.assertTrue({"days", "days_completed", "crashes", "results", "duration_s"} <= data.keys())
                self.assertEqual(data["days"], 2)
                self.assertEqual(data["days_completed"], data["days"])
                self.assertEqual(data["crashes"], 0)
                self.assertGreaterEqual(data["duration_s"], 0)
                self.assertEqual(len(data["results"]), data["days"])
                for day, result in enumerate(data["results"], 1):
                    self.assertTrue({"day", "earned", "reputation", "score"} <= result.keys())
                    self.assertEqual(result["day"], day)
                    self.assertEqual(result["score"], result["earned"] + 100 * math.floor(result["reputation"]))
                runs.append(data["results"])
        self.assertEqual(runs[0], runs[1])


if __name__ == "__main__":
    unittest.main()
