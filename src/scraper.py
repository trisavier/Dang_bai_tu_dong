"""
src/scraper.py — Crawl danh sách sản phẩm camera từ kabegroup.vn
"""
import random
import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}


class ProductScraper:
    """Crawl thông tin sản phẩm từ kabegroup.vn."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_product_list(self) -> List[Dict]:
        """Lấy danh sách sản phẩm từ trang chính."""
        products = []
        page = 1

        while True:
            url = self.base_url if page == 1 else f"{self.base_url}page/{page}/"
            logger.info(f"Đang crawl trang {page}: {url}")

            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Lỗi kết nối trang {page}: {e}")
                break

            soup = BeautifulSoup(resp.text, "lxml")

            # Tìm các item sản phẩm (selector cho kabegroup.vn)
            items = soup.select(".product-item, .product, article.product, li.product")
            if not items:
                # Thử selector rộng hơn
                items = soup.select("[class*='product']")

            if not items:
                logger.info(f"Không tìm thấy sản phẩm ở trang {page}, dừng lại.")
                break

            for item in items:
                name_tag = item.select_one("h2, h3, .product-title, .woocommerce-loop-product__title")
                link_tag = item.select_one("a[href]")

                if name_tag and link_tag:
                    name = name_tag.get_text(strip=True)
                    link = urljoin(self.base_url, link_tag["href"])
                    products.append({"name": name, "url": link})

            # Kiểm tra có trang tiếp theo không
            next_page = soup.select_one("a.next, .next-page, [rel='next']")
            if not next_page:
                break
            page += 1

        logger.info(f"Tổng cộng crawl được {len(products)} sản phẩm.")
        return products

    def get_product_detail(self, url: str) -> Optional[Dict]:
        """Lấy thông tin chi tiết của một sản phẩm."""
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Lỗi lấy chi tiết sản phẩm {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        # Tên sản phẩm
        name = ""
        name_tag = soup.select_one("h1.product-title, h1.entry-title, h1")
        if name_tag:
            name = name_tag.get_text(strip=True)

        # Mô tả ngắn
        short_desc = ""
        desc_tag = soup.select_one(".woocommerce-product-details__short-description, .short-description")
        if desc_tag:
            short_desc = desc_tag.get_text(separator="\n", strip=True)

        # Mô tả đầy đủ / thông số kỹ thuật
        full_desc = ""
        full_tag = soup.select_one(
            "#tab-description, .woocommerce-Tabs-panel--description, "
            ".product-description, .description, .tab-content"
        )
        if full_tag:
            full_desc = full_tag.get_text(separator="\n", strip=True)

        # Lấy thông số kỹ thuật dạng bảng
        specs = {}
        tables = soup.select("table")
        for table in tables:
            rows = table.select("tr")
            for row in rows:
                cells = row.select("td, th")
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    val = cells[1].get_text(strip=True)
                    if key:
                        specs[key] = val

        return {
            "name": name,
            "url": url,
            "short_description": short_desc,
            "full_description": full_desc,
            "specs": specs,
        }

    def get_available_product(self, posted_names: List[str]) -> Optional[Dict]:
        """
        Lấy NGẪU NHIÊN một sản phẩm chưa được đăng.
        Trả về thông tin chi tiết của sản phẩm đó.
        """
        products = self.get_product_list()
        posted_lower = [n.lower() for n in posted_names]

        # Loc danh sach cac san pham chua dang
        available_products = [p for p in products if p["name"].lower() not in posted_lower]

        if not available_products:
            logger.warning("Không còn sản phẩm mới để đăng!")
            return None

        # Chon ngau nhien
        selected = random.choice(available_products)
        logger.info(f"Chọn ngẫu nhiên sản phẩm mới: {selected['name']}")
        
        detail = self.get_product_detail(selected["url"])
        if detail:
            return detail
            
        # Nếu không lấy được chi tiết, dùng thông tin cơ bản
        return {"name": selected["name"], "url": selected["url"],
                "short_description": "", "full_description": "", "specs": {}}
