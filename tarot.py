import streamlit as st
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Tarot Reader - 78 Lá Chuẩn", page_icon="🔮", layout="wide")

# CSS "biến hình" các nút Streamlit thành các thẻ bài Tarot lưng tím huyền bí cuộn ngang
st.markdown("""
<style>
    /* Thanh cuộn ngang chứa 78 thẻ bài */
    div[data-testid="stHorizontalBlock"] {
        overflow-x: auto !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        gap: 12px !important;
        padding: 16px 12px !important;
        background: #090d16 !important;
        border-radius: 14px !important;
        border: 1px solid #1e293b !important;
        scrollbar-width: thin !important;
        scrollbar-color: #6366f1 #090d16 !important;
    }
    div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        height: 8px !important;
    }
    div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {
        background: #6366f1 !important;
        border-radius: 4px !important;
    }
    
    /* Cố định kích thước mỗi cột bài */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 0 0 85px !important;
        min-width: 85px !important;
        width: 85px !important;
    }

    /* Biến nút bấm thành thẻ bài Tarot */
    div[data-testid="stHorizontalBlock"] button {
        width: 85px !important;
        height: 140px !important;
        border-radius: 8px !important;
        background: radial-gradient(circle, #2e1065 0%, #0f172a 100%) !important;
        border: 2px solid #a855f7 !important;
        color: #e9d5ff !important;
        font-size: 26px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6) !important;
        transition: all 0.25s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Hiệu ứng khi rê chuột vào lá bài */
    div[data-testid="stHorizontalBlock"] button:hover {
        transform: translateY(-8px) scale(1.05) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 10px 22px rgba(56, 189, 248, 0.4) !important;
        color: #ffffff !important;
    }

    /* Thẻ bài đã rút */
    div[data-testid="stHorizontalBlock"] button:disabled {
        opacity: 0.2 !important;
        filter: grayscale(100%) !important;
        transform: none !important;
        border-color: #334155 !important;
        cursor: not-allowed !important;
    }

    /* Thẻ bài đã lật trên bàn */
    .tarot-card-box {
        background: #1e293b;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid #475569;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# 1. Dữ liệu chuẩn 78 lá bài Rider-Waite
MAJOR_ARCANA = [
    ("The Fool", "ar00"), ("The Magician", "ar01"), ("The High Priestess", "ar02"),
    ("The Empress", "ar03"), ("The Emperor", "ar04"), ("The Hierophant", "ar05"),
    ("The Lovers", "ar06"), ("The Chariot", "ar07"), ("Strength", "ar08"),
    ("The Hermit", "ar09"), ("Wheel of Fortune", "ar10"), ("Justice", "ar11"),
    ("The Hanged Man", "ar12"), ("Death", "ar13"), ("Temperance", "ar14"),
    ("The Devil", "ar15"), ("The Tower", "ar16"), ("The Star", "ar17"),
    ("The Moon", "ar18"), ("The Sun", "ar19"), ("Judgement", "ar20"), ("The World", "ar21")
]
SUITS_MAP = {"Wands": "wa", "Cups": "cu", "Swords": "sw", "Pentacles": "pe"}
RANKS_MAP = {
    "Ace": "ac", "Two": "02", "Three": "03", "Four": "04", "Five": "05",
    "Six": "06", "Seven": "07", "Eight": "08", "Nine": "09", "Ten": "10",
    "Page": "pa", "Knight": "kn", "Queen": "qu", "King": "ki"
}

ALL_CARDS_DATA = []
for name, code in MAJOR_ARCANA:
    ALL_CARDS_DATA.append({
        "name": name,
        "img_url": f"https://www.sacred-texts.com/tarot/pkt/img/{code}.jpg"
    })

for suit_name, s_code in SUITS_MAP.items():
    for rank_name, r_code in RANKS_MAP.items():
        ALL_CARDS_DATA.append({
            "name": f"{rank_name} of {suit_name}",
            "img_url": f"https://www.sacred-texts.com/tarot/pkt/img/{s_code}{r_code}.jpg"
        })

# Cấu hình các định dạng trải bài Tarot tiêu chuẩn
SPREAD_CONFIGS = {
    "⏳ Thời gian (Quá khứ - Hiện tại - Tương lai)": [
        "Quá khứ (Nền tảng/Cội nguồn)",
        "Hiện tại (Thực trạng hiện nay)",
        "Tương lai (Xu hướng tiến triển)"
    ],
    "💡 Hướng giải quyết (Hoàn cảnh - Thử thách - Lời khuyên)": [
        "Hoàn cảnh (Thực trạng bối cảnh)",
        "Thử thách (Rào cản/Khó khăn)",
        "Lời khuyên (Cách tháo gỡ)"
    ],
    "🧭 Lựa chọn (Lựa chọn A - Lựa chọn B - Yếu tố quyết định)": [
        "Lựa chọn A (Tiềm năng/Hệ quả A)",
        "Lựa chọn B (Tiềm năng/Hệ quả B)",
        "Yếu tố quyết định (Lời khuyên cân nhắc)"
    ],
    "✨ Trải bài mở (Lá 1 - Lá 2 - Lá 3)": [
        "Lá 1 (Tổng quan)",
        "Lá 2 (Yếu tố tác động)",
        "Lá 3 (Kết quả tiềm năng)"
    ]
}

# 2. Quản lý trạng thái Session[cite: 1]
if "deck_map" not in st.session_state:
    shuffled = ALL_CARDS_DATA.copy()
    random.shuffle(shuffled)
    st.session_state.deck_map = {
        i: {
            "name": item["name"],
            "img_url": item["img_url"],
            "orientation": "Xuôi" if random.random() > 0.3 else "Ngược"
        }
        for i, item in enumerate(shuffled)
    }

if "picked_indices" not in st.session_state:
    st.session_state.picked_indices = []

def reset_all():
    st.session_state.clear()
    st.rerun()

# --- GIAO DIỆN CHÍNH ---
st.markdown("<h2 style='text-align: center; color: #f8fafc;'>🔮 AI Tarot Chamber</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Tập trung năng lượng vào câu hỏi, chọn hình thức trải bài, cuộn ngang dải bài và click chọn lá bài.</p>", unsafe_allow_html=True)

# Tùy chọn câu hỏi và kiểu trải bài
col_q, col_s = st.columns([3, 2])
with col_q:
    question = st.text_input(
        "💬 Nhập câu hỏi hoặc băn khoăn của bạn:",
        placeholder="Ví dụ: Công việc của tôi trong 3 tháng tới sẽ phát triển ra sao?",
        key="user_question"
    )

with col_s:
    selected_spread = st.selectbox(
        "🎴 Chọn hình thức trải bài:",
        options=list(SPREAD_CONFIGS.keys()),
        index=0
    )

position_meanings = SPREAD_CONFIGS[selected_spread]
picked_count = len(st.session_state.picked_indices)

if not question.strip():
    st.warning("👉 Vui lòng nhập câu hỏi trước khi chọn bài từ dải bài bên dưới.")
else:
    if picked_count < 3:
        target_role = position_meanings[picked_count]
        st.info(f"✨ Hãy rút lá đại diện cho: **{target_role}** (Đã chọn {picked_count}/3 lá chính).")
    elif picked_count == 3:
        st.success("✅ Đã đủ 3 vị trí chính của trải bài! Bạn có thể click chọn thêm 1 lá thứ 4 làm rõ (Clarity Card) hoặc copy prompt bên dưới.")
    else:
        st.success("🎉 Đã hoàn thiện toàn bộ trải bài (3 lá chính + 1 lá làm rõ)!")

st.divider()

# KHU VỰC 1: CÁC LÁ BÀI ĐÃ BỐC TRÊN BÀN[cite: 1]
if picked_count > 0:
    st.markdown("### 🎴 Các lá bài trên bàn của bạn:")
    cols = st.columns(max(4, picked_count))
    for i, idx in enumerate(st.session_state.picked_indices):
        card = st.session_state.deck_map[idx]
        slot_label = position_meanings[i] if i < 3 else "Lá 4: Làm rõ (Clarity / Chốt hướng đi)"
        is_reversed = card["orientation"] == "Ngược"
        rev_style = "transform: rotate(180deg);" if is_reversed else ""
        badge_color = "#991b1b" if is_reversed else "#065f46"
        
        with cols[i]:
            st.markdown(f"""
            <div class="tarot-card-box">
                <div style="font-size: 13px; color: #a5b4fc; font-weight: bold; margin-bottom: 6px; min-height: 38px;">{slot_label}</div>
                <div style="min-height: 240px; display: flex; align-items: center; justify-content: center;">
                    <img src="{card['img_url']}" style="width: 100%; max-width: 160px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); {rev_style}" referrerpolicy="no-referrer" alt="{card['name']}" />
                </div>
                <div style="font-size: 15px; font-weight: bold; margin: 10px 0 6px; color: #f8fafc;">{card['name']}</div>
                <span style="font-size: 12px; padding: 3px 10px; border-radius: 9999px; background: {badge_color}; color: white; font-weight: 600;">
                    {card['orientation']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# KHU VỰC 2: DẢI 78 LÁ BÀI CUỘN NGANG (NATIVE STREAMLIT BUTTON)[cite: 1]
st.markdown("### 🃏 Dải bài 78 lá (Cuộn ngang để lướt tìm lá bài)")
st.caption("👈 Giữ Shift + Lăn chuột hoặc vuốt sang ngang để lướt dải bài, click thẳng vào lá bài để rút 👉")

scroll_cols = st.columns(78)
can_pick_more = bool(question.strip()) and (picked_count < 4)

for i in range(78):
    with scroll_cols[i]:
        is_picked = i in st.session_state.picked_indices
        btn_symbol = "✓" if is_picked else "✦"
        
        if st.button(btn_symbol, key=f"tarot_card_{i}", disabled=(is_picked or not can_pick_more)):
            st.session_state.picked_indices.append(i)
            st.rerun()

# KHU VỰC 3: PROMPT VÀ NÚT COPY[cite: 1]
if picked_count >= 3:
    st.divider()
    st.markdown("### 📋 Prompt gửi cho AI Reader để giải bài")

    cards_summary = []
    for i, idx in enumerate(st.session_state.picked_indices):
        card = st.session_state.deck_map[idx]
        slot_label = position_meanings[i] if i < 3 else "Lá 4: Làm rõ (Clarity Card)"
        cards_summary.append(f"- Vị trí [{slot_label}]: {card['name']} ({card['orientation']})")

    cards_text = "\n".join(cards_summary)
    clarity_instruction = "3. Kết hợp Lá 4 (Làm rõ) để chốt lại thông điệp then chốt và hướng giải quyết dứt điểm cho vấn đề." if picked_count == 4 else ""

    prompt_to_copy = f"""Tôi đang có băn khoăn sau: "{question.strip()}"

Tôi đã thực hiện trải bài theo hình thức: "{selected_spread}" từ bộ bài chuẩn 78 lá Rider-Waite:
{cards_text}

Bạn hãy đóng vai một Tarot Reader chuyên nghiệp, tinh tế và thấu cảm để giải mã trải bài này:
1. Luận giải chi tiết từng lá bài dựa trên ĐÚNG Ý NGHĨA VỊ TRÍ của nó trong trải bài và trạng thái Xuôi/Ngược.
2. Xâu chuỗi mối liên kết logic giữa các lá bài để giải đáp thắc mắc của tôi.
{clarity_instruction}
4. Đưa ra lời khuyên thực tế (Actionable Advice) và định hướng tâm lý vững vàng nhất."""

    st.code(prompt_to_copy, language="markdown")

    copy_button_html = f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <button id="copy-btn" onclick="copyToClipboard()" style="
            background: linear-gradient(135deg, #4f46e5, #06b6d4);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
        ">📋 Bấm vào đây để Sao chép Prompt ngay</button>
    </div>
    <script>
    function copyToClipboard() {{
        const text = `{prompt_to_copy.replace('`', '\\`').replace('\\', '\\\\')}`;
        navigator.clipboard.writeText(text).then(() => {{
            const btn = document.getElementById('copy-btn');
            btn.innerText = '✅ Đã sao chép vào bộ nhớ tạm! Hãy quay lại chat dán (Ctrl+V)';
            btn.style.background = '#059669';
        }});
    }}
    </script>
    """
    components.html(copy_button_html, height=60)

    if st.button("🔄 Xáo bài & Làm lại từ đầu", use_container_width=True):
        reset_all()