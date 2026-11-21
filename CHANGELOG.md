# Changelog

## v1.0.0 / v1.3 — Phase 4
- **Hợp đồng & Cấu hình:** Bổ sung `contract_version: "1.3"`, khai báo `bench_cmd` (`python3 tools/bench.py`) và `soak_cmd` (`python3 tools/soak.py`) trong `game.contract.json`. Cập nhật `chonoi/contract.py` chấp nhận contract v1.3.
- **Soak Testing:** Thêm `tools/soak.py` chạy bot tất định 10 Ngày (`gather` -> `quan` -> `shop`, lặp D1–D5 ở Ngày 6–10), đo độ ổn định và xuất kết quả `soak.json`.
- **Benchmarking & UI Cảnh báo:** Đo hiệu năng cảnh lặn 1280×720 (`bench.json`), hỗ trợ 3 cảnh báo (thủy quái, sắp hết oxy, khách sắp giận) và chế độ tương phản cao.
- **Đóng gói & Phát hành:** Chuẩn bị bản phát hành v1.0.0, cập nhật README, LICENSE và CREDITS.

## v1.2 — Phase 3

- **Test thay bởi luật mới** (mỗi chỗ có comment `# P3 [THAY THẾ]`): fixture/kỳ vọng kho đếm trong `tests/test_smoke_p1.py`, `test_gather*.py`, `test_quan*.py`, `test_day_p2.py`, `test_live.py` chuyển sang mảng cá thể; `test_python_starter_units.py` theo adapter mới.
- **Sửa tích hợp:** `chonoi/jsonl.py` xuất `fresh` 6 chữ số, số thực khác 3 chữ số (sửa NameError sau khi gộp hai bản, 8073576).
- **Smoke:** `tools/smoke_p3.sh` → `docs/proof/phase-3/smoke-<sha>/`.

- **Breaking change:** kho đếm theo kind không còn hợp lệ (mã 2); file kho,
  gather.hold, quan.stock và snapshot chuyển sang mảng cá thể có id/kind/fresh.
  `customers[].reserved` chuyển từ lượng sang mảng id; món chốt giá theo độ tươi.
- Freshness dùng số nguyên 240 đơn vị/điểm, gather −2/tick, quan −1/tick;
  dưới 30 là ươn, phát spoiled một lần theo thứ tự id. Adapter ghi nguyên tử,
  theo id, sáu chữ số thập phân; bảo toàn đơn vị/ngưỡng khi đọc lại.
- Day bàn giao nguyên cá thể cùng tick, giữ id tăng xuyên Ngày; mẫu giỏ Ngày
  kế được cấp id mới theo thứ tự vào giỏ. Shop không hao tươi; vendor nếu có
  chọn bán tươi nhất và nhập hàng mua riêng vào kho quán Ngày kế ở fresh 100.
- Cập nhật fixture trước: `{"items":{"ca_loc":1,"bong_sung":2}}`;
  sau: `{"items":[{"id":"I1","kind":"ca_loc","fresh":100},
  {"id":"I2","kind":"bong_sung","fresh":100},
  {"id":"I3","kind":"bong_sung","fresh":100}]}`.
  Scenario dùng mảng trên cho hold/stock (không bọc items). Phần giữ trước
  `{"ca_loc":1}` thành `["I1"]`; không khai reserved để sim tự chọn tươi nhất.
  Đừng đổi fixture kho đếm âm tính: phải tiếp tục kiểm mã 2.
- Lát A đổi adapter/contract/scenario/runner/day vì PRD bắt buộc schema mới;
  không đổi luật gather/quan trong lát này. Kiểm riêng: 8 test FreshInventoryP3
  và 5 test DayAdapterP3 (double giao diện B/C); kiểm sim thật sau tích hợp.

  Kết quả tại worktree lát A: 13/13 test nền tảng/ranh giới qua; toàn bộ 176
  test có 59 fail, 11 error do phần sim/fixture còn schema trước tích hợp
  (ví dụ GatherSim chưa chuyển fresh sang fresh_u). Chưa xác nhận regression
  với sim B/C thật. PRD Phase 3 có sẵn được giữ nguyên; không commit/push.
