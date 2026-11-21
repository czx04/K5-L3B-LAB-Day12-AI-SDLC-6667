# Changelog

Các phiên bản v1.0–v1.3 dưới đây là **Test Contract**; v1.0.0 là phiên bản phát hành game. Tag được đối chiếu bằng `git tag` và `git show phase-1 phase-2 phase-3 --stat`.

## v1.3 — Phase 4 · phát hành game v1.0.0

- **Điểm mới:** contract khai `bench_cmd` (`python3 tools/bench.py`) và `soak_cmd` (`python3 tools/soak.py`). Bench nhận `--duration` (giữ bí danh `--measure-s`), xuất `avg_fps`, `p1_low_fps`, `frames`, `measured_s`, `load_ms`; hiện đo phản hồi HTTP `/state`, không phải render Canvas.
- Soak bot tất định chạy 10 Ngày, lặp kế hoạch D1–D5 ở Ngày 6–10; `results[]` ghi `earned` tích lũy, uy tín và `score` khi Shop đóng, sau giao dịch và trước Ngày kế.
- Live có cảnh báo chữ/biểu tượng thủy quái gần, oxy sắp hết, khách sắp giận và chế độ tương phản cao. Bằng chứng ảnh cảnh báo khách còn thiếu theo ma trận P4.
- README hướng dẫn clone sạch trong ba lệnh, điều khiển, test/headless/bench/soak; bổ sung LICENSE, rà CREDITS và tài liệu phát hành. Script đóng gói chỉ lấy file đã commit tại `HEAD`, không đưa thay đổi chưa commit vào zip.
- **Breaking change:** manifest tăng `contract_version` lên `1.3`, thêm hai lệnh; gameplay, schema kho cá thể và JSONL giữ v1.2.
- **Tag:** dự kiến `phase-4` và phát hành `v1.0.0` trên cùng commit main; chưa có trong danh sách tag cục bộ lúc rà soát. Không coi tài liệu này là xác nhận đã phát hành.
- **Bằng chứng:** [verification P4](docs/verification/phase-4.md), [summary tích hợp](docs/proof/phase-4/integ-a154cbf/summary.txt): unittest OK; soak 10/10 Ngày, 0 crash. Smoke P3 12/12 PASS ở `735e4e3`; cần chạy lại trên commit main gắn tag.

## v1.2 — Phase 3

- **Điểm mới:** nguyên liệu có id/kind/fresh; độ tươi giảm trong gather/quán, dừng khi pause và ở Shop. Dưới 30 là ươn; phát `spoiled` một lần theo thứ tự id. Giữ nguyên liệu tươi nhất, thay phần giữ vừa ươn và chốt giá món theo độ tươi khi bắt đầu nấu; boa theo giá đã chốt. HUD hiển thị độ tươi/hàng ươn.
- Freshness dùng số nguyên 240 đơn vị/điểm, gather −2/tick, quán −1/tick; xuất fresh tối đa sáu chữ số thập phân, số thực khác ba chữ số. Adapter ghi nguyên tử, sắp id, bảo toàn ngưỡng khi đọc lại. Sửa lỗi tích hợp `NameError` trong `chonoi/jsonl.py` tại `8073576`.
- Day bàn giao nguyên cá thể cùng tick, giữ id tăng xuyên Ngày; mẫu giỏ Ngày kế được cấp id mới theo thứ tự vào giỏ. Không bật mở rộng `current`/`reservations` hay vendor.
- **Breaking change:** kho đếm theo kind bị từ chối với mã 2; file kho, `gather.hold`, `quan.stock` và snapshot chuyển sang mảng cá thể. `customers[].reserved` chuyển từ lượng sang mảng id; giá món thay đổi theo fresh.
- **Cập nhật fixture:** `{"items":{"ca_loc":1,"bong_sung":2}}` → `{"items":[{"id":"I1","kind":"ca_loc","fresh":100},{"id":"I2","kind":"bong_sung","fresh":100},{"id":"I3","kind":"bong_sung","fresh":100}]}`. Scenario hold/stock dùng mảng trực tiếp; reserved `{"ca_loc":1}` → `["I1"]`, hoặc bỏ reserved để sim tự chọn. Giữ fixture kho đếm âm tính để kiểm mã 2.
- Test đổi theo luật mới có comment `# P3 [THAY THẾ]`; smoke P1/P2 cũ không còn hiệu lực do dựng kho đếm, regression còn hiệu lực nằm trong unittest.
- **Tag:** `phase-3` → `88f0872`. [Verification P3](docs/verification/phase-3.md), [smoke trên main 535972c](docs/proof/phase-3/smoke-535972c/summary.txt): 12/12 PASS, 233 test OK; commit tag bổ sung tài liệu.

## v1.1 — Phase 2

- **Điểm mới:** vòng `gather → quan → Shop`, `--mode day --days 1..5`, `day_plan` D1–D5 và bàn giao kho trong bộ nhớ; tiền, earned, uy tín xuyên Ngày. Shop mua Bình oxy/Áo phao, áp cấp từ Ngày kế, không trừ earned/điểm khi mua.
- Pause/resume cho cả ba pha; live có menu, intro, kết quả Ngày, Shop, tổng kết và HUD kế hoạch. Cá bơi/sinh theo seed; Cá Sấu tuần tra/đuổi/đánh, mất giỏ và bất tử tạm thời theo tuning. Quán có 2 bếp, 4 bàn, 6 món và 6 nguyên liệu.
- **Breaking change:** manifest lên `1.1`, cập nhật tuning chuẩn; thêm mode day, inputs pause/shop_done/buy, scenario day, snapshot/event ngày và pha. File kho vẫn là kho đếm v1.0; fixture từ chối day ở P1 được thay vì day trở thành lõi. Nút mở rộng đúng kiểu nhưng chưa bật được bỏ qua theo TICKET-02.
- **Tag:** `phase-2` → `c541cb8`. [TICKET-02](docs/tickets/TICKET-02.md), [verification P2](docs/verification/phase-2.md): 163 test OK, smoke kho/day tất định/nâng cấp OK tại lần kiểm được ghi; bằng chứng ở [docs/proof/phase-2/](docs/proof/phase-2/).

## v1.0 — Phase 1

- **Điểm mới:** gather lõi di chuyển, lặn/oxy/hồi oxy, ngạt/ngất, hái bông, bắt cá và cập bến giao giỏ. Quán lõi khách đến/gọi món, giữ nguyên liệu, nấu/bưng/phục vụ, thanh toán/boa và uy tín; điểm `earned + 100 × floor(reputation)`.
- File kho đếm `{"items":{"ca_loc":1,"bong_sung":2}}` nối hai tiến trình gather/quán; headless Test Contract v1.0 có seed/inputs/scenario, snapshot/event/end JSONL tất định, mã thoát và kiểm dữ liệu. Live chơi hai buổi với HUD/điều khiển.
- **Breaking change:** bản nền đầu tiên, chưa có phiên bản trước để di trú; schema kho đếm lịch sử được thay ở v1.2.
- **Tag:** `phase-1` → `5c9d097`. [Verification P1](docs/verification/phase-1.md), [smoke trên main ca074fe](docs/proof/phase-1/smoke-ca074fe/summary.txt): 10/10 PASS, 121 test OK (5 skip); commit tag bổ sung tài liệu.
