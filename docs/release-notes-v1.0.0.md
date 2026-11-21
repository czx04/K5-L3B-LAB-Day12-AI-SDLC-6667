# Quán Ăn Chợ Nổi v1.0.0 — nhóm 6667

Bản phát hành game v1.0.0 dùng Test Contract v1.3; gameplay, kho và JSONL giữ v1.2. Nhóm tổng hợp ghi chú này từ lịch sử git, README và bằng chứng trong repo. Hiện có tag `phase-1`, `phase-2`, `phase-3`; `phase-4` và phát hành `v1.0.0` còn chờ tích hợp, kiểm trên main và gắn tag.

## Điểm mới

- **Phase 1 (v1.0):** buổi sáng lặn, quản lý oxy/ngạt, hái/bắt và giao kho; buổi tối đón khách, giữ nguyên liệu, nấu/phục vụ, nhận tiền/boa và uy tín. Headless xuất JSONL tất định, kho đếm nối hai buổi.
- **Phase 2 (v1.1):** chơi trọn vòng gather → quán → Shop theo kế hoạch D1–D5; mua nâng cấp oxy/Máu cho Ngày kế, pause/resume, menu và tổng kết. Cá bơi/sinh, Cá Sấu; quán 2 bếp, 4 bàn, 6 món.
- **Phase 3 (v1.2):** kho cá thể `{id, kind, fresh}`, hao tươi/ươn, giữ nguyên liệu theo id, giá chốt theo độ tươi và HUD độ tươi. Kho đếm cũ trả mã 2; xem hướng di trú fixture trong [CHANGELOG](../CHANGELOG.md).
- **Phase 4 (v1.3):** manifest thêm `bench_cmd`/`soak_cmd`, bench nhận `--duration`, soak có earned/score từng Ngày, ba cảnh báo chữ/biểu tượng và tương phản cao. README, LICENSE, CREDITS và tài liệu phát hành được rà soát.

## Cách chạy

Cần Git, **Python 3** và trình duyệt hiện đại hỗ trợ Canvas/JavaScript; hướng dẫn README dành cho macOS/Linux, CI dùng Python 3.12. Chỉ dùng thư viện chuẩn, không cần pip hay build. Ba lệnh từ [README](../README.md):

```bash
git clone https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667.git
cd K5-L3B-LAB-Day12-AI-SDLC-6667
python3 -m chonoi.live --mode day
```

Mở địa chỉ in ra (mặc định `http://127.0.0.1:8000/`), bấm Chơi. WASD/mũi tên để di chuyển, E tương tác, Space bắt cá, Esc/P pause; Shop mua bằng nút. Nút Tương phản cao trên thanh công cụ bật/tắt chế độ đó. Điều khiển đầy đủ và cách tính điểm ở README.

## Kiểm thử, headless, bench và soak

Chạy từ thư mục gốc repo:

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
tools/smoke_p3.sh
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out gather.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out quan.jsonl
python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 111000 --out day.jsonl
python3 tools/bench.py --seed 42 --duration 30 --out bench.json
python3 tools/soak.py --seed 7 --days 10 --out soak.json
```

Bench cần mở socket localhost; `--measure-s` vẫn là bí danh của `--duration`. Soak lặp D1–D5 cho Ngày 6–10, ghi `earned` tích lũy và `score` khi Shop đóng, sau giao dịch và trước khi sang Ngày kế.

## Đóng gói

```bash
tools/package_release.sh
```

Script tạo `dist/cho-noi-v1.0.0.zip` với thư mục gốc `cho-noi-v1.0.0/`, in đường dẫn và SHA-256. `git archive` chỉ lấy file đã commit tại `HEAD`; phải tích hợp/commit đủ nội dung phát hành trước khi tạo gói chính thức. Kiểm `git status --short --untracked-files=all -- dist/` trước bàn giao và **không commit `dist/`**. Script từ chối nếu `dist/` đã có file được git theo dõi. Đây là thao tác đóng gói cục bộ, không tạo tag hay đăng GitHub Release.

## Bằng chứng

- Ma trận từng phase: [P1](verification/phase-1.md), [P2](verification/phase-2.md), [P3](verification/phase-3.md), [P4](verification/phase-4.md) trong `docs/verification/`.
- Bằng chứng lịch sử: [P1](proof/phase-1/), [P2](proof/phase-2/), [P3](proof/phase-3/), [P4](proof/phase-4/README.md) trong `docs/proof/`.
- [Summary tích hợp a154cbf](proof/phase-4/integ-a154cbf/summary.txt): unittest OK (log/ma trận ghi 239 test), bench exit 0; soak hoàn tất 10/10 Ngày, 0 crash. Smoke P3 12/12 PASS tại `735e4e3` sau khi nhận contract 1.3; không phải cùng SHA với lượt tích hợp a154cbf.
- Các bằng chứng trên chưa chứng nhận commit phát hành trên main. Cần chạy lại kiểm tra tại commit gắn tag; xem ma trận P4 để biết mục đạt, còn thiếu và phạm vi từng bằng chứng.

## Giới hạn đã biết

- Bench đo tốc độ phản hồi HTTP `/state`, **không phải render Canvas** trong trình duyệt; không dùng các số FPS đó để xác nhận FPS render.
- `tools/smoke_p1.sh` và `tools/smoke_p2.sh` không còn hiệu lực vì dựng fixture kho đếm, bị v1.2 từ chối đúng luật. Dùng unittest cho regression còn hiệu lực và smoke P3 cho kho cá thể.
- Không làm mở rộng `current`, `reservations`, leaderboard hay phụ đề SFX; các mở rộng weapon/net/snake/burn/vendor/ca_ho/settings chưa bật theo README.
- Ảnh bằng chứng P4 chưa hiển thị rõ banner “KHÁCH SẮP GIẬN”; ma trận chưa xác nhận đủ mục cảnh báo.
- Các giả định P3/P4 trong [docs/clarify.md](clarify.md) **chưa được PO xác nhận**, gồm độ chính xác/lượng tử hóa fresh, pause và thứ tự reserved, giao diện vendor, đại lượng bench và thời điểm chốt số liệu soak. Không coi giả định là quyết định đã chốt.

## Nhóm

Theo [TEAM.md](../TEAM.md), nhóm 6667 có bốn thành viên: Le Quy Toan (`ToanLee5433`), Nguyễn Thành Nam (`Ishodayo`), Dam Hong Thai (`itsbra1vo`), Dư Văn Hùng (`czx04`). Giấy phép và nguồn tài nguyên: [LICENSE](../LICENSE), [CREDITS.md](../CREDITS.md).
