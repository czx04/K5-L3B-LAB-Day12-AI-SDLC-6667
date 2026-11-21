# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt:
- Điều tệ:
- 1 hành động cho Phase 3:

## Phase 3 (nhanh) — đổi kho đếm sang kho cá thể
- Điều tốt: chốt giao diện chung trước (cá thể `fresh_u`, 240 đơn vị/điểm, `chonoi/fresh.py`) nên 5 lát làm song song gộp không conflict văn bản; test hộp đen `tests/test_fresh_p3.py` (24 AC) viết từ PRD trước khi có code, sau ghép đạt 24/24.
- Điều tệ: hai PR cùng sửa `chonoi/jsonl.py` để xuất fresh 6 chữ số, bản gộp gọi biến `key` không tồn tại → mọi headless crash, 121 test đỏ trên p3/integ. Merge phase 2 (`7932de0`) ghi đè 3 dòng ai-usage-log và phản tư của Toan bằng bản cũ trên `dev` — phát hiện khi làm phase 3, đã khôi phục.
- 1 hành động cho Phase 4: file dùng chung (jsonl.py, game.contract.json, inventory.py, docs/*) chỉ một người sửa mỗi lần; trước khi merge `dev` → `main` chạy `git diff main dev -- docs/` để không đè ghi chép.
- Ý kiến cá nhân: TODO(nhóm).

## Phase 4 (cuối)

Đối chiếu tại `origin/dev` = `c73d78b` (worktree `p4/e`). Nguồn: `git log --all`, `git shortlog -sn --no-merges origin/dev` và các tài liệu dẫn dưới đây. `gh pr list --state all --limit 100 --json number,title,state,baseRefName,headRefName,mergeCommit,url` không kết nối được `api.github.com`; chưa xác minh review, bình luận hoặc trạng thái PR hiện tại trên GitHub.

- Rà lại hành động Phase 2 và Phase 3:
  - **Phase 2: chưa có hành động được ghi để đối chiếu.** Mục “1 hành động cho Phase 3” ở trên còn trống; không thể kết luận đã làm hay chưa hoặc tự gán nguyên nhân. TODO(nhóm): bổ sung hành động đã chốt và bằng chứng nếu có.
  - **Phase 3: đã ghi quy tắc, chưa đủ bằng chứng thực thi toàn bộ.** Commit `5f7c0b0` thêm quy tắc mỗi file dùng chung chỉ một người sửa và `git diff main dev -- docs/` vào `AGENTS.md`; [kế hoạch P4](plan/phase-4.md) phân chủ sở hữu cụ thể, ba file của lát này thuộc czx04. Chưa có log chứng minh mọi lần merge đều chạy lệnh diff hoặc báo kênh nhóm. Vướng: thiếu biên bản thực thi, cần tích hợp viên lưu kết quả trước lần merge phát hành.
- Điều tốt / điều tệ (sự kiện kiểm được):
  - Tốt: lỗi tích hợp P3 được sửa ở `8073576`; `6a67eaa` khôi phục ghi chép P1. [Verification P3](verification/phase-3.md) và [smoke trên main `535972c`](proof/phase-3/smoke-535972c/summary.txt) ghi 12/12 PASS, 233 test OK. [Proof P4](proof/phase-4/README.md) ghi clone sạch chạy được bằng 3 lệnh, có ảnh và log regression tại `162c7dd`.
  - Tệ: hai nhánh sửa `chonoi/jsonl.py` (`950366b`, `95280df`) gộp thành lời gọi biến `key` không tồn tại, mọi headless crash, 121 test đỏ theo retro P3/ai-log; `8073576` sửa lỗi. Phase 2 (`7932de0`) làm mất ghi chép P1 khi tích hợp, được khôi phục ở `6a67eaa`: kiểm tài liệu cũng cần nằm trong bước review.
  - Tệ: PR #22 (`c84ac8d`) được merge trên dòng `main` sau `phase-3`, rồi revert #25 (`523be51`, nội dung `4ab1767`) và revert-revert #27 (`f7a3521`, nội dung `9925749`). Nhánh Thái sau đó có merge tích hợp `4eda8a6` trước PR #28 (`162c7dd`) vào `dev`. Chuỗi này kiểm được từ graph; chi tiết “gây PR #28 conflict” chưa có biên bản trong repo, TODO(nhóm): xác nhận từ PR khi truy cập được GitHub.
  - Tag `phase-1` hiện trỏ `5c9d097` (merge #12, chứa proof `f92d54d`), còn [verification P1](verification/phase-1.md) ghi smoke tại `ca074fe` và chờ tag vào commit chứa bằng chứng. Không có reflog tag trong worktree này để xác minh lần dời tag, SHA cũ hay lý do; TODO(nhóm): bổ sung bằng chứng việc tag `phase-1` phải dời.
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
  - `git shortlog -sn --no-merges origin/dev` tại `c73d78b`: czx04 **28**; Ishodayo **11**; Hai Duong **9**; Le Quy Toan **9**; itsbra1vo **5**; Hồng Thái **3**. Đây là số theo tên tác giả git, toàn lịch sử nhánh, không chỉ P4; chưa gộp bí danh và không dùng để suy năng suất cá nhân.
  - Cách đọc code có ghi nhận: [czx04](members/czx04.md) dùng Codex review #3/#4, gộp thử và chạy test; [Ishodayo](members/Ishodayo.md) xem trực tiếp #4/#5/#7, góp ý với người làm và ghi rõ không để review GitHub; [ToanLee5433](members/ToanLee5433.md) đối chiếu kho ở #3 và HUD ở #5; [itsbra1vo](members/itsbra1vo.md) đối chiếu snapshot/hợp đồng và kiểm tay giao diện. Chưa có số lượng review P4 đã xác minh.
  - Theo [ai-usage-log](ai-usage-log.md): ToanLee5433 P1 **~45k tokens**; czx04 chỉ có ghi nhận **~20k token ở phiên tích hợp P3**, các phiên khác chưa đo nên không có tổng cá nhân; Ishodayo và itsbra1vo chưa đo. P2 chưa phân bổ theo người; P4 czx04 chưa đo. Không suy token từ số commit hay số phiên.
- Một lần AI sai và cách nhóm phát hiện:
  - Lát bench của Thái có `tools/bench.py` chỉ nhận `--measure-s`, chưa nhận `--duration`. Tái hiện tại lát này bằng `python3 tools/bench.py --duration 30 --seed 42 --out /tmp/p4-e-bench.json`: mã 2, `unrecognized arguments: --duration 30`. Chạy đúng tham số runner được yêu cầu làm lộ lệch giao diện, dù proof cũ chỉ chạy lệnh mặc định đã ghi đạt. Bản PRD/runner P4 chưa được lưu trong `docs/`; chưa xác minh nguyên văn toàn bộ lệnh ngoài tham số vừa chạy.
  - Soak cũ hoàn thành 10 Ngày nhưng [soak.json tại `162c7dd`](proof/phase-4/regression-162c7dd/soak.json) thiếu `earned`/`score` từng ngày; không thể dùng “0 crash” để kết luận đủ đầu ra. TODO(nhóm): chạy lại runner và kiểm schema sau khi lát soak sửa.
- Nếu làm lại, đổi gì: **TODO(nhóm)** — ý kiến cá nhân chưa thu thập. Đề mục để nhóm cân nhắc từ sự kiện trên: khóa người giữ file dùng chung, kiểm lệnh runner với đủ cờ và trường JSON trước khi ghi đạt, kiểm diff tài liệu, chốt commit bằng chứng rồi mới gắn tag.
- Hành động tiếp theo (đề xuất chờ nhóm nhận việc): người giữ bench/soak sửa giao diện và trường thiếu; QA chạy lại đúng lệnh runner, regression và lưu bằng chứng trên commit phát hành; tích hợp viên lưu `git diff main dev -- docs/`, kiểm đích merge `dev`, kiểm tag/Release cùng commit theo kế hoạch P4. TODO(nhóm): xác nhận chủ việc, hạn hoàn tất, ý kiến cá nhân và các bằng chứng GitHub còn thiếu; chưa coi là hành động đã chốt.

Kiểm chứng lát tài liệu P4 trên `c73d78b`: `PYTHONPATH=tests:. python3 -m unittest discover -s tests` chạy 234 test, 1 FAIL do test P3 còn ép phiên bản `1.2` trong khi contract là `1.3`, 1 ERROR do sandbox chặn bind socket ở `test_live.LiveServerTest.test_state_input_and_clean_stop` (được phép bỏ qua theo phân công). Không sửa test/code ngoài ba file được giao. `git diff --check` đạt.
