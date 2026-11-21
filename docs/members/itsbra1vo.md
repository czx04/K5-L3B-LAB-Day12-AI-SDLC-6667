# itsbra1vo — phản tư cá nhân (≤ 200 từ)

Dam Hong Thai · `client/ui` · Scrum/Release.

- Tôi đã làm (kèm link commit):
  - Hoàn thiện HUD, thông báo sự kiện, điều khiển cảm ứng và hiển thị dữ liệu hai buổi trong giao diện client UI ([7190e56](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/commit/7190e56fd798facdce2e5ef48bd35d7a245c5c1f), gộp qua [PR #5](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/5)).
  - Phase 4: thêm cảnh báo thủy quái gần, oxy thấp, khách sắp giận; nút tương phản cao; `/metrics`; benchmark `tools/bench.py`.
- Tôi đã review (kèm link): Đối chiếu [PR #5](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/5) với snapshot/hợp đồng và chạy kiểm tay hai buổi trong [biên bản Phase 1](../proof/phase-1/manual.md); phát hiện một lỗi hiển thị nhỏ ở cửa sổ cao.
- AI sai ở đâu và tôi phát hiện thế nào: AI dễ sinh fallback giao diện giả định khóa snapshot tồn tại và tên món trùng id nội bộ. Tôi đối chiếu `/state`, hợp đồng và các snapshot thực tế; sau đó bổ sung kiểm tra meta/bounds, chuẩn hóa dữ liệu khách/bếp và tên món hiển thị.
- Điều tôi học được: Giao diện không chỉ vẽ đẹp mà còn phải chịu lỗi dữ liệu, cửa sổ và thiết bị khác nhau. Cần kiểm tay trên trình duyệt, đối chiếu snapshot với hợp đồng và ghi bằng chứng thay vì chỉ tin màn hình hoặc output AI.
