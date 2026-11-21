# Ishodayo — phản tư cá nhân (≤ 200 từ)

Nguyễn Thành Nam · `sim/quan`

- Tôi đã làm: P1 luật Quán theo PRD-0 D/E/F, 13 test hộp đen, sửa 2 lỗi chặn qua review ([#3](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/3)). P2 2 bếp/4 bàn, 6 món, `day_plan`, `plan_dishes`/`carry` cho day, 12 test ([#11](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/11)). P3 sửa `jsonl.py` xuất `fresh` 6 chữ số, xanh 7 test quán và 10 test liên quan ([#16](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/16)). P4 clone sạch 3 lệnh, regression P1–P3, bench, soak ([#30](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/30)); README, LICENSE, CREDITS, gói zip do czx04 commit.
- Tôi đã review (xem trực tiếp, góp ý người làm, không review trên GitHub): [#4](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/4) gather, [#5](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/5) UI, [#7](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/7) bàn giao P1.
- AI sai: siết luật hơn PRD (`tip: 0` bị mã 2, đỏ 16 test QA) và bỏ kiểm kiểu (`dish_id: []` crash), cả hai lộ ra qua review #3; tôi cho AI viết test quét ~140 fixture sai kiểu. P4 lần đo đầu thiếu phần của Thái, phát hiện khi đối chiếu `dev`, đo lại.
- Tôi học: PRD không nói thì ghi `docs/clarify.md`, đừng để AI tự siết; file dùng chung chỉ một người sửa; đo trên đúng commit tích hợp.
