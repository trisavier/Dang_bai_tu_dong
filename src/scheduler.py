"""
src/scheduler.py — Lên lịch đăng bài tự động hàng ngày
"""
import logging
import schedule
import time
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)


class BotScheduler:
    """Quản lý lịch chạy tự động cho bot đăng bài."""

    def __init__(self, job_func: Callable, post_time: str = "06:00"):
        """
        Args:
            job_func: Hàm thực thi khi đến giờ đăng bài
            post_time: Giờ đăng bài định dạng "HH:MM"
        """
        self.job_func = job_func
        self.post_time = post_time
        self._is_running = False

    def setup(self):
        """Cấu hình lịch chạy."""
        schedule.clear()
        schedule.every().day.at(self.post_time).do(self._run_job)
        logger.info(f"✅ Đã lên lịch đăng bài lúc {self.post_time} mỗi ngày.")

    def _run_job(self):
        """Wrapper để bắt lỗi khi chạy job."""
        logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Bắt đầu job đăng bài...")
        try:
            self.job_func()
        except Exception as e:
            logger.error(f"❌ Lỗi khi chạy job: {e}", exc_info=True)

    def run_now(self):
        """Chạy job ngay lập tức (không chờ đến giờ lên lịch)."""
        logger.info("▶️  Chạy job ngay lập tức...")
        self._run_job()

    def start(self):
        """Bắt đầu vòng lặp chờ lịch."""
        self._is_running = True
        logger.info(f"🚀 Bot đang chạy, đăng bài lúc {self.post_time} mỗi ngày.")
        logger.info("   Nhấn Ctrl+C để dừng.\n")

        while self._is_running:
            schedule.run_pending()
            time.sleep(30)  # Kiểm tra mỗi 30 giây

    def stop(self):
        """Dừng vòng lặp."""
        self._is_running = False
        schedule.clear()
        logger.info("🛑 Bot đã dừng.")

    def get_next_run(self) -> str:
        """Lấy thời gian chạy tiếp theo."""
        jobs = schedule.jobs
        if jobs:
            next_run = jobs[0].next_run
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
        return "Chưa lên lịch"

    def get_status(self) -> dict:
        """Lấy trạng thái hiện tại của scheduler."""
        return {
            "is_running": self._is_running,
            "post_time": self.post_time,
            "next_run": self.get_next_run(),
            "jobs_count": len(schedule.jobs),
        }
