# Bằng chứng Phase 4 — Nam (đóng gói + QA regression)

> **Cập nhật sau tích hợp:** các lỗi nêu dưới đây đã được xử lý. `735e4e3` cho `tools/smoke_p3.sh` nhận contract `"1.3"`; trên bản tích hợp `a154cbf`: unittest **239 test, OK**, smoke P3 **12/12 PASS** ([`integ-a154cbf/`](integ-a154cbf/), [ma trận phase 4](../../verification/phase-4.md) AC-P4-06). Từ `a154cbf` tới tag `phase-4` (`14342ef`) chỉ thêm `tools/package_release.sh` và một dòng trong `smoke_p3.sh`, không đổi code game. Phần dưới là biên bản gốc tại `162c7dd`, giữ làm lịch sử.

## 0–15': clone sạch + regression trên `dev` @ `162c7dd`

`162c7dd` = contract v1.3 (Toan, PR #23) + bench/cảnh báo (Thái, PR #28).
Máy: Windows 11, Git Bash, Python 3.15.2. Clone mới vào thư mục tạm, không cài thêm gì.
(Lần chạy trước trên `de33d6a` thiếu phần của Thái nên đã thay bằng lần này.)

### Clone sạch → bản có giao diện: 3 lệnh — ĐẠT

```bash
git clone -b dev https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667.git
cd K5-L3B-LAB-Day12-AI-SDLC-6667
python3 -m chonoi.live --mode day        # = run_cmd trong game.contract.json
```

- Server in địa chỉ ([`live.log`](clean-clone-162c7dd/live.log)), trang mở được.
- Menu chính Chơi/Thoát: [`1-menu.jpg`](clean-clone-162c7dd/1-menu.jpg). Bấm Chơi, giữ S → Út Sen lặn, oxy giảm (28 s), banner "Lặn xuống", HUD kế hoạch Ngày 1: [`2-dang-lan-ngay1.jpg`](clean-clone-162c7dd/2-dang-lan-ngay1.jpg).
- README vẫn hướng dẫn `--mode gather` và ghi Test Contract v1.1 → cần cập nhật (việc của Nam, bước sau).

### Regression P1–P3, bench, soak

| Kiểm | Kết quả | Ghi chú |
|---|---|---|
| `unittest` toàn bộ ([log](regression-162c7dd/unittest.log)) | **CHƯA ĐẠT: 234 test, 1 fail**, 6 skip | `test_fresh_p3.test_ac_p3_01_contract_v12` khẳng định `contract_version == "1.2"`, nay `"1.3"`. Luật không sai; test cần nhận v1.3. |
| `tools/smoke_p3.sh` ([log](regression-162c7dd/smoke_p3.log), [summary](regression-162c7dd/smoke_p3-summary.txt)) | **10/12 PASS** | Ngưỡng 30 → `spoiled` tick 1, bàn giao file gather → quán khớp id/kind/fresh, kho đếm → mã 2, `day` chạy, JSONL/kho tất định: PASS. FAIL `contract_v1_2` (kiểm cứng `"1.2"`) và `unittest` (do test trên). |
| `tools/smoke_p1.sh` ([log](regression-162c7dd/smoke_p1.log)) | **Hết hiệu lực** (9 FAIL) | Fixture kho đếm (`hold: ["ca_loc", …]`) bị thay bởi kho cá thể ở Phase 3 → gather trả mã 2 đúng luật mới. Bàn giao kho còn hiệu lực do `smoke_p3` kiểm. |
| `tools/smoke_p2.sh` | **Hết hiệu lực** | Dừng ở bước unittest đầu (`set -e`, `PYTHONPATH=tests:.`), fixture cũng kho đếm. Vòng `day` do `smoke_p3` (`day_runs`) kiểm. |
| `bench_cmd` `python3 tools/bench.py` ([bench.json](regression-162c7dd/bench.json)) | **ĐẠT** | 1280×720, seed 42, đo 30.001 s: `avg_fps` 93.1, `p1_low_fps` 80.0, 2793 frame, `load_ms` 10.7 (≥ 30 FPS). Máy Thái đo 544 FPS ([`bench.json`](bench.json)) — khác máy. |
| `soak_cmd` `python3 tools/soak.py` ([soak.json](regression-162c7dd/soak.json), [log](regression-162c7dd/soak.log)) | **ĐẠT** | 10/10 Ngày, 0 crash, 2.9 s. |

### Cần người giữ file sửa (không thuộc file Nam giữ)
1. `tests/test_fresh_p3.py::test_ac_p3_01_contract_v12` và bước `contract_v1_2` trong `tools/smoke_p3.sh`: nhận `"1.3"` (v1.3 giữ nguyên khối `freshness`).
2. `tools/smoke_p1.sh`, `tools/smoke_p2.sh`: chuyển fixture sang kho cá thể hoặc ghi rõ "thay bởi luật mới, xem smoke_p3".
