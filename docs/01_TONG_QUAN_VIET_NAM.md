# AudioVerse — Bản hướng dẫn dự án bằng tiếng Việt

**Ngày:** 17/11/2026  |  **Loại tài liệu:** Định hướng sản phẩm và hướng dẫn bàn giao kỹ thuật  |  **Tình trạng:** Prototype cho môi trường local; chưa phát hành thương mại.

## I. Dự án chúng ta đang xây là gì?
AudioVerse là ứng dụng mobile dành cho khán giả Việt Nam, có hai trải nghiệm: **Thư viện truyện audio** và **Truyện tương tác rẽ nhánh**. Trong thư viện, người nghe thưởng thức truyện đã được cấp phép, bằng giọng người kể hoặc giọng tổng hợp AI. Trong chế độ tương tác, họ có thể lựa chọn hành động, làm thay đổi trạng thái thế giới và kết cục. Người không thích tương tác vẫn phải có thể nghe liền mạch theo kịch bản mặc định được biên tập.

### Ba năng lực cốt lõi
1. **Trải nghiệm audio:** tìm kiếm, thư viện, phát nền, tua, ngủ hẹn giờ, offline khi có quyền, đồng bộ tiến độ và tài khoản, hợp đồng tác giả/người đọc.
2. **Narrative engine:** đồ thị truyện, state machine, precondition/effect, lịch sử sự kiện không sửa ngược, bộ nhớ dài hạn, các nhánh do AI sinh có kiểm soát, chất lượng văn phong và giọng kể tiếng Việt.
3. **Nền tảng thương mại:** CMS tác giả, kiểm duyệt bản quyền, thanh toán, hạn mức tương tác AI, dữ liệu vận hành, analytics, bảo mật, thông báo và quản trị nội dung.

## II. Vì sao cần tách Audio Library khỏi AI Branching?
Quyền phát một file audio của người kể trên mạng **không đồng nghĩa** với quyền dùng truyện đó viết thêm nhánh mới, quyền dùng giọng người kể để clone hay quyền huấn luyện AI. Mỗi nội dung cần ghi rõ ai sở hữu bản truyện, bản dịch, giọng biểu diễn, master recording và quyền nào được cấp. Khi chỉ có quyền phát, AudioVerse phải phát nguyên trạng theo điều kiện cấp phép. Chế độ rẽ nhánh dùng truyện gốc của dự án hoặc nội dung đã được cấp quyền chuyển thể.

## III. Mã nguồn đã có gì?
- **Python API:** FastAPI gồm health, catalog, tạo phiên truyện, lấy trạng thái, gửi lựa chọn, xem lịch sử và phát MP3 demo.
- **Engine:** chỉ chấp nhận lựa chọn có thật trong scene hiện tại và thỏa điều kiện. Các hiệu ứng (ví dụ người chơi có chìa khóa hay có đồng đội) được lưu có phiên bản. Gửi cùng mã yêu cầu lần thứ hai không tạo sự kiện trùng lặp.
- **SQLite:** lưu story run và append-only choice events phục vụ demo. Production cần chuyển sang PostgreSQL, auth, backup và migration.
- **Web demo:** giao diện tối, nghe cảnh, chọn nhánh, theo dõi manh mối và kết cục qua `http://127.0.0.1:8765/`.
- **Flutter:** có mã nguồn giao diện danh sách, player foreground và lựa chọn; môi trường đóng gói không có Flutter nên chưa thể xác minh compile/native app. T001 là công việc đầu tiên khi làm trên máy Windows của bạn.
- **Audio mẫu:** 11 MP3 tổng hợp tự động bằng eSpeak từ truyện **Bên Kia Cánh Cửa** nguyên bản. Đây chỉ là kiểm thử kỹ thuật, chất giọng chưa phù hợp bán cho người nghe.
- **AI hiện tại:** Chưa gọi LLM hay API TTS trả phí. `DemoNarrativeProvider` làm nhiệm vụ minh họa hợp đồng kỹ thuật. Mô hình thật là giai đoạn T006–T007.
- **Test:** 17 bài kiểm thử Python đạt và đã chạy HTTP smoke tests trong môi trường build. Chưa có thiết bị Android/iOS xác nhận.

## IV. Kiến trúc production mục tiêu
Flutter cho Android/iOS; Python FastAPI modular monolith; PostgreSQL; queue/worker cho AI; object storage và streaming chỉ khi người dùng có quyền; cổng thanh toán native của Apple/Google; CMS cho tác giả, biên tập và người kiểm duyệt quyền; hạ tầng monitoring và chi phí AI. Phân loại pháp lý trò chơi điện tử trên mạng tại Việt Nam phải được chuyên gia xác nhận trước khi public.

## V. Chi phí cần hiểu đúng
- **Audio tạo sẵn:** Phát lại nhiều lần rất rẻ. 1 giờ MP3 64 kbps khoảng 28,8 MB. Chi phí thực thường đến từ quyền truyện, bản ghi, sản xuất/biên tập và tìm người nghe.
- **Audio tương tác AI:** Tăng theo giờ người dùng tạo mới. Ví dụ TTS Pro giả định $16,50/1 triệu ký tự và mật độ 45.000 ký tự/giờ -> ~$0,7425/giờ audio; thêm LLM, retry và hạ tầng. Không được bán hạn mức “AI không giới hạn” khi chưa có dữ liệu chi phí.
- **Hạ tầng:** object storage có thể thấp; API/auth/db/CDN/jobs cùng marketing và compliance mới là tổng chi phí. `scripts/cost_model.py` cho phép thay đổi kịch bản; các số liệu đều là **giả định nghiên cứu**.
- **GPU tự train:** Chưa nên đầu tư cho phiên bản đầu. Đo chất lượng API, độ trễ, tiếng Việt và chi phí thật trước. Nếu fine-tune giọng người thật, phải có quyền khai thác giọng và dữ liệu huấn luyện độc lập.

## VI. Cách phát triển dài hạn với Codex/AI Coding Agent
**Bắt đầu bằng** `AGENTS.md` + `scripts/agent_bootstrap_prompt.txt`. Agent đọc `PROJECT_STATE.md`, `CURRENT_TASK.md` và `BACKLOG.md` ở đầu mọi phiên. Chỉ triển khai một task chính; trước khi kết thúc phải chạy test, ghi lại test chưa chạy, cập nhật trạng thái và append `SESSION_LOG.md`. Khi đổi tài khoản hoặc cuộc trò chuyện, repo là bộ nhớ chung.

Các tài liệu nguồn: `PRD.md` nêu sản phẩm và đối tượng; `FUNCTIONAL_SPEC.md` nêu 182 yêu cầu; `ARCHITECTURE.md` mô tả services; `NARRATIVE_ENGINE.md` mô tả thuật toán; `AUDIO_TTS.md` mô tả dữ liệu giọng và benchmark; `LEGAL_RIGHTS_RELEASE_GATES.md` mô tả quyền và yêu cầu kiểm duyệt; `COST_MODEL.md` mô tả công thức kinh tế; `docs/tasks/` có 16 gói nhiệm vụ.

## VII. Kế hoạch từng giai đoạn
**R1:** Chạy được Flutter thật, kiểm tra player, mô hình quyền nội dung và chuyển đổi backend sang an toàn hơn. **R2:** LLM provider, state-aware writer, TTS API, cache, CMS, benchmark, cost ledger. **R3:** Kiểm duyệt nội dung, hợp đồng và hồ sơ pháp lý, native thanh toán, beta trong phạm vi đã được cho phép. **R4:** Phát hành, đo retention/monetization, mở rộng nội dung. **R5:** Fine-tune giọng Việt có quyền, creator network và nghiên cứu tối ưu sinh nhánh.

## VIII. Các quyết định không nên bỏ qua
1. Không tải/sao chép audio YouTube hoặc podcast khác về làm thư viện thương mại nếu chưa có quyền.
2. Không clone giọng người đọc chỉ vì họ đăng audio công khai.
3. Không biến LLM thành “nguồn chân lý” điều khiển các sự kiện trong truyện.
4. Không thử thanh toán tiền thật hoặc deploy backend demo ra Internet.
5. Không tuyên bố hệ thống hợp pháp để phát hành trò chơi tại Việt Nam khi chưa có đánh giá và thủ tục áp dụng.
6. Không bắt đầu fine-tuning trước khi thử nghiệm model API và có bộ dữ liệu có quyền hợp lệ.

## IX. Tiêu chuẩn đi tới bản có thể bán
Đầu tiên: người dùng thử thích câu chuyện, nghe tiếp tự nguyện, lựa chọn có tác động, chờ nhánh không gây khó chịu. Sau đó: chủ sở hữu tác phẩm/người kể đã cấp phép rõ ràng, hệ thống an toàn và tuân thủ, giá/hạn mức AI có lợi nhuận gộp, thanh toán thực kiểm tra được. Chỉ khi hai nhóm điều kiện trên cùng đạt mới triển khai thương mại.
