"""Đọc game.contract.json và kiểm dải hợp lệ của tuning P1 (PRD mục 13.2, Test Contract)."""

import json
import math
import os

from .errors import BadInput

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and (isinstance(v, int) or math.isfinite(v))


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    if not isinstance(c, dict) or c.get("contract_version") not in ("1.2", "1.3"):
        raise BadInput("contract_version phải là 1.2 hoặc 1.3")
    validate_tuning(c.get("tuning"))
    return c


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if (not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos)):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_gather(g):
    """Dải hợp lệ P1 theo PRD mục 13.2."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    if not isinstance(fy, dict) or not {"ca_linh", "ca_loc"} <= set(fy):
        raise BadInput("tuning.gather.fish_yield phải có ca_linh và ca_loc")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BadInput("tuning.gather.nodes phải là mảng không rỗng")
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if n.get("kind") not in ("bong_dien_dien", "bong_sung", "keo_neo"):
            raise BadInput(f"tuning.gather.nodes.{n['id']}: kind phải là bong_dien_dien, bong_sung hoặc keo_neo")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if not {"bong_dien_dien", "bong_sung"} <= kinds:
        raise BadInput("tuning.gather.nodes phải có ít nhất một nút mỗi loại (bong_dien_dien, bong_sung)")
    fish = g.get("fish_initial")
    if isinstance(fish, int):
        _int_between("gather.fish_initial", fish, 1, 30)
    elif isinstance(fish, list):
        seen = set()
        for f in fish:
            if not isinstance(f, dict) or not isinstance(f.get("id"), str) or f["id"] in seen:
                raise BadInput("tuning.gather.fish_initial: mỗi đàn cần id duy nhất")
            seen.add(f["id"])
            if f.get("kind") not in fy:
                raise BadInput(f"tuning.gather.fish_initial.{f['id']}: kind phải thuộc fish_yield")
            _pos_in(f"gather.fish_initial.{f['id']}.pos", f.get("pos"), b, ("x", "d"))
            if f["pos"][1] <= g["surface_depth"]:
                raise BadInput(f"tuning.gather.fish_initial.{f['id']}: đàn cá phải ở dưới nước")
    else:
        raise BadInput("tuning.gather.fish_initial phải là số nguyên hoặc danh sách đàn cá")


def validate_tuning(t):
    if not isinstance(t, dict):
        raise BadInput("tuning phải là object")
    _int_between("tick_hz", t.get("tick_hz"), 60, 60)
    freshness = t.get("freshness")
    if not isinstance(freshness, dict) or set(freshness) != {"initial", "gather_decay_per_s", "quan_decay_per_s", "spoiled_below"}:
        raise BadInput("tuning.freshness cần đúng initial, gather_decay_per_s, quan_decay_per_s, spoiled_below")
    for key in ("initial", "spoiled_below"):
        _between(f"freshness.{key}", freshness[key], 0, 100)
    for key in ("gather_decay_per_s", "quan_decay_per_s"):
        if not _num(freshness[key]) or freshness[key] < 0:
            raise BadInput(f"freshness.{key} phải là số hữu hạn không âm")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    _validate_gather(g)
    _validate_phase2(t)
    # Quán: dải hợp lệ P1 (PRD mục 13.2)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null ở Phase 1")
    # TODO(nhóm): bổ sung kiểm các khóa còn lại nếu muốn chặt hơn (bếp/bàn, uy tín, ...).
    for dish_id, d in menu.items():
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
    if "day_plan" in t:
        _validate_day_plan(t["day_plan"], menu)


def _validate_day_plan(plan, menu):
    """v1.1: mảng 5 ngày {day, dishes, ingredients}; ingredients = tổng công thức × số suất."""
    if not isinstance(plan, list) or [p.get("day") if isinstance(p, dict) else None for p in plan] != [1, 2, 3, 4, 5]:
        raise BadInput("tuning.day_plan phải là mảng 5 object, day lần lượt 1..5")
    for p in plan:
        name = f"day_plan.D{p['day']}"
        if set(p) != {"day", "dishes", "ingredients"}:
            raise BadInput(f"tuning.{name} chỉ có day, dishes, ingredients")
        need = {}
        for key in ("dishes", "ingredients"):
            m = p[key]
            if not isinstance(m, dict) or not m:
                raise BadInput(f"tuning.{name}.{key} phải là map id -> số nguyên dương")
            for k, n in m.items():
                if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
                    raise BadInput(f"tuning.{name}.{key}.{k} phải là số nguyên dương")
        for dish_id, n in p["dishes"].items():
            if dish_id not in menu:
                raise BadInput(f"tuning.{name}: món {dish_id} không có trong menu")
            for k, c in menu[dish_id]["recipe"].items():
                need[k] = need.get(k, 0) + c * n
        if need != p["ingredients"]:
            raise BadInput(f"tuning.{name}.ingredients phải bằng tổng công thức × số suất: {need}")


def _validate_phase2(t):
    """Reject malformed shared data before constructing or writing a simulation."""
    shop = t.get("shop")
    if not isinstance(shop, dict) or not {"max_ticks", "upgrades"} <= set(shop) or set(shop) - {"max_ticks", "upgrades", "vendor"}:
        raise BadInput("tuning.shop cần max_ticks và upgrades")
    _int_between("shop.max_ticks", shop["max_ticks"], 1, 1_000_000)
    if "vendor" in shop:
        from .inventory import KINDS
        vendor = shop["vendor"]
        if not isinstance(vendor, dict) or set(vendor) != {"buy_multiplier", "sell_prices"}:
            raise BadInput("shop.vendor cần buy_multiplier, sell_prices")
        _between("shop.vendor.buy_multiplier", vendor["buy_multiplier"], 0, 100)
        prices = vendor["sell_prices"]
        if not isinstance(prices, dict) or set(prices) != set(KINDS):
            raise BadInput("shop.vendor.sell_prices cần đủ các kind")
        for kind, price in prices.items():
            _int_between(f"shop.vendor.sell_prices.{kind}", price, 0, 1_000_000)
    upgrades = shop["upgrades"]
    if not isinstance(upgrades, dict) or set(upgrades) != {"oxygen", "hp"}:
        raise BadInput("tuning.shop.upgrades cần oxygen và hp")
    for kind, field in (("oxygen", "oxygen_max_s"), ("hp", "hp_max")):
        rows = upgrades[kind]
        if not isinstance(rows, list) or not rows:
            raise BadInput(f"shop.upgrades.{kind} cần mảng cấp")
        for i, row in enumerate(rows, 1):
            if not isinstance(row, dict) or set(row) != {"level", "price", field} or row["level"] != i:
                raise BadInput(f"shop.upgrades.{kind}: cấp phải tăng liên tiếp từ 1")
            _int_between(f"shop.upgrades.{kind}.level", row["level"], 1, len(rows))
            _int_between(f"shop.upgrades.{kind}.price", row["price"], 0, 1_000_000)
            if field == "hp_max":
                _int_between(f"shop.upgrades.{kind}.{field}", row[field], 1, 99)
            else:
                _between(f"shop.upgrades.{kind}.{field}", row[field], 1, 120)
    monsters = t["gather"].get("monsters")
    if not isinstance(monsters, dict) or not isinstance(monsters.get("species"), dict):
        raise BadInput("gather.monsters cần species")
    _int_between("gather.monsters.invuln_ticks", monsters.get("invuln_ticks"), 0, 10000)
    _between("gather.monsters.loss_ratio", monsters.get("loss_ratio"), 0, 1)
    for kind, cfg in monsters["species"].items():
        if not isinstance(cfg, dict):
            raise BadInput("monster species cần object")
        for key in ("patrol_speed", "chase_speed", "detect_radius", "exit_radius", "hit_radius", "recoil_dist"):
            _between(f"monsters.{kind}.{key}", cfg.get(key), 0, 1000)
        _int_between(f"monsters.{kind}.recoil_ticks", cfg.get("recoil_ticks"), 1, 10000)
        depths = cfg.get("depths")
        if not isinstance(depths, list) or len(depths) != 2 or not all(_num(x) for x in depths) or not 0 <= depths[0] < depths[1] <= t["gather"]["bounds"]["d"][1]:
            raise BadInput("monster.depths ngoài biên map")
    spawns = monsters.get("spawns")
    if not isinstance(spawns, list):
        raise BadInput("monsters.spawns cần mảng")
    seen = set()
    for m in spawns:
        if not isinstance(m, dict) or not isinstance(m.get("id"), str) or m["id"] in seen or m.get("kind") not in monsters["species"]:
            raise BadInput("monster spawn: id/loài không hợp lệ")
        seen.add(m["id"])
        _int_between("monster.from_day", m.get("from_day"), 1, 5)
        _pos_in("monster.pos", m.get("pos"), t["gather"]["bounds"], ("x", "d"))
        if not isinstance(m.get("waypoints"), list) or len(m["waypoints"]) != 2:
            raise BadInput("monster cần hai waypoint")
        for pt in [m["pos"], *m["waypoints"]]:
            _pos_in("monster.waypoint", pt, t["gather"]["bounds"], ("x", "d"))
            lo, hi = monsters["species"][m["kind"]]["depths"]
            if not lo <= pt[1] <= hi:
                raise BadInput("monster spawn/waypoint ngoài dải sâu loài")
