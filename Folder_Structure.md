project/
│
├── app.py                       # Điểm khởi chạy Flask App
├── config.py                    # Cấu hình chung (DB, thư mục upload,...)
├── master_key.key               # (Sinh một lần) chứa KEK mã hóa DEK
│
├── templates/                   # HTML Templates cho UI
│   ├── index.html               # Trang chính
│   ├── upload.html              # Trang upload video
│   └── watch.html               # Trang xem video
│
├── static/                      # File tĩnh: CSS, JS
│
├── models.py                   # Định nghĩa các bảng: User, Video,...
├── db.py                        # SQLAlchemy init
│
├── utils/                       # Các công cụ mã hóa, sinh key
│   ├── aes_crypto.py            # AES mã hóa/giải mã file
│   ├── chaotic_cipher.py        # Truyền video bằng chaotic cipher
│   ├── crypto_utils.py          # Xử lý base64, session key, mở rộng
│   └── key_utils.py             # Sinh và mã hóa DEK bằng KEK
│
├── routes/                      # Các blueprint xử lý logic
│   ├── __init__.py
│   ├── main.py                  # index, upload, xem video
│   ├── auth.py                  # Đăng ký, đăng nhập, logout
│   ├── api.py                   # API phụ trợ nếu cần (REST JSON, v.v.)
│   └── admin.py                 # Quản lý video, xóa, logs (chỉ admin)
│
├── uploads/                     # File upload tạm trước khi mã hóa (sẽ xóa)
├── encrypted_videos/           # File đã mã hóa AES (enc_abc.mp4.enc)
├── temp/                        # File giải mã tạm thời khi xem video
└── logs/                        # (tuỳ chọn) Log audit hệ thống

--------------------------------------------------------------------------
--------------------------------CHECK LIST--------------------------------

✅ I. Data and Information Assets – Checklist
1. Bổ sung MFA (Multi-Factor Authentication)
 Tích hợp thư viện Flask-TwoFactor hoặc Flask-Security.

 Tạo QR code OTP bằng PyOTP (Google Authenticator).

 Thêm cột mfa_enabled, mfa_secret vào bảng User.

 Giao diện kích hoạt MFA trong profile.

 Bắt buộc xác minh OTP khi login nếu mfa_enabled=True.

2. Tạo hệ thống Viewing History / Watchlist / Rating
 Tạo bảng ViewingHistory(user_id, video_id, timestamp).

 Tạo bảng Watchlist(user_id, video_id).

 Tạo bảng Rating(user_id, video_id, score, comment).

 Tích hợp các chức năng này vào giao diện người dùng.

 Tùy chọn: thêm biểu đồ phân tích lịch sử xem.

3. Mở rộng metadata của video
 Thêm cột description, tags, subtitles_path, duration vào bảng Video.

 Thêm form nhập mô tả/tags khi upload.

 Cập nhật template index.html để hiển thị metadata.

4. Cải thiện Logging / Audit trail
 Dùng Flask Signals hoặc decorator ghi log cho các hành động: login, xem video, upload, xóa.

 Ghi lại IP, user-agent, thời gian.

 Định dạng log rõ ràng, lưu thành file audit.log riêng.

5. Tích hợp quản lý hợp đồng / royalty
 Tạo bảng Contract(provider_id, terms, revenue_share, signed_date).

 Cho phép admin tạo hợp đồng, liên kết với content provider.

 Giao diện xem thống kê tổng số video và lượt xem theo nhà cung cấp.

6. Triển khai Key Management cơ bản
 Tách lưu KEK (Fernet key) vào thư mục bảo mật, chỉ đọc được bởi root (nếu local).

 Ghi log mỗi khi có hành động giải mã DEK.

 Bổ sung module rotate_kek.py để xoay vòng KEK và re-encrypt các DEK cũ.

🖥️ II. Systems and Devices – Checklist
1. Triển khai HTTPS và Reverse Proxy
 Cấu hình Flask chạy qua Gunicorn + Nginx.

 Dùng Let's Encrypt để lấy TLS cert miễn phí.

 Redirect HTTP → HTTPS trong Nginx.

2. Triển khai CI/CD và kiểm tra bảo mật mã nguồn
 Tạo GitHub Action:

bandit (kiểm tra mã Python)

safety hoặc pip-audit (kiểm tra dependency)

 Push mã lên GitHub riêng (nếu chưa).

 Gửi báo cáo CI qua email / Slack.

3. Đóng gói hệ thống bằng Docker
 Viết Dockerfile cho Flask app.

 Viết docker-compose.yml chạy Flask + PostgreSQL + Redis (nếu cần).

 Định nghĩa biến môi trường qua .env.

🌐 III. Intangible Assets – Checklist
1. Tăng cường bảo vệ Privacy
 Hiển thị pop-up Cookie Consent nếu có web frontend.

 Cấu hình session cookie:

secure=True, httponly=True, samesite='Lax'

 Auto logout sau X phút không hoạt động (Flask-Session).

2. Tạo trang Privacy Policy và Terms of Use
 Tạo file privacy.html và terms.html.

 Thêm link footer trên mọi trang.

3. Xây dựng kịch bản xử lý sự cố (Incident Response)
 Ghi nhận lỗi nghiêm trọng vào incident.log.

 Gửi email đến admin nếu có lỗi 500, giải mã thất bại, bất thường.

 Tạo giao diện admin xem log lỗi theo ngày.

4. Bảo vệ mã nguồn và nội dung độc quyền
 Nếu public demo: tách phần chaotic cipher ra thành utils/experimental/ để rõ mục đích nghiên cứu.

 Thêm license (MIT, GPL, hoặc custom).

 Cân nhắc dùng PyArmor hoặc Nuitka để đóng gói nếu muốn phát hành thực tế.
