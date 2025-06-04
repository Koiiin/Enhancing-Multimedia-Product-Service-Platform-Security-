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
