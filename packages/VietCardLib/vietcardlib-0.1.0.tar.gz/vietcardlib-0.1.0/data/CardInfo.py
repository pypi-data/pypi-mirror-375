"""
Card Information Data Module
Contains predefined card types for Vietnamese identification and cards
"""

class CardSide:
    FRONT = "front"
    BACK = "back"
    UNKNOWN = "unknown"

class CardInfo:
    def __init__(self):
            self.CARD_INFO = [
                {
                "id": 0,
                "name": "Chứng Minh Nhân Dân 9 Số",
                "nameEn": "ID Card 9 Digits",
                "description": "Loại CMND truyền thống, từng được cấp cho công dân từ trước 2012. CMND 9 số có giá trị sử dụng đến hết ngày 31/12/2024 và sẽ không còn được dùng từ năm 2025.",
                "is_active": True,  # Expired after 2024
                "sides": [CardSide.FRONT],
                "templates": {
                    CardSide.FRONT: "templates/base/0_CMND.png"
                }
                },
                {
                "id": 1,
                "name": "Chứng Minh Nhân Dân 12 Số",
                "nameEn": "ID Card 12 Digits",
                "description": "Được áp dụng từ năm 2012 thay cho CMND 9 số, có mã vạch 2 chiều, ảnh in trực tiếp trên thẻ, thay vì dán như CMND 9 số. Cũng chỉ được sử dụng đến hết 31/12/2024.",
                "is_active": True,  # Expired after 2024
                "sides": [CardSide.FRONT],
                "templates": {
                    CardSide.FRONT: "templates/base/0_CMND_12.png"
                }
                },
                {
                "id": 2,
                "name": "Căn Cước Công Dân Mã Vạch",
                "nameEn": "Citizens Card with Barcode",
                "description": "Loại thẻ được cấp từ năm 2016, dùng thay cho CMND 12 số. Số căn cước công dân chính là số định danh cá nhân 12 số của công dân. Thẻ này được sử dụng đến hết thời hạn in trên thẻ và có thể được đổi sang thẻ Căn cước mới khi cần thiết.",
                "is_active": True,
                "sides": [CardSide.FRONT],
                "templates": {
                    CardSide.FRONT: "templates/base/0_CCCD.jpg"
                }
                },
                {
                "id": 3,
                "name": "Căn Cước Công Dân Gắn Chip",
                "nameEn": "Citizens Card with Chip",
                "description": "Được áp dụng chính thức từ năm 2021, thẻ gắn chip chứa đầy đủ các thông tin nhận dạng và cá nhân, bảo mật cao, tích hợp nhiều chức năng. Công dân cũng có thể sử dụng thẻ này cho các thủ tục hành chính và được giữ nguyên số định danh cá nhân khi cấp đổi.",
                "is_active": True,
                "sides": [CardSide.FRONT],
                "templates": {
                   CardSide.FRONT: "templates/base/0_CCCD_CHIP.jpg"
                }
                },
                {
                "id": 4,
                "name": "Thẻ Căn Cước (2024)",
                "nameEn": "Identity Card (2024)",
                "description": "Loại thẻ mới theo Luật Căn cước 2023, chính thức có hiệu lực từ 01/7/2024, thay thế thẻ Căn cước công dân. Thẻ in các thông tin cá nhân cơ bản và có thể tích hợp các dữ liệu như thẻ bảo hiểm y tế, sổ bảo hiểm xã hội, giấy phép lái xe, giấy khai sinh, giấy chứng nhận kết hôn.",
                "is_active": True,
                "sides": [CardSide.FRONT],
                "templates": {
                     CardSide.FRONT: "templates/base/0_CANCUOC.jpg"
                }
                }
            ]

    def get_card_by_id(self, card_id):
        """Get card information by ID"""
        for card in self.CARD_INFO:
            if card["id"] == card_id:
                return card
        return None

    def get_active_cards(self):
        """Get all active cards"""
        return [card for card in self.CARD_INFO if card["is_active"]]

    def get_card_names(self):
        """Get all card names in Vietnamese"""
        return [card["name"] for card in self.CARD_INFO]

    def get_card_names_en(self):
        """Get all card names in English"""
        return [card["nameEn"] for card in self.CARD_INFO]

    def get_card_sides(self, card_id):
        """Get available sides for a card"""
        card = self.get_card_by_id(card_id)
        return card["sides"] if card else []

    def validate_card_side(self, card_id, side):
        """Validate if a side exists for a card"""
        card_sides = self.get_card_sides(card_id)
        return side in card_sides

    def get_all_sides(self):
        """Get all possible card sides"""
        return [CardSide.FRONT, CardSide.BACK, CardSide.UNKNOWN]

    def get_template_path(self, card_id, side):
        """Get template image path for a specific card and side"""
        card = self.get_card_by_id(card_id)
        if card and "templates" in card:
            return card["templates"].get(side, None)
        return None

    def get_all_templates(self, card_id):
        """Get all template paths for a card"""
        card = self.get_card_by_id(card_id)
        return card.get("templates", {}) if card else {}

if __name__ == "__main__":
    card_info = CardInfo()
    print("Available Cards:")
    for card in card_info.get_active_cards():
        print(f"- {card['name']} ({card['nameEn']})")
        for side in card['sides']:
            template_path = card_info.get_template_path(card['id'], side)
            print(f"  - Side: {side}, Template: {template_path}")