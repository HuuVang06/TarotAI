"""
test_tarot.py - Bộ kiểm thử tự động toàn diện cho hệ thống Tarot.
Kiểm tra cấu trúc 78 lá, Fisher-Yates shuffle, Spreads logic và Prompt generation.
"""

import unittest
from tarot_engine import (
    build_full_deck,
    shuffle_deck,
    SPREAD_CONFIGS,
    generate_ai_prompt,
    MAJOR_ARCANA_RAW,
    SUITS_META,
    RANKS_META
)


class TestTarotEngine(unittest.TestCase):

    def setUp(self):
        """Khởi tạo deck cơ bản trước mỗi test case."""
        self.deck = build_full_deck()

    def test_deck_total_count(self):
        """Kiểm tra tổng số lượng lá bài phải chính xác là 78."""
        self.assertEqual(len(self.deck), 78, "Bộ bài Tarot bắt buộc phải có đủ 78 lá.")

    def test_major_arcana_composition(self):
        """Kiểm tra 22 lá Ẩn chính (Major Arcana)."""
        major_cards = [c for c in self.deck if c["type"] == "Major"]
        self.assertEqual(len(major_cards), 22, "Ẩn chính phải có đúng 22 lá.")
        self.assertEqual(len(MAJOR_ARCANA_RAW), 22)

    def test_minor_arcana_composition(self):
        """Kiểm tra 56 lá Ẩn phụ chia đều cho 4 bộ (Wands, Cups, Swords, Pentacles)."""
        minor_cards = [c for c in self.deck if c["type"] == "Minor"]
        self.assertEqual(len(minor_cards), 56, "Ẩn phụ phải có đúng 56 lá.")

        for suit in ["Wands", "Cups", "Swords", "Pentacles"]:
            suit_cards = [c for c in minor_cards if c["suit"] == suit]
            self.assertEqual(len(suit_cards), 14, f"Mỗi chất {suit} phải có đúng 14 lá bài.")

    def test_unique_card_ids_and_names(self):
        """Đảm bảo không có lá bài nào bị trùng lặp ID hoặc tên."""
        ids = [c["id"] for c in self.deck]
        self.assertEqual(len(ids), len(set(ids)), "Mỗi lá bài phải có ID duy nhất.")

        names = [c["name"] for c in self.deck]
        self.assertEqual(len(names), len(set(names)), "Tên tiếng Anh của 78 lá phải là duy nhất.")

    def test_image_urls_validity(self):
        """Kiểm tra tất cả URL ảnh đều trỏ về Sacred Texts chuẩn định dạng .jpg."""
        for card in self.deck:
            self.assertTrue(
                card["img_url"].startswith("https://www.sacred-texts.com/tarot/pkt/img/"),
                f"URL ảnh của lá {card['name']} không đúng định dạng chuẩn Sacred Texts."
            )
            self.assertTrue(card["img_url"].endswith(".jpg"))

    def test_shuffle_deck_non_destructive(self):
        """Kiểm tra hàm shuffle bảo toàn số lượng và gán đủ thuộc tính chiều bài."""
        shuffled = shuffle_deck(self.deck)
        self.assertEqual(len(shuffled), 78, "Xáo bài không được làm mất hoặc tăng số lượng lá bài.")
        
        for card in shuffled:
            self.assertIn("orientation", card)
            self.assertIn(card["orientation"], ["Xuôi", "Ngược"])
            self.assertIn("meaning", card)
            self.assertTrue(len(card["meaning"]) > 0)

    def test_shuffle_randomness(self):
        """Kiểm tra vị trí lá bài thay đổi sau khi xáo (Fisher-Yates)."""
        shuffled_1 = shuffle_deck(self.deck)
        shuffled_2 = shuffle_deck(self.deck)
        
        ids_1 = [c["id"] for c in shuffled_1]
        ids_2 = [c["id"] for c in shuffled_2]
        # Xác suất 78 lá sau khi shuffle trùng thứ tự là 1/(78!) ~ 0
        self.assertNotEqual(ids_1, ids_2, "Thứ tự xáo bài của hai lần liên tiếp không được giống nhau.")

    def test_spread_configurations(self):
        """Kiểm tra tính hợp lệ của danh mục cấu hình trải bài."""
        self.assertGreaterEqual(len(SPREAD_CONFIGS), 3)
        for spread_name, data in SPREAD_CONFIGS.items():
            self.assertIn("description", data)
            self.assertIn("slots", data)
            self.assertTrue(len(data["slots"]) > 0)
            for slot in data["slots"]:
                self.assertIn("role", slot)
                self.assertIn("guide", slot)

    def test_generate_ai_prompt_format(self):
        """Kiểm tra chuỗi Prompt AI sinh ra đầy đủ câu hỏi, tên lá và vị trí."""
        shuffled = shuffle_deck(self.deck)
        test_question = "Tôi có nên đổi việc trong tháng sau không?"
        spread_name = "⏳ 3 Lá: Quá khứ - Hiện tại - Tương lai"
        slots = SPREAD_CONFIGS[spread_name]["slots"]
        picked = [shuffled[0], shuffled[1], shuffled[2]]
        clarity = shuffled[3]

        prompt = generate_ai_prompt(
            question=test_question,
            spread_name=spread_name,
            picked_cards=picked,
            spread_slots=slots,
            clarity_card=clarity
        )

        self.assertIn(test_question, prompt)
        self.assertIn(spread_name, prompt)
        self.assertIn(picked[0]["name"], prompt)
        self.assertIn("Clarity Card", prompt)
        self.assertIn("Actionable Advice", prompt)


if __name__ == "__main__":
    unittest.main(verbosity=2)