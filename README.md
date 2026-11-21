# Quán Ăn Chợ Nổi — nhóm 6667

Game 2D quản lý quán ăn miền Tây: buổi sáng Út Sen lặn bắt cá, hái bông trên sông Chín Khúc (`gather`); buổi tối nấu và phục vụ khách trên nhà bè của Má Tư (`quan`). Những gì mang về buổi sáng quyết định quán bán được món nào.

Lab Day 12 · AI SDLC · Phát hành v1.0.0 · Test Contract v1.3 (gameplay, kho và JSONL giữ luật v1.2). Thành viên và vai: [`TEAM.md`](TEAM.md).

## Chạy từ clone sạch (macOS / Linux, chỉ cần Python 3, không cài thêm gì)

Yêu cầu: macOS hoặc Linux có Git, Python 3 và trình duyệt hiện đại hỗ trợ Canvas/JavaScript. Game chỉ dùng thư viện chuẩn Python, không cần `pip`, engine hay bước build; CI dùng Python 3.12.

```bash
git clone https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667.git
cd K5-L3B-LAB-Day12-AI-SDLC-6667
python3 -m chonoi.live --mode day
```

Mở địa chỉ lệnh in ra (mặc định `http://127.0.0.1:8000/`). Bấm **Chơi**, đọc lời dặn Má Tư rồi bấm **Bắt đầu buổi sáng**. Chơi riêng buổi sáng: `python3 -m chonoi.live --mode gather`; buổi tối: `python3 -m chonoi.live --mode quan`.

**Chơi nối hai buổi:** mặc định, khi Gather kết thúc game tự chuyển sang Quán và mang theo kho:

```bash
python3 -m chonoi.live --mode gather
```

Muốn giữ Gather ở màn kết thúc và chạy Quán riêng bằng file kho:

```bash
python3 -m chonoi.live --mode gather --no-auto-transition --inventory-out kho.json
python3 -m chonoi.live --mode quan --inventory kho.json
```

## Điều khiển

| Phím | Buổi sáng (`gather`) | Buổi tối (`quan`) |
|---|---|---|
| WASD / mũi tên | Bơi (S / ↓ là lặn xuống) | Đi lại trong nhà bè |
| E | Cập bến (kết thúc buổi, giao giỏ) · hái bông khi ở mặt nước | Nấu ở bếp · bưng món · phục vụ ở bàn |
| Space | Bắt đàn cá khi đang lặn | — |
| R | Chơi lại | Chơi lại |

**Esc / P** hoặc nút **Tạm dừng / Tiếp tục**: pause/resume (kể cả Shop). Trong Shop, bấm **Mua** ở Bình oxy/Áo phao; bấm **Đóng Shop / Ngày tiếp** để đi tiếp hoặc chờ Shop tự đóng. Nâng cấp áp dụng từ Ngày kế. Nút **Về menu** quay về menu. Thiết bị cảm ứng có nút di chuyển, E và Space trên màn hình.

Bấm nút **Tương phản cao** trên thanh công cụ để bật/tắt; hiện chưa có phím tắt riêng.

Cảnh báo bằng chữ và biểu tượng, không chỉ bằng màu:

- **⚠ THỦY QUÁI GẦN**: thủy quái ở gần; bơi tránh xa.
- **🫧 OXY SẮP HẾT**: oxy còn ≤ 25%; nổi lên mặt nước để hồi oxy.
- **‼ KHÁCH SẮP GIẬN**: kiên nhẫn còn ≤ 25%; ưu tiên phục vụ.

HUD buổi sáng: thời gian, oxy, Máu, giỏ. Buổi tối: kho khả dụng, món khách gọi, kiên nhẫn, trạng thái bếp, món trên tay, tiền, uy tín.

## Luật chính và cách tính điểm

- **Buổi sáng:** dưới nước mất oxy, nổi lên thì hồi. Hết oxy thì cứ 60 tick ngạt mất 1 Máu; hết 3 Máu thì ngất, mất cả giỏ. Giỏ chứa 12 ô. Cập bến hoặc hết giờ thì phần trong giỏ thành kho của quán.
- **Buổi tối:** khách đến theo lịch, gọi một trong 3 món nấu được từ kho và giữ nguyên liệu ngay. Nấu → bưng → phục vụ trước khi khách hết kiên nhẫn. Nguyên liệu là từng cá thể có id/độ tươi; độ tươi giảm theo thời gian, dưới 30% là ươn và không dùng nấu. Giá món chốt khi bắt đầu nấu bằng `floor(giá niêm yết × độ tươi trung bình / 100)`. Khách ăn xong trả tiền món; còn ≥ 50% kiên nhẫn lúc được phục vụ thì boa `floor(giá đã chốt × 0.2)` và quán được +0.2 uy tín. Khách bỏ về vì chờ lâu: −0.5 uy tín. Uy tín trong [0, 5], bắt đầu 3.0.
- **Điểm** (ở mọi snapshot và dòng `end`):

  ```
  score = earned + 100 × floor(reputation)
  ```

  `earned` là tổng tiền thu (nghìn đồng, gồm boa). Ví dụ thu 72, uy tín 3.2 → `72 + 100 × 3 = 372`.

Số liệu đầy đủ ở [`game.contract.json`](game.contract.json); hợp đồng tích hợp ở [`docs/contracts/README.md`](docs/contracts/README.md).

## Test (1 lệnh)

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

Smoke Phase 3 (kho cá thể, ngưỡng ươn, bàn giao kho và tính tất định):

```bash
tools/smoke_p3.sh
```

Các smoke Phase 1/2 bên dưới giữ để tra lịch sử; fixture kho đếm đã được thay ở v1.2, xem [bằng chứng Phase 4](docs/proof/phase-4/README.md) về giới hạn regression hiện tại.

Smoke hai tiến trình (gather → file kho → quan) và lưu bằng chứng vào `docs/proof/phase-1/smoke-<sha>/`:

```bash
tools/smoke_p1.sh
```

## Headless (Test Contract)

```bash
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out gather.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out quan.jsonl
python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 111000 --out day.jsonl
```

Tùy chọn: `--scenario sc.json`, `--inputs in.json`; Gather có `--inventory-out kho.json`, Quán có `--inventory kho.json`. Kho dùng mảng cá thể `{id, kind, fresh}` theo v1.2; file kho đếm cũ không còn hợp lệ.

Mã thoát: `0` bình thường · `2` tham số/dữ liệu sai · `1` lỗi chạy. Cùng seed và đầu vào → JSONL và file kho giống từng byte.

## Benchmark và soak

Lệnh benchmark theo yêu cầu phát hành (seed 42, đo 30 giây):

```bash
python3 tools/bench.py --seed 42 --duration 30 --out bench.json
```

**Giới hạn đã biết:** `--measure-s` vẫn nhận làm bí danh của `--duration`. Công cụ hiện đo tốc độ phản hồi `/state` của live qua HTTP; các trường `avg_fps`, `p1_low_fps` không phải phép đo render Canvas trong trình duyệt. Cần quyền mở socket localhost.

Soak 10 Ngày, seed 7, xuất báo cáo JSON:

```bash
python3 tools/soak.py --seed 7 --days 10 --out soak.json
```

## Sáng tạo của nhóm

Giao diện live có cảnh sông vẽ bằng Canvas (cá, rong, bong bóng), HUD kho cá thể/độ tươi, thông báo sự kiện và nút cảm ứng. Đây là phần trình bày của live, không chạy trong headless và không thay luật mô phỏng. Chưa bật các mở rộng weapon/net/snake/burn/vendor/ca_ho/settings; không coi các tính năng lõi bắt buộc của phase là sáng tạo thêm.

## Phát hành v1.0.0

Tải bản đóng gói tại [GitHub Release v1.0.0](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/releases/tag/v1.0.0), giải nén, vào thư mục chứa `game.contract.json` rồi chạy `python3 -m chonoi.live --mode day`. Môi trường như mục chạy từ clone sạch. Giấy phép và nguồn tài nguyên: [LICENSE](LICENSE), [CREDITS.md](CREDITS.md).

## Tài liệu nhóm

[`TEAM.md`](TEAM.md) · [`AGENTS.md`](AGENTS.md) · [`docs/contracts/`](docs/contracts/README.md) · [`docs/clarify.md`](docs/clarify.md) · [`docs/verification/phase-1.md`](docs/verification/phase-1.md) · [`docs/proof/`](docs/proof/) · [`docs/plan/`](docs/plan/) · [`docs/ai-usage-log.md`](docs/ai-usage-log.md) · [`docs/retro.md`](docs/retro.md) · [`docs/standup.md`](docs/standup.md) · [`docs/members/`](docs/members/) · [`CREDITS.md`](CREDITS.md)

## Về lab

Yêu cầu từng phase mở theo giờ tại lab board **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)**. Chi tiết khung Python của giảng viên (cái gì có sẵn, đổi ngôn ngữ thế nào): [`docs/STARTER.md`](docs/STARTER.md).


## Phase 2 — Chơi trọn vòng ngày
```bash
python3 -m chonoi.live --mode day
python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl
tools/smoke_p2.sh
```
Live mặc định 5 Ngày; `--days 1..5` chọn số Ngày. Headless mặc định 1 Ngày. Bấm Chơi, xem lời dặn Má Tư, WASD bơi/đi, E hái/cập bến/nấu/bưng/phục vụ, Space bắt cá, Esc/P pause. Shop mua Bình oxy/Áo phao bằng nút, đóng sớm hoặc chờ 10 s hoạt động. Cấp mua áp dụng từ Ngày kế; earned và điểm không bị trừ khi mua. Thoát trở về màn lời chào để đóng thẻ trình duyệt.

Lõi đã bổ sung: vòng gather→quan→Shop, kế hoạch D1–D5, menu/intro/kết quả/tổng kết, pause cả Shop, HUD mục tiêu và quái, 6 tên món. Chưa bật các mở rộng weapon/net/snake/burn/vendor/ca_ho/settings. Nguồn: `docs/tickets/TICKET-02.md`; kiểm chứng: `docs/verification/phase-2.md`.
