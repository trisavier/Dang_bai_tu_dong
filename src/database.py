"""
src/database.py — Quản lý database JSON cho sản phẩm đã đăng
"""
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ProductDatabase:
    """Quản lý danh sách sản phẩm đã đăng bằng file JSON."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Tạo file nếu chưa tồn tại."""
        if not os.path.exists(self.db_path):
            self._write([])
            logger.info(f"Tạo database mới tại: {self.db_path}")

    def _read(self) -> List[Dict]:
        """Đọc toàn bộ database."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Lỗi đọc database, khởi tạo lại.")
            return []

    def _write(self, data: List[Dict]):
        """Ghi dữ liệu vào database."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[Dict]:
        """Lấy tất cả bản ghi."""
        return self._read()

    def get_posted_names(self) -> List[str]:
        """Lấy danh sách tên sản phẩm đã đăng."""
        return [p.get("name", "") for p in self._read()]

    def add(
        self,
        name: str,
        content: str,
        status: str = "success",
    ):
        """Thêm sản phẩm đã đăng vào database."""
        records = self._read()
        record = {
            "id": len(records) + 1,
            "name": name,
            "date": str(datetime.now().date()),
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": status,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "full_content": content,
        }
        records.append(record)
        self._write(records)
        logger.info(f"Đã lưu bài viết: {name}")
        return records

    def delete(self, record_id: int) -> bool:
        """Xoa mot bai viet theo ID."""
        records = self.get_all()
        initial_length = len(records)
        records = [r for r in records if r["id"] != record_id]
        
        if len(records) < initial_length:
            self._write(records)
            logger.info(f"Da xoa bai viet ID: {record_id}")
            return True
        return False

    def get_stats(self) -> Dict:
        """Thống kê tổng quát."""
        records = self._read()
        success = [r for r in records if r.get("status") == "success"]
        failed = [r for r in records if r.get("status") == "failed"]
        return {
            "total": len(records),
            "success": len(success),
            "failed": len(failed),
            "last_post": records[-1] if records else None,
        }

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Lấy các bài đăng gần đây nhất."""
        records = self._read()
        return list(reversed(records))[:limit]
