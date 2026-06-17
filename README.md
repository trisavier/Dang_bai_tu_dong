# 🎥 Camera Post Automation Bot

Bot tự động đăng bài Facebook giới thiệu sản phẩm camera an ninh từ [kabegroup.vn](https://kabegroup.vn/kabet/san-pham/).

---

## 📦 Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.9+
- pip

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường

Copy file mẫu và điền thông tin:

```bash
copy .env.example .env
```

Mở `.env` và điền đầy đủ:

| Biến | Mô tả |
|------|-------|
| `CLAUDE_API_KEY` | API key từ [console.anthropic.com](https://console.anthropic.com) |
| `FB_ACCESS_TOKEN` | Facebook User/Page Access Token |
| `FB_ALLOWED_USER_IDS` | ID của những người được xem bài (cách nhau bởi dấu phẩy) |
| `COMPANY_NAME` | Tên công ty của bạn |
| `COMPANY_ADDRESS` | Địa chỉ công ty |
| `COMPANY_EMAIL` | Email liên hệ |
| `COMPANY_WEBSITE` | Website công ty |
| `COMPANY_HOTLINE` | Số điện thoại |
| `COMPANY_CITY` | Thành phố (dùng cho hashtag) |
| `POST_TIME` | Giờ đăng bài mỗi ngày (VD: `06:00`) |

---

## 🚀 Sử dụng

### Kiểm tra cấu hình
```bash
python main.py --check
```

### Đăng bài thử ngay
```bash
python main.py --run-now
```

### Chạy bot tự động (lên lịch hàng ngày)
```bash
python main.py
```

### Chạy với giờ tùy chỉnh
```bash
python main.py --time 08:30
```

### Mở Web Dashboard
```bash
python main.py --dashboard
```
Sau đó truy cập: http://localhost:5000

### Xem danh sách bài đã đăng
```bash
python main.py --list
```

---

## 🌐 Web Dashboard

Dashboard tại `http://localhost:5000` cho phép bạn:

- 📊 Xem thống kê tổng bài đăng, thành công/thất bại
- ▶️ Đăng bài ngay lập tức bằng 1 nút bấm
- 🔑 Kiểm tra Facebook token còn hợp lệ không
- 📋 Xem lịch sử đầy đủ và nội dung từng bài
- 📋 Copy nội dung bài để dùng thủ công

---

## 📁 Cấu trúc dự án

```
Dự án tự động/
├── src/
│   ├── scraper.py      # Crawl sản phẩm từ kabegroup.vn
│   ├── generator.py    # Sinh bài viết bằng Claude AI
│   ├── facebook.py     # Đăng bài lên Facebook API
│   ├── scheduler.py    # Lên lịch hàng ngày
│   └── database.py     # Lưu trữ dữ liệu JSON
├── web/
│   ├── app.py          # Flask Dashboard
│   ├── templates/
│   │   └── index.html
│   └── static/
│       └── style.css
├── data/               # Tự tạo khi chạy
│   ├── posted_products.json
│   └── bot.log
├── config.py           # Cấu hình tập trung
├── main.py             # Entry point
├── requirements.txt
├── .env.example        # Mẫu cấu hình
└── .env                # Cấu hình thực (tự tạo)
```

---

## 🔑 Lấy Facebook Access Token

1. Vào [Facebook Developers](https://developers.facebook.com/)
2. Tạo app → Thêm sản phẩm **Facebook Login**
3. Vào **Tools → Graph API Explorer**
4. Chọn app → Generate Access Token
5. Cần quyền: `publish_actions`, `pages_manage_posts` (nếu đăng lên Page)

### Lấy User ID để giới hạn người xem
```
https://graph.facebook.com/v18.0/{username}?access_token={token}
```

---

## ⚠️ Lưu ý

- **Privacy CUSTOM**: Chỉ hoạt động với `User Access Token` cá nhân, không phải Page Token.
- Token Facebook có thể hết hạn sau 60 ngày — cần gia hạn định kỳ.
- Tôn trọng [Facebook Platform Policy](https://developers.facebook.com/policy/) khi sử dụng API.
- Đảm bảo chỉ đăng thông tin thực tế từ website — không bịa thêm thông số.

---

## 🛠️ Khắc phục sự cố

| Vấn đề | Giải pháp |
|--------|-----------|
| `❌ CLAUDE_API_KEY chưa cấu hình` | Điền API key vào file `.env` |
| `❌ Token không hợp lệ` | Lấy lại token mới trên Facebook Developers |
| `Không tìm thấy sản phẩm mới` | Tất cả sản phẩm đã được đăng. Xóa bớt trong `posted_products.json` |
| Crawl website thất bại | Kiểm tra kết nối internet và URL trong `.env` |

---

Được tạo tự động bởi **Antigravity AI** 🤖
