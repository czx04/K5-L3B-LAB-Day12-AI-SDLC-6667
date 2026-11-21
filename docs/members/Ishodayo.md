# Ishodayo — phản tư cá nhân (≤ 200 từ)

Nguyễn Thành Nam · `sim/quan`

- Tôi làm luật Quán P1 theo PRD-0 D/E/F: khách, giữ chỗ, kiên nhẫn, bếp, bưng, phục vụ, tiền, uy tín, hết ca; 13 test hộp đen: [d09e7e7](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/commit/d09e7e7). Sửa 2 lỗi chặn qua review, thêm test quét fixture sai kiểu: [35b237f](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/commit/35b237f). Cập nhật vai `TEAM.md`: [0f99a4b](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/commit/0f99a4b); gộp `dev`: [#3](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/3).
- Tôi xem trực tiếp, góp ý người làm, không review GitHub: [#4](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/4) gather core (lát bên, đối chiếu kho/quán), [#5](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/5) UI (snapshot quán), [#7](https://github.com/czx04/K5-L3B-LAB-Day12-AI-SDLC-6667/pull/7) bàn giao P1 lên main.
- Review #3 thấy AI siết PRD: khách chưa phục vụ có `tip: 0` bị mã 2, đỏ 16 test QA. Review thấy AI bỏ kiểm kiểu: `dish_id: []` gây crash (mã 1 thay vì 2); tôi cho AI viết test quét ~140 fixture sai kiểu, bắt thêm `stoves[].dish` sai kiểu.
- Tôi học: PRD không nói thì đừng để AI siết luật, ghi `docs/clarify.md`; quét sai kiểu bắt lỗi test ca thường bỏ sót; chốt hợp đồng sớm tránh hai người viết cùng module.
<!-- rút gọn ≤200 từ theo PRD P4, nội dung giữ nguyên ý tác giả -->
