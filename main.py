"""
main.py — Entry point chính của bot Camera Post Automation
"""
import argparse
import logging
import os
import sys

# Fix Unicode/emoji tren Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Them thu muc goc vao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.database import ProductDatabase
from src.scraper import ProductScraper
from src.generator import PostGenerator
from src.scheduler import BotScheduler

# ========================
# CẤU HÌNH LOGGING
# ========================
os.makedirs(config.DATA_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("CameraBot")


# ========================
# KHỞI TẠO COMPONENTS
# ========================
db = ProductDatabase(config.PRODUCTS_FILE)
scraper = ProductScraper(config.PRODUCTS_URL)
generator = PostGenerator(
    api_key=config.GEMINI_API_KEY,
    model=config.GEMINI_MODEL,
    company_info=config.COMPANY_INFO,
    city=config.COMPANY_CITY,
)


def daily_job():
    """
    Job chinh: crawl san pham -> sinh bai -> luu DB.
    """
    logger.info("=" * 60)
    logger.info("[BOT] BAT DAU JOB SOAN BAI TU DONG")
    logger.info("=" * 60)

    # 1. Lay danh sach san pham da dang
    posted_names = db.get_posted_names()
    logger.info("Da dang %d san pham truoc do.", len(posted_names))

    # 2. Crawl san pham chua dang
    logger.info("Dang crawl san pham moi tu website...")
    product = scraper.get_available_product(posted_names)

    if not product:
        logger.warning("Khong tim thay san pham moi! Bot dung lai.")
        return

    logger.info("Da chon san pham: %s", product['name'])

    # 3. Sinh bai viet bang Gemini AI
    logger.info("Dang sinh bai viet bang Gemini AI...")
    try:
        product_name, post_content = generator.generate(product, posted_names)
    except Exception as e:
        logger.error("Loi sinh bai viet: %s", e, exc_info=True)
        return

    logger.info("Bai viet sinh xong (%d ky tu).", len(post_content))

    # 4. Luu vao database
    db.add(
        name=product_name,
        content=post_content,
        status="success",
    )
    logger.info("HOAN THANH! Da luu bai viet: '%s' vao he thong", product_name)

    logger.info("=" * 60)


def check_config():
    """Kiem tra cau hinh co day du khong."""
    errors = []
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "":
        errors.append("[LOI] GEMINI_API_KEY chua duoc cau hinh trong .env")

    if errors:
        for e in errors:
            print(e)
        if any("[LOI]" in e for e in errors):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="🎥 Camera Post Automation Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python main.py                    # Chạy bot tự động hàng ngày
  python main.py --run-now          # Chay tao bai ngay lap tuc
  python main.py --dashboard        # Mở web dashboard
  python main.py --check            # Kiểm tra cấu hình
  python main.py --list             # Xem danh sách đã đăng
        """,
    )
    parser.add_argument("--run-now", action="store_true", help="Chạy đăng bài ngay lập tức")
    parser.add_argument("--dashboard", action="store_true", help="Mở web dashboard quản lý")
    parser.add_argument("--check", action="store_true", help="Kiểm tra cấu hình")
    parser.add_argument("--list", action="store_true", help="Liệt kê sản phẩm đã đăng")
    parser.add_argument("--time", default=config.POST_TIME, help="Giờ đăng bài (HH:MM, mặc định: 06:00)")

    args = parser.parse_args()

    print("=" * 50)
    print("  Camera Post Automation Bot (Gemini AI)")
    print("=" * 50)

    # Kiểm tra cấu hình
    if args.check:
        ok = check_config()
        if ok:
            print("[OK] Cau hinh hop le!")
        return

    # Liệt kê sản phẩm đã đăng
    if args.list:
        stats = db.get_stats()
        print(f"\nThong ke: {stats['total']} tong, {stats['success']} thanh cong, {stats['failed']} that bai")
        recent = db.get_recent(20)
        if recent:
            print("\n20 bai gan nhat:")
            for i, r in enumerate(recent, 1):
                status_icon = "[OK]" if r["status"] == "success" else "[LOI]"
                print(f"  {i:2}. {status_icon} [{r['date']}] {r['name']}")
        else:
            print("Chua co bai nao duoc dang.")
        return

    # Chạy ngay lập tức
    if args.run_now:
        if not check_config():
            sys.exit(1)
        daily_job()
        return

    # Mở dashboard
    if args.dashboard:
        from web.app import create_app
        app = create_app(db, scraper, generator)
        print(f"\n🌐 Dashboard: http://localhost:{config.DASHBOARD_PORT}")
        app.run(host="0.0.0.0", port=config.DASHBOARD_PORT, debug=False)
        return

    # Chạy scheduler (mặc định)
    if not check_config():
        sys.exit(1)

    post_time = args.time
    scheduler = BotScheduler(job_func=daily_job, post_time=post_time)
    scheduler.setup()

    print(f"\nBot se dang bai luc {post_time} moi ngay.")
    print("   Chay 'py -3.11 main.py --run-now' de test ngay.\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nBot da dung.")


if __name__ == "__main__":
    main()
