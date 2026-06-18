"""
config.py — Cấu hình tập trung cho toàn bộ dự án
"""
import os
from dotenv import load_dotenv

load_dotenv()

# === OPENROUTER API ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")

# === FACEBOOK API (DA GO BO) ===
# Du an chuyen sang che do tro ly viet bai.

# === THÔNG TIN CÔNG TY ===
COMPANY_NAME = os.getenv("COMPANY_NAME", "Công Ty Camera An Ninh")
COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "Địa chỉ công ty")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "contact@example.com")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "https://example.com")
COMPANY_HOTLINE = os.getenv("COMPANY_HOTLINE", "0900 000 000")
COMPANY_CITY = os.getenv("COMPANY_CITY", "Đà Nẵng")

COMPANY_INFO = """📞 LIÊN HỆ NGAY CAMERA VIỆT ĐỂ ĐƯỢC TƯ VẤN VÀ GIAO HÀNG TẬN NƠI:
🏢 CÔNG TY TNHH GPCN CAMERA VIỆT
📍 KĐT Làng Đại Học, TP. Đà Nẵng
📧 Email: kinhdoanh@camera-viet.vn
🌐 Website: www.camera-viet.vn
☎️ Hotline/Zalo: 0917.016.168 – 0972.880.506

🔖 #ImouCruiserSE #CameraImou #CameraWifi #CameraNgoaiTroi #Camera360 #Camera4MP #CameraAnNinh #CameraViet #CameraDaNang"""

# === CẤU HÌNH BOT ===
POST_TIME = os.getenv("POST_TIME", "06:00")
PRODUCTS_URL = os.getenv("PRODUCTS_URL", "https://kabegroup.vn/kabet/san-pham/")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "5000"))

# === ĐƯỜNG DẪN FILE ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "posted_products.json")
LOG_FILE = os.path.join(DATA_DIR, "bot.log")
