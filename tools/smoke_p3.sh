#!/usr/bin/env bash
# Smoke Phase 3 (contract v1.2, kho cá thể + độ tươi). Bằng chứng: docs/proof/phase-3/smoke-<sha>/
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
sha="$(git rev-parse --short HEAD)"
out="docs/proof/phase-3/smoke-${sha}"
if [[ -e "$out" ]]; then
    echo "Đã có bằng chứng cho commit $sha ở $out — không ghi đè. Xóa thư mục đó nếu muốn chạy lại." >&2
    exit 1
fi
mkdir -p "$out"
summary="$out/summary.txt"
printf 'sha: %s\ntime_utc: %s\n' "$(git rev-parse HEAD)" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "$summary"
failed=0
record() { printf '%s %s\n' "$1" "$2" | tee -a "$summary"; [[ "$1" == FAIL ]] && failed=1 || true; }
check() { local label="$1"; shift; if "$@"; then record PASS "$label"; else record FAIL "$label"; fi; }

headless_cmd="$(python3 -c 'import json; print(json.load(open("game.contract.json", encoding="utf-8"))["headless_cmd"])')"
headless() { python3 -c 'import shlex, subprocess, sys; sys.exit(subprocess.call(shlex.split(sys.argv[1]) + sys.argv[2:]))' "$headless_cmd" "$@"; }

check contract_v1_2_or_1_3 python3 -c 'import json; d=json.load(open("game.contract.json")); assert d["contract_version"] in ("1.2","1.3")  # P4: 1.3 chỉ thêm bench/soak, gameplay v1.2; f=d["tuning"]["freshness"]; assert (f["initial"],f["gather_decay_per_s"],f["quan_decay_per_s"],f["spoiled_below"])==(100,0.5,0.25,30)'

# (a) Ngưỡng 30: fixture PRD, gather một bước không input -> spoiled tick 1
printf '%s\n' '{"gather":{"hold":[{"id":"I1","kind":"ca_linh","fresh":30}],"random_fish":false,"monsters":[]}}' > "$out/threshold.json"
check threshold_run headless --mode gather --seed 1 --ticks 1 --scenario "$out/threshold.json" --out "$out/threshold.jsonl"
check threshold_spoiled_tick1 grep -qxF '{"type":"event","tick":1,"phase":"gather","name":"spoiled","data":{"item_id":"I1","kind":"ca_linh","location":"hold"}}' "$out/threshold.jsonl"

# (b) Bàn giao file: cùng mẫu fresh 100, cập bến frame 0 -> quán --ticks 0 khớp id/kind/fresh
printf '%s\n' '{"gather":{"hold":[{"id":"I1","kind":"ca_linh","fresh":100}],"random_fish":false,"monsters":[]}}' > "$out/dock.json"
printf '%s\n' '{"frames":[{"tick":0,"interact":true}]}' > "$out/dock-inputs.json"
check gather_dock headless --mode gather --seed 1 --scenario "$out/dock.json" --inputs "$out/dock-inputs.json" --ticks 1 --out "$out/gather.jsonl" --inventory-out "$out/catch.json"
check quan_reads_file headless --mode quan --seed 1 --inventory "$out/catch.json" --ticks 0 --out "$out/quan.jsonl"
check handoff_matches python3 - "$out" <<'PY'
import json, sys
d = sys.argv[1]
f = json.load(open(f"{d}/catch.json"))["items"]
rows = [json.loads(l) for l in open(f"{d}/gather.jsonl")]
end = [r for r in rows if r["type"] == "event" and r["name"] == "gather_end"][0]["data"]
assert end["reason"] == "docked" and end["inventory"]["items"] == f, (end, f)
stock = json.loads(open(f"{d}/quan.jsonl").readline())["stock"]
assert [(i["id"], i["kind"]) for i in stock] == [(i["id"], i["kind"]) for i in f] == [("I1", "ca_linh")]
assert all(abs(a["fresh"] - b["fresh"]) <= 0.01 for a, b in zip(stock, f))
assert abs(f[0]["fresh"] - (100 - 0.5 / 60)) <= 0.01
PY

# (c) Kho đếm v1.1 -> mã 2, không tạo output
printf '%s\n' '{"items":{"ca_loc":1}}' > "$out/counted-v1_1.json"
set +e; headless --mode quan --seed 1 --ticks 0 --inventory "$out/counted-v1_1.json" --out "$out/counted.jsonl" 2> "$out/counted.stderr"; code=$?; set -e
check counted_inventory_exit_2 test "$code" -eq 2

# (d) day chạy được; (e) tất định
check day_runs headless --mode day --seed 7 --ticks 3000 --out "$out/day.jsonl"
check gather_repeat headless --mode gather --seed 1 --scenario "$out/dock.json" --inputs "$out/dock-inputs.json" --ticks 1 --out "$out/gather-repeat.jsonl" --inventory-out "$out/catch-repeat.json"
check deterministic_jsonl cmp -s "$out/gather.jsonl" "$out/gather-repeat.jsonl"
check deterministic_inventory cmp -s "$out/catch.json" "$out/catch-repeat.json"

# (f) toàn bộ regression P1–P3
if PYTHONPATH=tests:. python3 -m unittest discover -s tests -v > "$out/test.log" 2>&1; then record PASS unittest; else record FAIL unittest; fi
rm -f "$out/counted.jsonl"

echo "Evidence: $out"
exit "$failed"
