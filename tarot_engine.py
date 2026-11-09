"""
tarot_engine.py - Core domain logic cho hệ thống AI Tarot Reader.
Quản lý dữ liệu 78 lá Rider-Waite, xáo bài Fisher-Yates, trải bài và sinh prompt.
"""

import random
from typing import Dict, List, Any, Optional

MAJOR_ARCANA_RAW = [
    ("The Fool", "Chàng Khờ", "ar00", "Khí", "Khởi đầu mới, tự do, ngây thơ, phiêu lưu", "Bồng bột, liều lĩnh, ngây ngô quá mức, trì hoãn"),
    ("The Magician", "Ảo Thuật Gia", "ar01", "Khí", "Năng lực biểu hiện, chủ động, sáng tạo, nguồn lực sẵn có", "Thao túng, lừa dối, tài năng chưa dùng đến, phân tán"),
    ("The High Priestess", "Nữ Đại Tư Tế", "ar02", "Nước", "Trực giác nhạy bén, tri thức ẩn giấu, tĩnh lặng, bí ẩn", "Mất kết nối nội tâm, bí mật lộ tẩy, nông cạn, bất an"),
    ("The Empress", "Hoàng Hậu", "ar03", "Đất", "Sung túc, nuôi dưỡng, tình mẫu tử, cái đẹp, trù phú", "Phụ thuộc cảm xúc, bế tắc sáng tạo, bỏ bê bản thân"),
    ("The Emperor", "Hoàng Đế", "ar04", "Lửa", "Trật tự, quyền lực, kỷ luật, bảo vệ, tính ổn định", "Độc đoán, kiểm soát thái quá, cứng nhắc, hỗn loạn"),
    ("The Hierophant", "Giáo Hoàng", "ar05", "Đất", "Truyền thống, niềm tin tâm linh, học vấn, chuẩn mực xã hội", "Nổi loạn vô căn cứ, giáo điều cực đoan, niềm tin mù quáng"),
    ("The Lovers", "Đôi Tình Nhân", "ar06", "Khí", "Tình yêu đích thực, gắn kết hòa hợp, lựa chọn giá trị sống", "Mâu thuẫn, mất cân bằng, chọn sai hướng, rạn nứt"),
    ("The Chariot", "Cỗ Xe", "ar07", "Nước", "Ý chí sắt đá, tiến về phía trước, chiến thắng, làm chủ", "Mất phương hướng, hung hăng, mất tự chủ, bế tắc"),
    ("Strength", "Sức Mạnh", "ar08", "Lửa", "Lòng dũng cảm thầm lặng, kiên nhẫn, thuần hóa bản năng", "Tự ti, nghi ngờ bản thân, kiệt sức, yếu lòng"),
    ("The Hermit", "Ẩn Sĩ", "ar09", "Đất", "Chiêm nghiệm nội tâm, tìm kiếm chân lý, tỉnh thức, đơn độc", "Cô lập cực đoan, cô đơn, né tránh thực tại, bảo thủ"),
    ("Wheel of Fortune", "Bánh Xe Số Phận", "ar10", "Lửa", "Bước ngoặt định mệnh, chu kỳ mới, may mắn, thời cơ", "Xui xẻo tạm thời, kháng cự thay đổi, chuỗi rủi ro"),
    ("Justice", "Công Lý", "ar11", "Khí", "Công bằng, sự thật, luật nhân quả, quyết định sáng suốt", "Bất công, dối trá, chối bỏ trách nhiệm, thiên vị"),
    ("The Hanged Man", "Người Treo Ngược", "ar12", "Nước", "Nhìn nhận góc độ mới, buông bỏ để tiến lên, hy sinh", "Cố chấp vô ích, trì trệ, không chịu buông xả, bế tắc"),
    ("Death", "Cái Chết", "ar13", "Nước", "Chấm dứt chu kỳ cũ, biến chuyển sâu sắc, tái sinh", "Sợ thay đổi, níu kéo quá khứ, kháng cự kết thúc tất yếu"),
    ("Temperance", "Tiết Độ", "ar14", "Lửa", "Cân bằng, dung hòa, kiên nhẫn điều độ, hòa hợp nội tâm", "Mất cân bằng, cực đoan, vội vã, xung đột lợi ích"),
    ("The Devil", "Ác Quỷ", "ar15", "Đất", "Sự trói buộc, cám dỗ, ám ảnh vật chất, thói quen độc hại", "Tự do dần tìm lại, giải thoát xiềng xích, nhìn rõ ảo vọng"),
    ("The Tower", "Tòa Tháp", "ar16", "Lửa", "Sụp đổ bất ngờ, vỡ mộng, thức tỉnh sau biến cố lớn", "Trì hoãn điều tất yếu, sợ đối diện đổ vỡ, tổn thương ngấm ngầm"),
    ("The Star", "Ngôi Sao", "ar17", "Khí", "Hy vọng tươi sáng, chữa lành, niềm tin, nguồn cảm hứng", "Mất niềm tin, tuyệt vọng tạm thời, bi quan, ảo tưởng"),
    ("The Moon", "Mặt Trăng", "ar18", "Nước", "Hoang mang, ảo giác, nỗi sợ tiềm thức, bí mật chưa rõ", "Sự thật dần sáng tỏ, xua tan mơ hồ, vượt qua nỗi sợ"),
    ("The Sun", "Mặt Trời", "ar19", "Lửa", "Hân hoan, thành công rực rỡ, năng lượng tích cực, minh bạch", "Niềm vui bị che khuất, tự phụ quá mức, nhiệt huyết giảm sút"),
    ("Judgement", "Phán Xét", "ar20", "Lửa", "Tỉnh thức, tiếng gọi nội tâm, tha thứ, bắt đầu hành trình mới", "Tự phán xét bản thân gay gắt, chần chừ, tiếc nuối"),
    ("The World", "Thế Giới", "ar21", "Đất", "Hoàn tất trọn vẹn, thành tựu viên mãn, hội nhập, tự do lớn", "Chưa thể kết thúc, thiếu bước cuối, cảm giác dở dang")
]

SUITS_META = {
    "Wands": {"vi": "Gậy", "code": "wa", "element": "Lửa", "realm": "Hành động, đam mê, sự nghiệp, ý chí"},
    "Cups": {"vi": "Cốc", "code": "cu", "element": "Nước", "realm": "Cảm xúc, tình cảm, trực giác, mối quan hệ"},
    "Swords": {"vi": "Kiếm", "code": "sw", "element": "Khí", "realm": "Tư duy, giao tiếp, xung đột, sự thật"},
    "Pentacles": {"vi": "Tiền", "code": "pe", "element": "Đất", "realm": "Tài chính, vật chất, công việc thực tế, sức khỏe"}
}

RANKS_META = [
    ("Ace", "Át", "ac", "Khởi nguồn năng lượng mới, hạt mầm tiềm năng", "Cơ hội bị bỏ lỡ, khởi đầu trắc trở"),
    ("Two", "Hai", "02", "Cân nhắc, kết nối đôi bên, lựa chọn cân bằng", "Mất cân bằng, do dự kéo dài, chia rẽ"),
    ("Three", "Ba", "03", "Mở rộng, hợp tác, kết quả ban đầu, phát triển", "Bất đồng quan điểm, đình trệ dự án"),
    ("Four", "Bốn", "04", "Ổn định, củng cố nền móng, an toàn, nghỉ ngơi", "Bảo thủ, ngột ngạt, sợ rủi ro, cô lập"),
    ("Five", "Năm", "05", "Xung đột, thử thách, mất mát, bài học gian nan", "Hòa giải sau biến cố, chấp nhận quá khứ"),
    ("Six", "Sáu", "06", "Hài hòa, sẻ chia, hồi phục, nhận trợ lực", "Mất cân bằng cho nhận, quá khứ níu chân"),
    ("Seven", "Bảy", "07", "Đánh giá lại, chiến lược, kiên trì thử nghiệm", "Ảo tưởng kế hoạch, thiếu tập trung, ngờ vực"),
    ("Eight", "Tám", "08", "Chuyển động nhanh, rèn luyện kỹ năng, chủ động", "Hấp tấp, trì hoãn vô cớ, mất phương hướng"),
    ("Nine", "Chín", "09", "Đạt đến đỉnh điểm, tự lực, kiên cường bảo vệ", "Kiệt sức, phòng thủ quá mức, cô đơn"),
    ("Ten", "Mười", "10", "Hoàn thành một chu kỳ, gánh nặng hoặc viên mãn", "Gánh nặng quá tải, sụp đổ, sẵn sàng buông"),
    ("Page", "Tiểu Đồng", "pa", "Người mang thông điệp, tò mò, học hỏi, nhiệt thành", "Trẻ con, thiếu kinh nghiệm, tin tức chậm trễ"),
    ("Knight", "Hiệp Sĩ", "kn", "Hành động quyết liệt, bứt phá, dấn thân", "Bốc đồng, nóng vội, thiếu suy tính đường dài"),
    ("Queen", "Hoàng Hậu", "qu", "Làm chủ nội lực, thấu cảm, chín chắn, bao dung", "Kiểm soát cảm xúc kém, lạnh lùng, ghen tuông"),
    ("King", "Quốc Vương", "ki", "Lãnh đạo đỉnh cao, quyền uy, làm chủ vận mệnh", "Độc tài, lạm dụng quyền hạn, thiếu khoan dung")
]

SPREAD_CONFIGS = {
    "⏳ 3 Lá: Quá khứ - Hiện tại - Tương lai": {
        "description": "Xem dòng chảy thời gian, nguồn gốc và xu hướng phát triển của vấn đề.",
        "slots": [
            {"role": "Quá khứ", "guide": "Nền tảng, cội nguồn và nguyên nhân dẫn đến hiện trạng."},
            {"role": "Hiện tại", "guide": "Thực trạng năng lượng, tình huống đang diễn ra."},
            {"role": "Tương lai", "guide": "Xu hướng tiến triển trong thời gian sắp tới."}
        ]
    },
    "💡 3 Lá: Hoàn cảnh - Thử thách - Lời khuyên": {
        "description": "Tháo gỡ bế tắc thực tế và tìm giải pháp tối ưu cho quyết định quan trọng.",
        "slots": [
            {"role": "Hoàn cảnh", "guide": "Bức tranh toàn cảnh hiện tại của sự việc."},
            {"role": "Thử thách", "guide": "Rào cản, xung đột hoặc bài học cần vượt qua."},
            {"role": "Lời khuyên", "guide": "Hành động cụ thể cần làm để giải quyết vấn đề."}
        ]
    },
    "❤️ 3 Lá: Tình Duyên & Gắn Kết": {
        "description": "Soi chiếu tâm lý hai người và triển vọng kết nối tình cảm.",
        "slots": [
            {"role": "Năng lượng của bạn", "guide": "Cảm xúc và suy nghĩ thật của bạn trong mối quan hệ."},
            {"role": "Năng lượng đối phương", "guide": "Tâm tư, cách nhìn nhận từ phía đối phương."},
            {"role": "Điểm chung & Xu hướng", "guide": "Mối liên kết chung và hướng đi sắp tới."}
        ]
    },
    "🧭 3 Lá: Lựa chọn A vs Lựa chọn B": {
        "description": "Cân nhắc giữa hai ngã rẽ và tìm yếu tố then chốt để quyết định.",
        "slots": [
            {"role": "Con đường A", "guide": "Tiềm năng và thử thách nếu chọn hướng A."},
            {"role": "Con đường B", "guide": "Tiềm năng và thử thách nếu chọn hướng B."},
            {"role": "Yếu tố quyết định", "guide": "Tiêu chí quan trọng nhất giúp bạn đưa ra lựa chọn."}
        ]
    },
    "🌟 1 Lá: Thông điệp hôm nay (Daily Card)": {
        "description": "Nhận một thông điệp cô đọng, định hướng tâm thế trong ngày hoặc trả lời Yes/No nhanh.",
        "slots": [
            {"role": "Thông điệp then chốt", "guide": "Trọng tâm bài học và năng lượng chủ đạo."}
        ]
    }
}


def build_full_deck() -> List[Dict[str, Any]]:
    """Khởi tạo đầy đủ 78 lá bài chuẩn Rider-Waite với metadata song ngữ."""
    deck: List[Dict[str, Any]] = []
    card_id = 0

    for en_name, vi_name, code, element, upright_kw, rev_kw in MAJOR_ARCANA_RAW:
        deck.append({
            "id": card_id,
            "type": "Major",
            "name": en_name,
            "name_vi": vi_name,
            "suit": "Major",
            "element": element,
            "img_url": f"https://www.sacred-texts.com/tarot/pkt/img/{code}.jpg",
            "upright_kw": upright_kw,
            "reversed_kw": rev_kw
        })
        card_id += 1

    for suit_en, suit_data in SUITS_META.items():
        s_code = suit_data["code"]
        for rank_en, rank_vi, r_code, rank_up, rank_rev in RANKS_META:
            deck.append({
                "id": card_id,
                "type": "Minor",
                "name": f"{rank_en} of {suit_en}",
                "name_vi": f"{rank_vi} {suit_data['vi']}",
                "suit": suit_en,
                "element": suit_data["element"],
                "img_url": f"https://www.sacred-texts.com/tarot/pkt/img/{s_code}{r_code}.jpg",
                "upright_kw": f"{rank_up}. Thuộc lĩnh vực: {suit_data['realm']}.",
                "reversed_kw": f"{rank_rev}. Thuộc lĩnh vực: {suit_data['realm']}."
            })
            card_id += 1

    return deck


def shuffle_deck(deck: List[Dict[str, Any]], reversed_chance: float = 0.3) -> List[Dict[str, Any]]:
    """Xáo bài bằng thuật toán Fisher-Yates và gán ngẫu nhiên trạng thái Xuôi/Ngược."""
    shuffled = [card.copy() for card in deck]
    for i in range(len(shuffled) - 1, 0, -1):
        j = random.randint(0, i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

    for card in shuffled:
        is_reversed = random.random() < reversed_chance
        card["orientation"] = "Ngược" if is_reversed else "Xuôi"
        card["is_reversed"] = is_reversed
        card["meaning"] = card["reversed_kw"] if is_reversed else card["upright_kw"]

    return shuffled


def generate_ai_prompt(
    question: str,
    spread_name: str,
    picked_cards: List[Dict[str, Any]],
    spread_slots: List[Dict[str, str]],
    clarity_card: Optional[Dict[str, Any]] = None
) -> str:
    """Sinh prompt Markdown chất lượng cao để nạp trực tiếp cho AI giải bài."""
    cards_text_lines = []
    
    for i, card in enumerate(picked_cards):
        role_info = spread_slots[i]["role"] if i < len(spread_slots) else f"Vị trí {i+1}"
        guide_info = spread_slots[i]["guide"] if i < len(spread_slots) else ""
        guide_str = f" ({guide_info})" if guide_info else ""
        
        cards_text_lines.append(
            f"- **Vị trí [{role_info}]{guide_str}: "
            f"**{card["name"]}** ({card["name_vi"]}) - Trạng thái: *{card['orientation']}* "
            f"(Nguyên tố: {card['element']})\n"
            f"  *Từ khóa ý nghĩa*: {card['meaning']}"
        )

    if clarity_card:
        cards_text_lines.append(
            f"- **Lá Bổ Trợ / Làm Rõ (Clarity Card)**: "
            f"**{clarity_card['name']}** ({clarity_card['name_vi']}) - Trạng thái: *{clarity_card['orientation']}* "
            f"(Nguyên tố: {clarity_card['element']})\n"
            f"  *Từ khóa ý nghĩa*: {clarity_card['meaning']}"
        )

    cards_block = "\n".join(cards_text_lines)
    clarity_rule = (
        "4. Dùng Lá Bổ Trợ (Clarity Card) để chốt lại nút thắt then chốt và điểm đột phá giải quyết vấn đề."
        if clarity_card else ""
    )

    all_cards = picked_cards + ([clarity_card] if clarity_card else [])
    all_elements = sorted(list(set(c["element"] for c in all_cards)))

    prompt = f"""Tôi có câu hỏi/băn khoăn sau: "{question.strip()}"

Hình thức trải bài: "{spread_name}"
Bộ bài: Chuẩn 78 lá Rider-Waite Smith (RWS)
Dưới đây là các lá bài được rút:
{cards_block}

Hãy đóng vai một Tarot Reader chuyên nghiệp, uyên bác và giàu lòng thấu cảm:
1. Phân tích chi tiết từng lá bài dựa trên: ý nghĩa biểu tượng, nguyên tố ({', '.join(all_elements)}), trạng thái Xuôi/Ngược và đúng vai trò của vị trí đó trong trải bài.
2. Xâu chuỗi mối quan hệ tương hỗ hoặc xung đột giữa các nguyên tố và các lá bài để trả lời trọng tâm câu hỏi của tôi.
3. Chỉ ra bài học tiềm thức hoặc góc nhìn mới mà tôi có thể đang bỏ quên.
{clarity_rule}
5. Kết luận bằng lời khuyên hành động thực tế (Actionable Advice) và thông điệp động viên tích cực, vững vàng."""

    return prompt