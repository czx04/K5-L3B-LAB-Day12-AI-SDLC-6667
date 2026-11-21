# Credits

## Khung và phần đóng góp

- Khung `chonoi/` (CLI, runner, RNG, kho, JSONL, live/web ban đầu): giảng viên cung cấp cho lab; xem [docs/STARTER.md](docs/STARTER.md). Không có tên tác giả hoặc giấy phép riêng trong README/STARTER hiện tại; giữ quyền và thông báo của tác giả gốc như ghi chú trong [LICENSE](LICENSE).
- Luật chơi và phần giao diện nhóm phát triển: Nhóm 6667; thành viên/vai trò ở [TEAM.md](TEAM.md). Phần đóng góp của nhóm dùng MIT, năm 2026.

## Đồ họa, âm thanh và font

Đã rà danh sách `git ls-files` và các tham chiếu tài nguyên trong `chonoi/web/index.html`:

- Đồ họa trong game: **tự vẽ bằng canvas, không dùng asset ngoài**. Hình cá, người lặn, rong, bến, thủy quái, bếp/bàn và hiệu ứng được vẽ bằng mã Canvas; HUD/menu dùng HTML/CSS.
- Font: `system-ui, sans-serif` có sẵn trên thiết bị; không đóng gói hoặc tải font ngoài. Biểu tượng là ký tự Unicode/emoji do hệ thống/trình duyệt hiển thị.
- Âm thanh: không có file âm thanh được Git theo dõi và không thấy tham chiếu tải/phát âm thanh trong giao diện.
- Ảnh `.jpg`/`.png` được Git theo dõi chỉ nằm trong `docs/proof/phase-1/`, `docs/proof/phase-2/`, `docs/proof/phase-4/`: ảnh chụp giao diện dùng làm bằng chứng kiểm chứng của nhóm, không phải asset nạp vào game. Nguồn và bối cảnh ở các ghi chép `docs/proof/` tương ứng.
- Giao diện không tham chiếu ảnh, âm thanh, font, thư viện hoặc CDN bên ngoài; các yêu cầu mạng trong mã là đến máy chủ live nội bộ.

## Công cụ AI

Nhóm đã dùng Codex, Claude Code và GitHub Copilot để hỗ trợ lập trình, giao diện, kiểm thử và tài liệu; xem [nhật ký AI](docs/ai-usage-log.md) và [ghi chép thành viên](docs/members/). Không thấy tài nguyên ảnh/âm thanh/font tạo bằng AI được đóng gói làm asset trong game.
