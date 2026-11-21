# Bằng chứng Phase 4 — Nam (đóng gói + QA regression)

## 0–15': clone sạch + regression trên `dev` @ `de33d6a` (contract v1.3)

Máy: Windows 11, Git Bash, Python 3.15.2. Clone mới vào thư mục tạm, không cài thêm gì.

### Clone sạch → bản có giao diện: 3 lệnh — ĐẠT

```bash
git clone -b dev https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667.git
cd K5-L3B-LAB-Day12-AI-SDLC-6667
python3 -m chonoi.live --mode day        # = run_cmd trong game.contract.json
```

- Server in địa chỉ ([`clean-clone/live.log`](clean-clone/live.log)); `GET /` → 200, `GET /state` → `mode day`, Ngày 1, pha `gather`.
- Menu chính Chơi/Thoát: [`clean-clone/1-menu.jpg`](clean-clone/1-menu.jpg). Bấm Chơi → đồng hồ chạy, HUD kế hoạch Ngày 1, oxy, giỏ, nút Tạm dừng: [`clean-clone/2-dang-choi-ngay1.jpg`](clean-clone/2-dang-choi-ngay1.jpg).
- README hiện vẫn hướng dẫn `--mode gather` và ghi Test Contract v1.1 → cần cập nhật (việc của Nam ở bước sau).

### Regression P1–P3

| Kiểm | Kết quả | Ghi chú |
|---|---|---|
| `unittest` toàn bộ ([`unittest.log`](regression-de33d6a/unittest.log)) | **CHƯA ĐẠT: 233 test, 1 fail**, 5 skip | `test_fresh_p3.test_ac_p3_01_contract_v12` khẳng định `contract_version == "1.2"`, nay là `"1.3"` sau PR #23. Luật không sai; test cần chấp nhận v1.3. |
| `tools/smoke_p3.sh` ([`smoke_p3.log`](regression-de33d6a/smoke_p3.log), [`summary`](regression-de33d6a/smoke_p3-summary.txt)) | **10/12 PASS** | Ngưỡng 30 → `spoiled` tick 1, bàn giao file gather → quán khớp id/kind/fresh, kho đếm → mã 2, `day` chạy, JSONL/kho tất định: PASS. FAIL `contract_v1_2` (kiểm cứng `"1.2"`) và `unittest` (do test trên). |
| `tools/smoke_p1.sh` ([`smoke_p1.log`](regression-de33d6a/smoke_p1.log)) | **Hết hiệu lực** | Fixture kho đếm (`hold: ["ca_loc", …]`, `{"items":{"ca_loc":1}}`) bị thay bởi kho cá thể ở Phase 3 (breaking change trong CHANGELOG) → gather trả mã 2 đúng luật mới. Phần bàn giao kho còn hiệu lực đã được `smoke_p3` kiểm. |
| `tools/smoke_p2.sh` | **Hết hiệu lực** | Bước đầu chạy unittest với `PYTHONPATH=tests:.` (dừng vì `set -e`); fixture cũng dùng kho đếm như P1. Vòng `day` đã được `smoke_p3` (`day_runs`) kiểm. |

### Cần người giữ file sửa (không thuộc file Nam giữ)
1. `tests/test_fresh_p3.py::test_ac_p3_01_contract_v12` và `tools/smoke_p3.sh` (`contract_v1_2`): nhận `"1.3"` (v1.3 giữ nguyên khối `freshness`).
2. `tools/smoke_p1.sh`, `tools/smoke_p2.sh`: chuyển fixture sang kho cá thể hoặc ghi rõ "thay bởi luật mới, xem smoke_p3".
