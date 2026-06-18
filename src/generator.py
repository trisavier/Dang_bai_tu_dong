"""
src/generator.py — Sinh bài viết Facebook bằng OpenRouter API
"""
import logging
from typing import Dict, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Bạn là chuyên gia viết nội dung marketing cho sản phẩm camera an ninh tại Việt Nam.
Nhiệm vụ của bạn là viết một bài đăng Facebook giới thiệu sản phẩm camera từ thông tin sản phẩm được cung cấp.

=== QUY TẮc BẮT BUỘC (KHÔNG ĐƯỢC VI PHẠM) ===
1. GIỮ NGUYÊN 100% tên sản phẩm gốc (mã model) — KHÔNG thêm bớt hay thay đổi.
2. PHẢI viết ĐẦY ĐỦ TẤT CẢ 9 mục theo đúng thứ tự, KHÔNG bỏ sót bất kỳ mục nào.
3. KHÔNG dùng dấu ** để bôi đậm tiêu đề.
4. Giữa mỗi mục PHẢI có 1 dòng trống.
5. KHÔNG bịa thêm thông số kỹ thuật ngoài thông tin được cung cấp.
6. Nếu thông tin một mục không có, hãy suy luận hợp lý từ loại camera và tính năng — KHÔNG bỏ qua mục đó.
7. Mỗi bullet point PHẢI viết ĐẦY ĐỦ thành 1-2 câu hoàn chỉnh, giải thích lợi ích cụ thể — KHÔNG liệt kê khô khan.
8. Kết thúc bài viết sau mục 🏠 Phù hợp lắp đặt cho là XONG. KHÔNG được tự thêm phần liên hệ, hashtag hay bất kỳ nội dung nào khác.

=== CẤU TRÚC BÀI VIẾT (PHẢI TUÂN THỦ CHÍNH XÁC) ===

[Viết 1-2 đoạn mở bài thật hấp dẫn, nêu vấn đề khách hàng gặp phải và giới thiệu giải pháp là sản phẩm camera này]

🆎 Tên sản phẩm: [GIỮ NGUYÊN TÊN GỐC]

🔍 Chất lượng hình ảnh:
* [bullet 1 — viết 1-2 câu mô tả độ phân giải + lợi ích cho người dùng]
* [bullet 2 — cảm biến và khả năng chụp chi tiết]
* [bullet 3 — chuẩn nén và lợi ích tiết kiệm lưu trữ]
* [bullet 4 — đặc điểm khác nếu có]

🌙 Tầm nhìn ban đêm thông minh:
* [bullet 1 — các chế độ ban đêm và công nghệ hỗ trợ]
* [bullet 2 — tầm xa hồng ngoại cụ thể, giải thích ý nghĩa]
* [bullet 3 — Color Night Vision hoặc đèn trợ sáng nếu có]

🤖 Tính năng thông minh:
* [bullet 1 — AI Detection, giải thích nhận biết gì và lợi ích]
* [bullet 2 — Smart Tracking, giải thích cách hoạt động]
* [bullet 3 — cảnh báo đẩy qua app, mô tả trải nghiệm người dùng]
* [bullet 4 — các tính năng AI khác nếu có]

🎙️ Âm thanh & giám sát:
* [bullet 1 — Micro/loa tích hợp và chất lượng âm thanh]
* [bullet 2 — ứng dụng xem từ xa, mô tả tiện lợi cho người dùng]
* [bullet 3 — tính năng âm thanh khác nếu có]

🔄 Khả năng quay quét linh hoạt:
* [Nếu có PTZ: mô tả góc Pan/Tilt cụ thể và phạm vi bao quát. Nếu cố định: “Camera cố định, góc nhìn rộng [X]°, phù hợp giám sát điểm cố định.”]

💪 Thiết kế & độ bền:
* [bullet 1 — chuẩn IP và khả năng chống chịu thời tiết]
* [bullet 2 — vật liệu vỏ, độ bền]
* [bullet 3 — nhiệt độ hoạt động]

📡 Kết nối & lưu trữ:
* [bullet 1 — WiFi/LAN, giải thích tính năng kết nối]
* [bullet 2 — thẻ nhớ, Cloud, dung lượng tối đa]
* [bullet 3 — tương thích NVR/DVR nếu có]

🔌 Thông số kỹ thuật cơ bản:
* Độ phân giải: [...]
* Ống kính: [...]
* Tầm xa hồng ngoại: [...]
* Chuẩn nén: [...]
* Kết nối: [...]
* Nguồn điện: [...]

✨ Lợi ích nổi bật:
✅ [Lợi ích 1]
✅ [Lợi ích 2]
✅ [Lợi ích 3]
✅ [Lợi ích 4]
✅ [Lợi ích 5]
✅ [Lợi ích 6]
✅ [Lợi ích 7]

🏠 Phù hợp lắp đặt cho:
[Liệt kê các địa điểm phù hợp trong 1 đoạn văn ngắn: nhà ở, cửa hàng, văn phòng, kho hàng, v.v.]"""


class PostGenerator:
    """Sinh bài viết Facebook bằng OpenRouter API."""

    def __init__(self, api_key: str, model: str, company_info: str, city: str):
        self.api_key = api_key
        self.model_name = model
        self.company_info = company_info
        self.city = city

    def _call_openrouter(self, user_prompt: str, max_tokens: int = 8000) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _build_user_prompt(self, product: Dict, posted_names: list) -> str:
        """Tao user prompt voi thong tin san pham."""
        specs_text = ""
        if product.get("specs"):
            specs_lines = [f"  - {k}: {v}" for k, v in product["specs"].items()]
            specs_text = "\n".join(specs_lines)

        return f"""Hay viet bai dang Facebook cho san pham camera sau:

Ten san pham: {product.get('name', 'N/A')}
URL: {product.get('url', '')}

Mo ta ngan:
{product.get('short_description', 'Khong co thong tin')}

Thong tin chi tiet:
{product.get('full_description', 'Khong co thong tin')}

Thong so ky thuat:
{specs_text if specs_text else 'Khong co thong so cu the'}

Thanh pho: {self.city}

San pham da dang roi (KHONG duoc chon lai):
{', '.join(posted_names) if posted_names else 'Chua co'}

Yeu cau:
1. Neu trong bai co the hien ten san pham thi phai dung nguyen van: {product.get('name', 'N/A')}
2. Viet bai theo dung cau truc trong SYSTEM_PROMPT, tieng Viet co dau, dung emoji.
3. Ket thuc sau muc 🏠, KHONG them lien he, hashtag hay noi dung nao khac.
"""

    def generate(self, product: Dict, posted_names: list) -> Tuple[str, str]:
        """
        Sinh bai viet cho san pham.
        Tra ve (ten_san_pham, noi_dung_bai_viet).
        """
        user_prompt = self._build_user_prompt(product, posted_names)
        logger.info("Dang sinh bai viet cho: %s (model: %s)", product.get('name', 'unknown'), self.model_name)

        full_text = self._call_openrouter(user_prompt, max_tokens=8000).strip()
        lines = full_text.split("\n")

        product_name = product.get("name", "Unknown")
        post_content_lines = []

        if lines and lines[0].startswith("PRODUCT_NAME:"):
            lines = lines[1:]

        heading_emojis = ["🆎", "🔍", "🌙", "🤖", "🎙️", "🔄", "💪", "📡", "🔌", "✨", "🏠"]
        for line in lines:
            cleaned_line = line.strip().replace("**", "")
            # Bo qua cac dong trong lien tiep
            if not cleaned_line:
                if post_content_lines and post_content_lines[-1] != "":
                    post_content_lines.append("")
                continue
            
            # Them dong trong truoc cac tieu de
            if any(cleaned_line.startswith(e) for e in heading_emojis):
                if post_content_lines and post_content_lines[-1] != "":
                    post_content_lines.append("")
            
            post_content_lines.append(cleaned_line)

        # Append company info manually at the end
        post_content_lines.append("")
        post_content_lines.append("--------------------")
        post_content_lines.append(self.company_info)

        post_content = "\n".join(post_content_lines).strip()
        logger.info("Sinh bai viet thanh cong: %d ky tu", len(post_content))
        return product_name, post_content

    def generate_from_url(
        self, product_url: str, posted_names: list, company_info: Optional[str] = None
    ) -> Tuple[str, str]:
        """Sinh bai viet tu URL san pham."""
        ci = company_info or self.company_info
        posted_str = ", ".join(posted_names) if posted_names else "Chua co"

        prompt = f"""Dua tren thong tin san pham camera tai trang {product_url}, viet bai dang Facebook theo dung dinh dang da yeu cau (tieng Viet co dau, dung emoji).

San pham da dang roi (KHONG duoc chon lai): {posted_str}

QUAN TRONG: Dong dau tien cua response phai la:
PRODUCT_NAME: [ten san pham]
Sau do moi la noi dung bai viet."""

        full_text = self._call_openrouter(prompt, max_tokens=2500).strip()
        lines = full_text.split("\n")

        product_name = "Unknown"
        post_content_lines = lines

        if lines and lines[0].startswith("PRODUCT_NAME:"):
            product_name = lines[0].replace("PRODUCT_NAME:", "").strip()
            post_content_lines = lines[1:]

        post_content = "\n".join(post_content_lines).strip()
        return product_name, post_content
