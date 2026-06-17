"""
web/app.py — Flask Web Dashboard để quản lý bot
"""
import os
import sys
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

# Bot scheduler instance toàn cục (được khởi tạo từ ngoài)
_scheduler = None
_is_job_running = False


def create_app(db, scraper, generator):
    """Tao Flask app voi cac dependencies duoc inject vao."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.urandom(24)

    import config

    def run_job_background(db, scraper, generator):
        """Chay job tao bai trong thread rieng."""
        global _is_job_running
        _is_job_running = True
        try:
            posted_names = db.get_posted_names()
            product = scraper.get_available_product(posted_names)
            if not product:
                logger.warning("Khong tim thay san pham moi!")
                return

            product_name, post_content = generator.generate(product, posted_names)

            db.add(
                name=product_name,
                content=post_content,
                status="success",
            )
        except Exception as e:
            logger.error(f"Loi job: {e}", exc_info=True)
        finally:
            _is_job_running = False

    # ========================
    # ROUTES
    # ========================

    @app.route("/")
    def index():
        stats = db.get_stats()
        recent = db.get_recent(20)
        return render_template(
            "index.html",
            stats=stats,
            recent=recent,
            post_time=config.POST_TIME,
            company_name=config.COMPANY_NAME,
            is_job_running=_is_job_running,
            products_url=config.PRODUCTS_URL,
        )

    @app.route("/api/stats")
    def api_stats():
        stats = db.get_stats()
        return jsonify(stats)

    @app.route("/api/posts")
    def api_posts():
        limit = int(request.args.get("limit", 20))
        posts = db.get_recent(limit)
        return jsonify(posts)

    @app.route("/api/post/<int:post_id>")
    def api_post_detail(post_id):
        all_posts = db.get_all()
        post = next((p for p in all_posts if p.get("id") == post_id), None)
        if post:
            return jsonify(post)
        return jsonify({"error": "Không tìm thấy bài"}), 404

    @app.route("/api/run-now", methods=["POST"])
    def api_run_now():
        global _is_job_running
        if _is_job_running:
            return jsonify({"success": False, "message": "Bot dang chay roi, vui long cho..."}), 409

        thread = threading.Thread(
            target=run_job_background,
            args=(db, scraper, generator),
            daemon=True,
        )
        thread.start()
        return jsonify({"success": True, "message": "✅ Da bat dau tao bai viet moi! Kiem tra log de theo doi."})

    @app.route("/api/status")
    def api_status():
        return jsonify({
            "is_running": _is_job_running,
            "total_posts": db.get_stats()["total"],
            "timestamp": datetime.now().isoformat(),
        })

    @app.route("/api/posts/<int:post_id>", methods=["DELETE"])
    def api_delete_post(post_id):
        success = db.delete(post_id)
        if success:
            return jsonify({"success": True, "message": "Da xoa bai viet thanh cong!"})
        return jsonify({"success": False, "message": "Khong tim thay bai viet!"}), 404

    return app


if __name__ == "__main__":
    # Chạy standalone (chủ yếu dùng từ main.py)
    import config
    from src.database import ProductDatabase
    from src.scraper import ProductScraper
    generator = PostGenerator(config.GEMINI_API_KEY, config.GEMINI_MODEL, config.COMPANY_INFO, config.COMPANY_CITY)

    app = create_app(db, scraper, generator)
    app.run(host="0.0.0.0", port=config.DASHBOARD_PORT, debug=True)
