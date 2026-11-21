# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

> Quy ước: **Trạng thái** = `chốt` (PRD / Anh Năm hàng xóm / giảng viên đã xác nhận) hoặc `giả định` (nhóm tạm làm theo, PO đang hỏi). Code làm theo cột "Trả lời / giả định"; đổi thì cập nhật dòng này và [`docs/contracts/README.md`](contracts/README.md).
> 2026-11-21 08:02: PRD-0 phát hành, đối chiếu lại toàn bộ câu 1–11.

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Trạng thái | Ai quyết |
|---|---|---|---|---|---|
| 1 | 2026-11-21 0:10 | Khi `fainted`, file kho ghi gì? | Ghi `{"items":{}}`, đúng một lần. Giỏ bỏ theo LIFO, liệt kê ở `faint.data.lost`. | chốt — PRD-0 F, G | PO |
| 2 | 2026-11-21 0:10 | Chạy hết `--ticks` mà chưa `gather_end` thì có ghi kho không? | Không tạo, không ghi đè file. | chốt — PRD-0 G | PO |
| 3 | 2026-11-21 0:10 | `interact` trong vùng bến và cạnh nút hái cùng lúc? | Xét bến trước (khoảng cách tới tâm bến, tính cả đúng mép) → `docked`, không hái. | chốt — PRD-0 F | PO |
| 4 | 2026-11-21 0:12 | Ranh giới "dưới nước"? | `d ≤ 0.5` là mặt nước. dive/surface so đầu và cuối bước; oxy theo d cuối bước. Nổi lên đúng bước đáng lẽ ngạt thì hồi oxy, không ngạt. | chốt — PRD-0 F | PO |
| 5 | 2026-11-21 0:12 | Giỏ không đủ chỗ cho cả mẻ cá? | `hold_full` (`action:"catch"`, `fish_id`, `required`, `free`), không nhận con nào, giữ đàn, **không** đặt hồi chiêu, không thử đàn khác. | chốt — PRD-0 F | PO |
| 6 | 2026-11-21 0:15 | Tên và `data` của các sự kiện gather/quan? | Theo bảng PRD-0 mục E, đã chép vào contracts mục 3 (khác bản nháp ở `gather`, `fish_caught`, `hold_full`, `oxygen_empty`, `faint` và toàn bộ sự kiện quan). | chốt — PRD-0 E | PO |
| 7 | 2026-11-21 0:15 | Bắt cá xong đàn cá biến mất hay mọc lại? | Xóa đàn khỏi `fish[]`. Phase 1 cá đứng yên, không sinh thêm. | chốt — PRD-0 F | PO |
| 8 | 2026-11-21 0:18 | Khách chọn món thế nào khi nhiều món nấu được? | Chọn đều theo seed trong các món đủ nguyên liệu khả dụng (tồn vật lý − phần giữ), duyệt id món theo Unicode; giữ đúng công thức ngay khi tới. | chốt — PRD-0 F | PO |
| 9 | 2026-11-21 0:18 | Không có bàn trống khi tới lịch khách? | Bỏ lượt, không phát sự kiện. Có bàn mà không món nào đủ → `no_dish` `{}`. | chốt — PRD-0 F | PO |
| 10 | 2026-11-21 0:20 | `burn_s = null` nghĩa là gì? | Món chín không cháy; `ready_ticks` là tuổi món trên bếp, chỉ tăng cho món đã ready từ đầu bước. | chốt — PRD-0 A, F | PO |
| 11 | 2026-11-21 0:20 | Uy tín kẹp thế nào, boa làm tròn ra sao? | Kẹp `[reputation_min, reputation_max]`. Boa = `floor(base_price × tip_rate)` nếu tỷ lệ kiên nhẫn còn lại sau bước 1 ≥ `tip_min_patience_ratio`, không thì 0; boa dương cộng `tip_reputation` khi thu tiền. | chốt — PRD-0 F | PO |
| 12 | 2026-11-21 10:28 | Id khách (cũng là `order_id`) đặt theo mẫu nào? | Tiền tố `C` cộng số thứ tự cấp qua `IdAllocator`: `C1`, `C2`… Khách luôn dùng `order_id` trùng id khách. | chốt — PO quyết (PRD-0 không nói) | PO |
| 13 | 2026-11-21 10:28 | Scenario không khai `reserved` mà kho không đủ nguyên liệu cho đơn có sẵn thì sao? | Coi là input lỗi: thoát mã 2, **không** tự chuyển đơn sang `unfulfillable`. | chốt — PO quyết (PRD-0 không nói) | PO |

## Phase 2 — nguồn chốt
TICKET-02 do người dùng cung cấp được lưu ở `docs/tickets/TICKET-02.md`. Không thêm luật Shop tự đoán: oxygen 200/400 (45/60s), hp 250/500 (4/5), tối đa 600 tick. Màn intro/result/menu là trình bày live, headless chỉ có gather/quan/shop theo mục 4.4–4.5. Không bật mở rộng trong lần triển khai này.

## Phase 3 — câu hỏi chờ PO, giả định tích hợp

Nguồn: [PRD Phase 3](prd/phase-3.md). Các dòng P1–P2 phía trên là lịch sử; khi mâu thuẫn schema, yêu cầu [THAY THẾ] của P3 được ưu tiên (ví dụ kho rỗng hiện là `{"items":[]}`). Các giả định kỹ thuật dưới đây theo giao diện chung v1.2 do nhóm cung cấp, chưa ghi thành xác nhận của PO.

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Trạng thái | Ai quyết |
|---|---|---|---|---|---|
| P3-01 | 2026-11-21 | “Đủ độ chính xác” khi xuất fresh là bao nhiêu chữ số? | Dùng `round(fresh_u / 240, 6)` ở snapshot/event/file, dưới dạng số JSON; không bắt buộc giữ số 0 cuối. Kiểm ngưỡng và floor bằng giá trị nội bộ trước làm tròn. | giả định | Nhóm v1.2; PO cần xác nhận |
| P3-02 | 2026-11-21 | PRD gợi ý 240 đơn vị/điểm: có dùng thống nhất không? | Có: `fresh_u = round(fresh * 240)`, `per_tick_u = round(decay_per_s * 240 / tick_hz)`, kẹp đáy 0. Giá trị đầu vào không nằm đúng lưới 1/240 được lượng tử hóa khi nạp. Không tích lũy float theo tick. | giả định | Nhóm v1.2; PO cần xác nhận |
| P3-03 | 2026-11-21 | Pause có hao ở bước bật/tắt không? | Kế thừa P2: bước bật pause chỉ tăng tick ngoài, không hao; bước resume chạy gameplay ngay, hao đúng một bước. Hàng Shop/chờ nhập không hao, kể cả khi không pause. | giả định | QA theo P2 + P3; PO cần xác nhận |
| P3-04 | 2026-11-21 | `customers[].reserved` phải xuất theo thứ tự nào? | Là mảng id, không lặp; PRD chưa chốt thứ tự mảng phần giữ. QA so tập id cho công thức nhiều cá thể, chỉ ép thứ tự mà PRD quy định ở cook_started `(kind,id)` và các mảng thực thể theo id. | giả định | QA; PO cần xác nhận |
| P3-05 | 2026-11-21 | Mã AC-P3-xx chính thức nằm ở đâu? | PRD hiện không liệt kê mã AC; dùng mã QA cục bộ 01–24 theo tên test và docs/plan/phase-3.md. Tích hợp viên nối vào verification, đổi ánh xạ nếu PO cung cấp mã chính thức. | giả định | QA; PO cần xác nhận |
| P3-06 | 2026-11-21 | Hàng mua Chợ Chú Sáu có lệnh mua nguyên liệu nào ở bản nền? | Contract P2 trong worktree chỉ khai nâng cấp oxygen/hp. Chưa tự thêm lệnh mua nguyên liệu; nếu lát C có hỗ trợ từ nguồn chuẩn khác, cần cung cấp giao diện để QA bổ sung kiểm fresh 100/id mới/chờ nhập không hao. | giả định | QA; PO/tích hợp viên cần trả lời |

## Phase 4

Nguồn đối chiếu: [kế hoạch P4](plan/phase-4.md), [proof P4](proof/phase-4/README.md), `game.contract.json` và diff với tag `phase-3`. Đây là giả định chờ PO xác nhận; không bổ sung luật gameplay/kho/JSONL ngoài v1.2.

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Trạng thái | Ai quyết |
|---|---|---|---|---|---|
| P4-01 | 2026-11-21 | Bench đo vòng mô phỏng, cổng `/state` hay khung render trình duyệt? | Tạm hiểu cần đo khung render của cảnh lặn 1280×720, seed 42, làm nóng 3 s rồi đo 30 s theo kế hoạch. Bench tại `c73d78b` đếm lượt HTTP `/state`, không đo khung render; chưa dùng số này để xác nhận FPS render. PO cần chốt đại lượng và cách đo. | giả định | TODO(nhóm): hỏi PO |
| P4-02 | 2026-11-21 | Soak lấy `earned`/`score` từng Ngày ở thời điểm nào? | Lấy tại lúc Shop đóng (`shop_end`), sau giao dịch Shop, trước khi dữ liệu Ngày kế tiếp thay thế; `earned` là tổng tích lũy, `score = earned + reputation_multiplier × floor(reputation)` theo runner hiện có, không dùng tiền còn lại sau mua làm doanh thu. Kế hoạch D1–D5 lặp cho Ngày 6–10. | giả định | TODO(nhóm): hỏi PO |
| P4-03 | 2026-11-21 | Test Contract v1.3 thay gameplay/kho/JSONL không? | Chỉ tăng `contract_version` lên `1.3` và thêm `bench_cmd`/`soak_cmd`; gameplay, kho cá thể, độ tươi và JSONL giữ v1.2. Diff `git diff phase-3 c73d78b -- game.contract.json` chỉ có ba thay đổi này; chưa suy thêm luật từ số phiên bản. | giả định | TODO(nhóm): hỏi PO |
