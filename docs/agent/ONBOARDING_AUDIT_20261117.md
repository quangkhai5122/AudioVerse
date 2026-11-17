# AudioVerse — Audit tiếp quản 2026-11-17 (T000)

**Kết luận:** R0 là prototype local có backend kiểm chứng; R1 mobile chưa được nghiệm thu. Audit DONE; không triển khai T001, không có tính năng production được nghiệm thu. Hồ sơ này phân biệt kiểm tra trực tiếp với kết luận đọc mã và bằng chứng đóng gói cũ.

## 1. Sản phẩm và kiến trúc
Mục tiêu B2C Việt Nam: thư viện truyện audio có quyền, tương tác rẽ nhánh tùy chọn, narrative engine nhất quán và nền tảng tài khoản/thanh toán/CMS về sau. Quyền stream, offline, derivative, tts, voice_clone, training tách biệt; AI chỉ soạn bản nháp, chuyển trạng thái xác định mới ghi canon.

Hiện thực hiện tại: Flutter source + browser client -> FastAPI modular monolith -> pure flag/choice engine + SQLite runs/events; một JSON truyện 11 cảnh, ba kết cục, JSON quyền demo và 11 MP3 eSpeak được starter khai báo tạo từ truyện gốc. Không có gọi AI thật. Kiến trúc mục tiêu Postgres/auth/private media/worker/queue/LLM/TTS/billing được mô tả nhưng chưa triển khai. Không thay stack hoặc ADR trong phiên này.

Đã đọc toàn bộ tài liệu bắt buộc trong yêu cầu, AGENTS/bootstrap, tám ADR, T001/T002/T003 và API/data/mobile/security/legal/test/runbook liên quan; đối chiếu mọi module Python/Dart/JS, test, script, workflow, cấu hình và demo content. Tài liệu tài chính/pháp lý là giả định và gate dự án; audit này không xác minh giá nhà cung cấp, văn bản luật hay cấp phê duyệt thay chuyên gia.

## 2. Kiểm kê implementation và trạng thái

| Thành phần | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Backend API + engine | DONE (demo) | 17 test hiện có; HTTP server loopback; catalog/work/run/choice/events, invalid/stale/idempotent cases |
| Graph truyện | DONE (demo) | Test duyệt tất cả nhánh; 11 cảnh; endings s8/s9/s10; flags/preconditions |
| SQLite persistence | PARTIAL | Transaction và unique(run_id, idem_key); không edition hash/migration/replay restore/DB immutability |
| Demo rights gate | PARTIAL | Deny action không có quyền, chưa review, voice_clone/training; không term/territory/reviewer/takedown |
| Audio fixtures | DONE về giao file; PARTIAL về QA | 11 MP3 HTTP 200; s0 Range 206; không nghe đánh giá chất giọng trong phiên này |
| Web UI | PARTIAL | HTML/CSS/JS và HTTP đạt, cú pháp JS đạt; chưa browser E2E hoặc nghe thật |
| Flutter | PARTIAL; validation BLOCKED | lib + một widget test có mã; không wrappers/lockfile, thiếu toolchain; chưa analyze/test/build/device |
| AI contract | PARTIAL | DemoNarrativeProvider deterministic và DisabledRemoteProvider; chưa được gọi từ route live; không planner/generation |
| Production platform | PLANNED | Auth/RBAC/Postgres/private media/rights CMS/LLM/TTS/payment/analytics/lifecycle/offline chưa có |
| Public/commercial release | BLOCKED | Quyền/pháp lý/bảo mật/mobile/store/billing và chuyên gia chưa đạt |

DONE chỉ áp dụng phạm vi demo và phép kiểm đã chạy. Register 182 requirements giữ DEMO/SOURCE/PLANNED như thuật ngữ riêng; không suy ra % hoàn thành sản phẩm hay DONE-PROD.

## 3. Môi trường và Git baseline
- Workspace `D:\Python_Project\AudioVerse`; ban đầu unborn `main`, chưa có commit, tracked files bằng 0; 117 file starter (116 checksum entries + manifest) chưa được track. **116/116 hash khớp trước sửa**.
- Origin `https://github.com/quangkhai5122/AudioVerse.git`, public; GitHub xác nhận owner/account `quangkhai5122` và push/admin access. `git ls-remote --symref origin` thực sự trả rỗng, exit 0. Không có remote history để ghi đè.
- Nhánh `codex/t000-onboarding-audit`; initial commit `94fda967aedb61d7c5e624b58242b9eaf32f651c` push thành công, remote hash khớp. GitHub tự chọn nhánh đầu tiên làm default khi kho rỗng; chưa có ref main. Không force, merge, xóa nhánh hoặc đổi default branch bằng API. SESSION_LOG ghi bằng chứng; commit riêng sau đó chỉ hoàn tất handoff.
- Git 2.49.0.windows.1; Node 24.11.1; Java 22.0.2. `python` là Windows Store alias không chạy; `py -3.14` đăng ký C:\Python314\python.exe không tồn tại.
- Python thực tế `D:\miniconda3\python.exe` **3.13.9**; tạo `.venv` riêng, không sửa dependency của môi trường dùng chung. Cài editable dev dependencies theo pyproject thành công sau khi cho phép kết nối mạng cho cài đặt local.
- Không tìm thấy Flutter/Dart/adb trong PATH; Flutter SDK không có ở các vị trí phổ biến đã kiểm tra; Android SDK không có ở `%LOCALAPPDATA%\Android\Sdk`. Không tìm thấy ffmpeg/ffprobe/espeak/gh/Ruff hệ thống trong PATH; Ruff đã có trong `.venv`. Không tái tạo audio hoặc cài Flutter trong phiên này.
- Không có biến `AUDIOVERSE_*` được đặt lúc baseline. Settings hỗ trợ AUDIOVERSE_ENV (chỉ demo), DB_PATH, launcher HOST/PORT. API_BASE là Dart define. File DB/test/cache/venv và egg-info được loại khỏi Git; không cần secret để chạy demo.
- Dependency khai báo: Python >=3.11, FastAPI/Uvicorn/Pydantic + pytest/httpx/Ruff; Dart >=3.8,<4 với Flutter/http/just_audio/flutter_lints. Python chưa có lock; Flutter chưa resolve dependency. Workflow chỉ backend Ubuntu/Python 3.11, chưa Flutter hoặc deploy.

Các phiên bản thực chạy trong `.venv`: FastAPI 0.163.1, Starlette 1.10.0, Pydantic 2.14.3/pydantic_core 2.50.4, Uvicorn 0.54.0, httpx 0.28.1/httpcore 1.0.9, pytest 9.2.0, Ruff 0.17.5, pip 25.2. Đây là snapshot 2026-11-17, không phải lock hay khuyến nghị version mới nhất.

## 4. Lệnh và kết quả thực chạy

Các lệnh dưới đây chạy từ repository root trên PowerShell, trừ phần được ghi khác.

| Lệnh / phép kiểm | Kết quả |
|---|---|
| `python -m pytest` | Không thực thi được: Windows Store alias không truy cập được |
| `python scripts/check_repo.py` | Cùng lỗi alias; không ghi PASS |
| `py -3.14 -m pytest` / `py -3.14 scripts/check_repo.py` | Launcher trỏ interpreter không tồn tại |
| `& 'D:\miniconda3\python.exe' -m pytest` | Collection lỗi thiếu fastapi; chưa có môi trường riêng |
| `& 'D:\miniconda3\python.exe' scripts/check_repo.py` | PASS: 11 scenes, 182 requirements, assets/docs |
| `& 'D:\miniconda3\python.exe' -m venv .venv` | Thành công |
| `.\.venv\Scripts\python.exe -m pip install -e '.[dev]' --disable-pip-version-check --retries 1 --timeout 30` | Thành công; lần đầu không có mạng bị WinError 10013, lần chạy có quyền kết nối cài đủ deps |
| `.\.venv\Scripts\python.exe -m pytest` | **17 passed, 1 warning**; chạy trước sửa và sau sửa |
| `.\.venv\Scripts\python.exe scripts/check_repo.py` | **PASS: 11 scenes, 182 requirements, assets and agent docs** |
| `.\.venv\Scripts\python.exe -m compileall -q backend scripts` | PASS, exit 0 |
| `.\.venv\Scripts\python.exe -m ruff check backend scripts --select E4,E7,E9,F` | Baseline FAIL 8 E701; sau sửa PASS |
| `.\.venv\Scripts\python.exe -m ruff check backend scripts` | Sau E701 còn 7 I001; sửa import order, sau đó **All checks passed** |
| `node --check web/app.js` | PASS, exit 0 |
| `scripts.package_release.create_zip` qua Python stdin, hai ZIP tạm dưới `.venv` | PASS: starter 119 files và docs 71 files; ZipFile.testzip đạt, ZIP tạm đã xóa; không ghi ra thư mục cha |
| `.\.venv\Scripts\python.exe -m pip check` | No broken requirements found |
| `.\.venv\Scripts\python.exe scripts/build_requirements.py` | Sinh 182 requirements; kiểm tra byte ban đầu khác do Windows CRLF; chuẩn hóa LF cho hash khớp bản gốc và khôi phục LF; không đổi nội dung register |
| PowerShell here-string Python -> `.\.venv\Scripts\python.exe -` (HTTP smoke) | Server Uvicorn subprocess ở 127.0.0.1/cổng trống, DB temp; health + 6 page/API routes 200; cả 11 MP3 200; Range s0 bytes=0-15 trả 206/16 bytes; run 201; 4 choices tới s8; 4 events. Server được dừng và temp DB tự xóa |
| Checksum starter + rà file/secret signatures | 116/116 khớp trước sửa; không phát hiện signature private-key/token phổ biến trong source candidate. Đây không phải chứng nhận secret scanning tuyệt đối |

Cảnh báo hiện có: StarletteDeprecationWarning về TestClient/httpx. Không tự đổi thư viện vì test vẫn đạt; xử lý dependency compatibility/pinning trong task phù hợp. Kiểm tra local Python 3.13 không thay cho CI Python 3.11.

**CI xác minh sau push:** [initial 94fda96 / run 44065446574](https://github.com/quangkhai5122/AudioVerse/actions/runs/44065446574) và [handoff 23aac92 / run 44065663346](https://github.com/quangkhai5122/AudioVerse/actions/runs/44065663346) đều completed/success. Backend job Ubuntu/Python 3.11 xác nhận từng bước install deps, compile, repository integrity, tests, Ruff critical đạt. Full Ruff là phép kiểm local riêng; chưa có Flutter CI. Truy vấn đầu tiên trả 0 runs là snapshot trước khi kết quả xuất hiện, không phải kết luận cuối.

**Chưa chạy:** Flutter doctor/pub get/analyze/test/build, Android emulator/thiết bị, iOS/Xcode, browser/audio listening, tải audio qua CDN/weak network, concurrency stress, backup restore, penetration/security scan đầy đủ, AI/TTS thật, payment/store/legal review. Không ghi nhận các phần này là đạt.

## 5. Findings, debt và giới hạn claim

| ID | Mức / loại bằng chứng | Phát hiện và nơi xử lý |
|---|---|---|
| A01 | CI gate; chạy tái hiện | 8 E701 trong build_requirements/check_repo/package_release; 7 I001 trong imports. Đã sửa tối thiểu; full Ruff và 17 test đạt |
| A02 | Environment; thực chạy | Alias Python hỏng hoặc base Miniconda thiếu FastAPI; giải quyết bằng `.venv` riêng. Khi đổi phiên/sandbox Windows, pytest mặc định bị `WinError 5` ở `%TEMP%\pytest-of-*` và `.pytest_cache\v\cache`; giải quyết bằng `-p no:cacheprovider --basetemp=".venv\pytest_tmp"`. Flutter/native validation vẫn BLOCKED (T001) |
| A03 | Security; đọc mã | X-Demo-Actor có thể giả, default actor dùng chung, audio public, không rate limit/auth/RBAC. Không public (T003/T004) |
| A04 | Deployment; đọc mã | Chỉ cấm env != demo; HOST hoặc ASGI CLI vẫn có thể bind public. README trước đó nói quá mức "only binds localhost"; đã sửa claim, chưa thêm enforcement |
| A05 | Narrative/storage; đọc schema/mã | Event append-only theo API, không trigger/privilege/hash chống sửa; state chưa pin edition; chưa replay/restore. Ghi PARTIAL thay vì immutable tuyệt đối (T003/T009) |
| A06 | Rights; code/test | verified_for_demo + action list chỉ demo; không kiểm hạn/territory/chain/reviewer/revoke. T002; không self-approve nội dung thật |
| A07 | Mobile recovery; đọc mã, chưa device tái hiện | `_choose` commit server rồi `_load` audio trước khi gán `_run`; audio lỗi có thể giữ version cũ; API không có get-run/reconciliation, timeout, persisted pending key. T001 foreground recovery, T005 lifecycle |
| A08 | Web errors; đọc mã, chưa browser tái hiện | catch trong choose đặt lỗi rồi render(current) ghi đè status; retry tạo key mới. Không khẳng định offline-safe. Regression test ở task client |
| A09 | Product gap; đối chiếu PRD | Chưa passive default route, full library/search/resume/background/offline, CMS, auth, payments hoặc AI orchestration. Không gọi prototype là B2C MVP |
| A10 | Documentation drift; đối chiếu | Start/test docs ghi 14 trong khi suite có 17; sửa. RELEASE_AUDIT cũ là lịch sử packaging. Đồng bộ dependency T003 với T002 và T001 client contract; ngày 2026-11-18 đồng bộ thêm drift giữa BACKLOG và task packets T003/T009/T011/T015/T016 |
| A11 | Legal/provenance; inventory | Manifest khai báo gốc/eSpeak và production_approval=false; không xác minh hợp đồng thương mại hay tái chứng minh nguồn bằng chất âm. Không có phê duyệt pháp lý/game/voice/store |

## 6. Thay đổi trong T000
- AGENTS, bootstrap, CONTRIBUTING, OWNER_DECISIONS, HANDOFF: lưu quyền commit/push thông thường đã cấp và đầy đủ giới hạn; báo cáo tiếng Việt tám mục; repository là bộ nhớ bàn giao.
- PROJECT_STATE/CURRENT_TASK/BACKLOG/SESSION_LOG, audit này và task T000/T001: trạng thái thật, dependencies, acceptance, bước kế tiếp. READMEs/start/index/test strategy/release audit/changelog sửa claim lỗi thời.
- Ba script chỉ tách statement cho Ruff; Ruff sắp thứ tự import trong bảy file. `.gitignore` thêm egg-info; `.gitattributes` giữ text LF và MP3 binary để hash ổn định giữa máy. Không đổi route/schema/logic truyện/rights/audio/Flutter; không tạo deployment, AI call hay nội dung mới.
- Manifest SHA256 được làm mới sau khi hoàn tất file candidate; không chạy package_release ra ngoài workspace. Hash không phải chữ ký hay legal attestation.

## 7. Roadmap và bước kế tiếp
R0 có baseline kiểm chứng và handoff; R1 chưa nghiệm thu mobile/security/rights. R2 AI/TTS/CMS vẫn PLANNED; R3–R4 public/commercial BLOCKED; R5 nghiên cứu DEFERRED. Không có thay đổi giai đoạn phát hành hoặc mở gate thương mại.

**Một nhiệm vụ ưu tiên:** T001 — Flutter Bootstrap & Device Validation, bắt đầu bằng kiểm tra/khôi phục toolchain. Acceptance: analyze + mocked widget tests + Android debug build đạt, emulator catalog/MP3/branch/ending/error paths có bằng chứng; debug-only HTTP; backend checks vẫn xanh; iOS chưa có macOS phải ghi chưa chạy. Exact next commands ở CURRENT_TASK. T002 là task local design độc lập nếu toolchain thực sự chưa thể khôi phục; không tự bắt đầu trong phiên audit này.
