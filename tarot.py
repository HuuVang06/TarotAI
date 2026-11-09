"""
tarot.py - Hệ thống Huyền Học Đa Năng (Tarot 78 Lá, Tử Vi Đẩu Số, Bài Tây 52 Lá, Tiếp Sức Server)
Giao diện tối ưu Mobile & PC, lật bài 3D bay lên bàn trải, tự sinh Prompt AI và tích hợp VietQR.
"""

import textwrap
import datetime
import random
import streamlit as st
import streamlit.components.v1 as components
from tarot_engine import (
    build_full_deck,
    shuffle_deck,
    SPREAD_CONFIGS,
    generate_ai_prompt
)

st.set_page_config(
    page_title="Mystic Chamber AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TỔNG THỂ CHO TOÀN BỘ GIAO DIỆN & HOẠT ẢNH 3D ---
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #030712 100%);
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* 1. HOẠT ẢNH THẺ BÀI BAY TỪ DƯỚI LÊN & LẬT 3D (FLY-UP & 3D FLIP) */
    @keyframes flyUpAndFlip3D {
        0% {
            transform: perspective(1000px) translateY(320px) scale(0.65) rotateY(180deg);
            opacity: 0;
            filter: drop-shadow(0 0 30px rgba(168, 85, 247, 0.9));
        }
        55% {
            transform: perspective(1000px) translateY(-28px) scale(1.08) rotateY(25deg);
            opacity: 0.95;
        }
        75% {
            transform: perspective(1000px) translateY(8px) scale(1.02) rotateY(-8deg);
        }
        100% {
            transform: perspective(1000px) translateY(0) scale(1) rotateY(0deg);
            opacity: 1;
            filter: drop-shadow(0 10px 25px rgba(0, 0, 0, 0.7));
        }
    }

    .card-just-drawn {
        animation: flyUpAndFlip3D 0.85s cubic-bezier(0.2, 0.9, 0.3, 1) forwards !important;
        transform-origin: center center;
    }

    .card-settled {
        opacity: 1;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .card-settled:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.8), 0 0 25px rgba(56, 189, 248, 0.4);
    }

    .tarot-revealed-card {
        background: linear-gradient(165deg, rgba(30, 41, 59, 0.92) 0%, rgba(15, 23, 42, 0.96) 100%);
        border: 1px solid rgba(139, 92, 246, 0.6);
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6), 0 0 20px rgba(139, 92, 246, 0.25);
    }

    .slot-role-header {
        font-size: 12px;
        font-weight: 700;
        color: #c084fc;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
        min-height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .card-img-box {
        width: 100%;
        max-width: 155px;
        margin: 0 auto 10px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 8px 18px rgba(0,0,0,0.7);
        background: #0b0f19;
    }
    .card-img-box img {
        width: 100%;
        display: block;
    }

    .card-name-vi {
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    .card-name-en {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .tag-container {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-bottom: 8px;
        flex-wrap: wrap;
    }
    .tag-badge {
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .badge-upright { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; }
    .badge-reversed { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #dc2626; }
    .badge-elem { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid #6366f1; }

    .meaning-desc-box {
        font-size: 11.5px;
        color: #cbd5e1;
        line-height: 1.45;
        background: rgba(15, 23, 42, 0.65);
        padding: 8px 10px;
        border-radius: 8px;
        text-align: left;
        border-left: 3px solid #8b5cf6;
    }

    .tarot-slot-waiting {
        border: 2px dashed #818cf8;
        border-radius: 14px;
        padding: 24px 12px;
        text-align: center;
        background: rgba(30, 27, 75, 0.25);
        min-height: 330px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #a5b4fc;
        animation: pulseGlow 1.8s infinite ease-in-out;
    }
    @keyframes pulseGlow {
        0%, 100% { border-color: rgba(99, 102, 241, 0.4); box-shadow: 0 0 10px rgba(99, 102, 241, 0.2); }
        50% { border-color: rgba(168, 85, 247, 0.9); box-shadow: 0 0 22px rgba(168, 85, 247, 0.45); }
    }

    .tarot-slot-locked {
        border: 1px dashed #334155;
        border-radius: 14px;
        padding: 24px 12px;
        text-align: center;
        background: rgba(15, 23, 42, 0.25);
        min-height: 330px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #64748b;
    }

    /* 2. DẢI 78 LÁ BÀI VUỐT NGANG (KÍCH THƯỚC TO - DỄ BẤM) */
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) {
        overflow-x: auto !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 16px !important;
        padding: 24px 16px 36px 16px !important;
        background: radial-gradient(ellipse at bottom, #111827 0%, #030712 100%) !important;
        border-radius: 18px !important;
        border: 1px solid rgba(139, 92, 246, 0.45) !important;
        box-shadow: inset 0 2px 28px rgba(0, 0, 0, 0.9), 0 8px 30px rgba(124, 58, 237, 0.25) !important;
        scrollbar-width: thin !important;
        scrollbar-color: #8b5cf6 #090d16 !important;
        -webkit-overflow-scrolling: touch !important;
        scroll-behavior: smooth !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15))::-webkit-scrollbar {
        height: 10px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15))::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #6366f1, #a855f7) !important;
        border-radius: 6px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) > div,
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) [data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) [data-testid="column"] {
        flex: 0 0 115px !important;
        min-width: 115px !important;
        max-width: 115px !important;
        width: 115px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) button {
        width: 115px !important;
        min-width: 115px !important;
        height: 180px !important;
        min-height: 180px !important;
        border-radius: 12px !important;
        background: radial-gradient(circle at center, #2e1065 0%, #1e1b4b 65%, #080c14 100%) !important;
        border: 2px solid #a855f7 !important;
        color: #e9d5ff !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.75), inset 0 0 16px rgba(168, 85, 247, 0.35) !important;
        transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) button:hover:not(:disabled) {
        transform: translateY(-15px) scale(1.08) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 18px 32px rgba(56, 189, 248, 0.5), inset 0 0 20px rgba(56, 189, 248, 0.4) !important;
        color: #ffffff !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) button:disabled {
        opacity: 0.18 !important;
        filter: grayscale(100%) !important;
        transform: none !important;
        border-color: #334155 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }

    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) > div,
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) [data-testid="stColumn"] {
            flex: 0 0 96px !important;
            min-width: 96px !important;
            max-width: 96px !important;
            width: 96px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(15)) button {
            width: 96px !important;
            min-width: 96px !important;
            height: 155px !important;
            min-height: 155px !important;
            font-size: 22px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. VIEW: XEM TAROT (78 LÁ CHUẨN RWS)
# ==========================================
def render_tarot_view():
    if "base_deck" not in st.session_state:
        st.session_state.base_deck = build_full_deck()

    if "shuffled_deck" not in st.session_state:
        st.session_state.shuffled_deck = shuffle_deck(st.session_state.base_deck)

    if "picked_indices" not in st.session_state:
        st.session_state.picked_indices = []

    if "just_drawn" not in st.session_state:
        st.session_state.just_drawn = False

    def reset_deck():
        st.session_state.shuffled_deck = shuffle_deck(st.session_state.base_deck)
        st.session_state.picked_indices = []
        st.session_state.just_drawn = False
        st.rerun()

    st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 2px;'>🔮 AI Tarot Chamber</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Tập trung tâm niệm vào câu hỏi, vuốt dải bài bên dưới và chạm vào lá bài định mệnh</p>", unsafe_allow_html=True)

    col_q, col_s = st.columns([3, 2])
    with col_q:
        question = st.text_input(
            "💬 Nhập câu hỏi bạn đang trăn trở:",
            placeholder="Ví dụ: Định hướng sự nghiệp của tôi trong vài tháng tới sẽ ra sao?",
            key="tarot_user_question"
        )

    with col_s:
        spread_name = st.selectbox(
            "🎴 Chọn kiểu trải bài:",
            options=list(SPREAD_CONFIGS.keys()),
            index=0
        )

    spread_data = SPREAD_CONFIGS[spread_name]
    slots = spread_data["slots"]
    max_main = len(slots)
    current_picks = len(st.session_state.picked_indices)

    st.caption(f"ℹ️ **Ý nghĩa trải bài**: {spread_data['description']}")

    if not question.strip():
        st.warning("👉 Hãy nhập câu hỏi trước để bắt đầu mở dải bài.")
    else:
        if current_picks < max_main:
            cur_role = slots[current_picks]["role"]
            cur_guide = slots[current_picks]["guide"]
            st.info(f"✨ Vuốt dải bài bên dưới và chọn lá đại diện cho: **{cur_role}** ({cur_guide}) - Đã rút {current_picks}/{max_main} lá.")
        elif current_picks == max_main:
            st.success(f"✅ Đã đủ {max_main} lá chính! Bạn có thể rút thêm 1 lá bổ trợ (Clarity Card) hoặc copy prompt bên dưới.")
        else:
            st.success("🎉 Trải bài đã hoàn thiện đầy đủ cả lá chính và lá bổ trợ!")

    st.divider()
    st.markdown("<div id='tarot-board-anchor'></div>", unsafe_allow_html=True)

    # Bàn trải bài với hiệu ứng bay & lật 3D
    st.markdown("### 🎴 Bàn Trải Bài")
    total_slots = max_main + (1 if current_picks >= max_main else 0)
    table_cols = st.columns(total_slots)

    for col_idx in range(total_slots):
        with table_cols[col_idx]:
            if col_idx < current_picks:
                card = st.session_state.shuffled_deck[st.session_state.picked_indices[col_idx]]
                is_clarity = col_idx >= max_main
                role_label = slots[col_idx]["role"] if not is_clarity else "🌟 Lá Bổ Trợ (Clarity)"
                
                rev_style = "transform: rotate(180deg);" if card["is_reversed"] else ""
                badge_class = "badge-reversed" if card["is_reversed"] else "badge-upright"
                anim_class = "card-just-drawn" if (col_idx == current_picks - 1 and st.session_state.just_drawn) else "card-settled"
                
                card_html = textwrap.dedent(f"""
                    <div class="tarot-revealed-card {anim_class}">
                        <div class="slot-role-header">{role_label}</div>
                        <div class="card-img-box">
                            <img src="{card['img_url']}" style="{rev_style}" referrerpolicy="no-referrer" alt="{card['name']}" />
                        </div>
                        <div class="card-name-vi">{card['name_vi']}</div>
                        <div class="card-name-en">{card['name']}</div>
                        <div class="tag-container">
                            <span class="tag-badge {badge_class}">{card['orientation']}</span>
                            <span class="tag-badge badge-elem">{card['element']}</span>
                        </div>
                        <div class="meaning-desc-box">
                            <b>Ý nghĩa</b>: {card['meaning']}
                        </div>
                    </div>
                """)
                st.markdown(card_html, unsafe_allow_html=True)

            elif col_idx == current_picks and bool(question.strip()):
                role_label = slots[col_idx]["role"] if col_idx < max_main else "Lá Bổ Trợ (Clarity)"
                waiting_html = textwrap.dedent(f"""
                    <div class="tarot-slot-waiting">
                        <div style="font-size: 32px; margin-bottom: 8px;">✨</div>
                        <div style="font-weight: 700; font-size: 15px; margin-bottom: 4px;">{role_label}</div>
                        <div style="font-size: 12px; color: #c7d2fe;">Vuốt dải bài bên dưới<br>và chạm để rút</div>
                    </div>
                """)
                st.markdown(waiting_html, unsafe_allow_html=True)

            else:
                role_label = slots[col_idx]["role"] if col_idx < max_main else "Lá Bổ Trợ"
                locked_html = textwrap.dedent(f"""
                    <div class="tarot-slot-locked">
                        <div style="font-size: 26px; margin-bottom: 8px;">🔒</div>
                        <div style="font-weight: 600; font-size: 13px;">{role_label}</div>
                    </div>
                """)
                st.markdown(locked_html, unsafe_allow_html=True)

    if st.session_state.just_drawn:
        st.session_state.just_drawn = False

    st.markdown("<br>", unsafe_allow_html=True)

    # Dải bài 78 lá vuốt ngang
    col_deck_title, col_deck_actions = st.columns([3, 1])
    with col_deck_title:
        st.markdown("### 🃏 Dải bài 78 lá (Vuốt ngón tay hoặc kéo chuột để lướt)")
        st.caption("👈 Vuốt sang ngang tìm lá bài bạn cảm nhận mạnh nhất, nhấp thẳng vào lá bài để rút 👉")
    with col_deck_actions:
        if st.button("🔄 Xáo lại bài", use_container_width=True):
            reset_deck()

    can_pick_more = bool(question.strip()) and (current_picks < max_main + 1)
    deck_cols = st.columns(78)

    for i in range(78):
        with deck_cols[i]:
            is_picked = i in st.session_state.picked_indices
            btn_symbol = "✓" if is_picked else "✦"
            if st.button(btn_symbol, key=f"tarot_card_{i}", disabled=(is_picked or not can_pick_more)):
                st.session_state.picked_indices.append(i)
                st.session_state.just_drawn = True
                st.rerun()

    # Kéo chuột mượt mà trên PC và tự động lướt lên bàn trải bài
    components.html("""
    <script>
    setTimeout(function() {
        const parentDoc = window.parent.document;
        const blocks = parentDoc.querySelectorAll('div[data-testid="stHorizontalBlock"]');
        let deckBlock = null;
        blocks.forEach(b => {
            if (b.children.length > 20) { deckBlock = b; }
        });
        if (deckBlock) {
            let isDown = false;
            let startX, scrollLeft;
            deckBlock.style.cursor = 'grab';

            deckBlock.addEventListener('mousedown', (e) => {
                if (e.target.tagName === 'BUTTON') return;
                isDown = true;
                deckBlock.style.cursor = 'grabbing';
                startX = e.pageX - deckBlock.offsetLeft;
                scrollLeft = deckBlock.scrollLeft;
            });
            deckBlock.addEventListener('mouseleave', () => { isDown = false; deckBlock.style.cursor = 'grab'; });
            deckBlock.addEventListener('mouseup', () => { isDown = false; deckBlock.style.cursor = 'grab'; });
            deckBlock.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - deckBlock.offsetLeft;
                const walk = (x - startX) * 1.6;
                deckBlock.scrollLeft = scrollLeft - walk;
            });
        }
        const anchor = parentDoc.getElementById('tarot-board-anchor');
        if (anchor) { anchor.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    }, 300);
    </script>
    """, height=0)

    # PROMPT AI & KHU VỰC KHỀU DONATE TINH TẾ (GIEO DUYÊN)
    if current_picks >= max_main:
        st.divider()
        st.markdown("### 📋 Prompt Giải Mã Chi Tiết Cho AI")

        main_cards = [st.session_state.shuffled_deck[i] for i in st.session_state.picked_indices[:max_main]]
        clarity_card = st.session_state.shuffled_deck[st.session_state.picked_indices[max_main]] if current_picks > max_main else None

        prompt_content = generate_ai_prompt(
            question=question,
            spread_name=spread_name,
            picked_cards=main_cards,
            spread_slots=slots,
            clarity_card=clarity_card
        )

        st.text_area("Nội dung prompt tạo sẵn:", value=prompt_content, height=200)

        copy_btn_html = f"""
        <div style="margin-top: 8px;">
            <button id="copy-btn" onclick="copyPromptText()" style="
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #6366f1, #3b82f6);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
                transition: all 0.25s ease;
            ">📋 Bấm vào đây để Sao chép Prompt ngay</button>
        </div>
        <script>
        function copyPromptText() {{
            const text = `{prompt_content.replace('`', '\\`').replace('\\', '\\\\')}`;
            if (navigator.clipboard && window.isSecureContext) {{
                navigator.clipboard.writeText(text).then(showSuccess);
            }} else {{
                const ta = document.createElement("textarea");
                ta.value = text;
                ta.style.position = "fixed";
                ta.style.left = "-9999px";
                document.body.appendChild(ta);
                ta.focus();
                ta.select();
                try {{
                    document.execCommand('copy');
                    showSuccess();
                }} catch (err) {{
                    alert('Vui lòng bôi đen ô văn bản phía trên để sao chép.');
                }}
                document.body.removeChild(ta);
            }}
        }}
        function showSuccess() {{
            const btn = document.getElementById('copy-btn');
            btn.innerText = '✅ Đã sao chép! Chúc bạn nhận được lời giải sáng rõ nhất ✨';
            btn.style.background = '#10b981';
        }}
        </script>
        """
        components.html(copy_btn_html, height=70)

        # Hòm gieo duyên tinh tế ngay dưới nút copy
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("✨ Gieo duyên chút lộc trà đá để 'lấy vía' quẻ bài linh ứng? (Tùy tâm)", expanded=False):
            col_tip_text, col_tip_qr = st.columns([3, 2])
            with col_tip_text:
                st.markdown(textwrap.dedent("""
                <div style="font-size: 13.5px; line-height: 1.6; color: #cbd5e1;">
                    🔮 <b>Vạn sự tùy tâm - Năng lượng tuần hoàn:</b><br>
                    Để tạo ra một trải bài chỉnh chu với đầy đủ 78 lá, nguyên tố và vị trí sâu sắc như trên, hệ thống tiêu tốn khá nhiều chi phí duy trì server và token AI.<br><br>
                    Nếu thông điệp này chạm đến bạn, bạn có thể <i>"gieo duyên"</i> một ly trà đá <b>10k - 20k</b> để tiếp sức cho tác giả nuôi server, cũng là một cách trao đi năng lượng tích cực lấy vía lành nhé! ☕🙏
                </div>
                """), unsafe_allow_html=True)
            with col_tip_qr:
                BANK_ID = "MB"
                ACCOUNT_NO = "43737918062006"
                ACCOUNT_NAME = "NGUYEN HUU VANG"
                DEFAULT_MEMO = "Gieo duyen Tarot"
                
                vietqr_mini = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?accountName={ACCOUNT_NAME.replace(' ', '%20')}&addInfo={DEFAULT_MEMO.replace(' ', '%20')}&amount=10000"
                
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 12px; padding: 12px; text-align: center;">
                    <img src="{vietqr_mini}" style="width: 100%; max-width: 160px; border-radius: 8px; margin-bottom: 6px;" alt="VietQR" />
                    <div style="font-size: 11px; color: #94a3b8;">MB Bank: <b>{ACCOUNT_NO}</b></div>
                    <div style="font-size: 11px; color: #a5b4fc;">{ACCOUNT_NAME}</div>
                </div>
                """, unsafe_allow_html=True)


# ==========================================
# 2. VIEW: LÁ SỐ TỬ VI (MODULE MỞ RỘNG)
# ==========================================
def render_tu_vi_view():
    st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 2px;'>📜 Tra Cứu & Luận Giải Lá Số Tử Vi</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Nhập thông tin bản mệnh để lập bàn cờ Tử Vi Đẩu Số 12 Cung và luận giải thiên mệnh</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Họ và tên đương số:", placeholder="Ví dụ: Nguyễn Văn A", key="tuvi_name")
        gender = st.radio("⚧ Giới tính:", ["Nam (Dương Nam / Âm Nam)", "Nữ (Dương Nữ / Âm Nữ)"], horizontal=True)
        dob = st.date_input("📅 Ngày tháng năm sinh (Dương lịch):", value=datetime.date(2000, 1, 1), min_value=datetime.date(1940, 1, 1))

    with col2:
        hours_options = [
            "Tí (23h00 - 00h59)", "Sửu (01h00 - 02h59)", "Dần (03h00 - 04h59)",
            "Mão (05h00 - 06h59)", "Thìn (07h00 - 08h59)", "Tị (09h00 - 10h59)",
            "Ngọ (11h00 - 12h59)", "Mùi (13h00 - 14h59)", "Thân (15h00 - 16h59)",
            "Dậu (17h00 - 18h59)", "Tuất (19h00 - 20h59)", "Hợi (21h00 - 22h59)"
        ]
        birth_hour = st.selectbox("⏰ Giờ sinh (Địa chi):", options=hours_options, index=6)
        view_focus = st.multiselect(
            "🎯 Lĩnh vực trọng tâm cần luận giải chi tiết:",
            ["Công danh & Sự nghiệp (Cung Quan Lộc)", "Tiền bạc & Tài vận (Cung Tài Bạch)", "Tình duyên & Hôn nhân (Cung Phu Thê)", "Sức khỏe & Tai ương (Cung Tật Ách)", "Gia đạo & Bất động sản (Cung Điền Trạch)", "Vận hạn năm nay"],
            default=["Công danh & Sự nghiệp (Cung Quan Lộc)", "Tiền bạc & Tài vận (Cung Tài Bạch)"]
        )

    btn_calc = st.button("🌟 Lập Lá Số & Tạo Prompt Luận Giải AI", use_container_width=True, type="primary")

    if btn_calc or name.strip():
        st.markdown("### 🏛️ Bàn Cờ 12 Cung Bản Mệnh")
        cung_list = [
            ("Mệnh", "Ngoại hình, tính cách, số phận tổng quát"),
            ("Phụ Mẫu", "Duyên nợ cha mẹ, sự nâng đỡ gia đình"),
            ("Phúc Đức", "Phúc ấm tổ tiên, đời sống tinh thần"),
            ("Điền Trạch", "Đất đai, nhà cửa, cơ ngơi tích lũy"),
            ("Quan Lộc", "Đường học vấn, sự nghiệp, chức vị"),
            ("Nô Bộc", "Bạn bè, cấp dưới, quý nhân phù trợ"),
            ("Thiên Di", "Xuất hành, môi trường xã hội bên ngoài"),
            ("Tật Ách", "Bệnh tật tiềm ẩn, tai ương cần phòng"),
            ("Tài Bạch", "Năng lực kiếm tiền, đường tài lộc"),
            ("Tử Tức", "Đường con cái, thế hệ kế cận"),
            ("Phu Thê", "Đặc điểm hôn phối, hạnh phúc gia đạo"),
            ("Huynh Đệ", "Mối quan hệ anh chị em ruột thịt")
        ]

        c_cols = st.columns(4)
        for i, (c_name, c_desc) in enumerate(cung_list):
            with c_cols[i % 4]:
                st.markdown(textwrap.dedent(f"""
                <div style="background: rgba(30, 41, 59, 0.75); border: 1px solid #3b82f6; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 6px 16px rgba(0,0,0,0.5);">
                    <div style="font-weight: 700; color: #38bdf8; font-size: 15px;">Cung {c_name}</div>
                    <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 4px;">{c_desc}</div>
                </div>
                """), unsafe_allow_html=True)

        st.markdown("### 📋 Prompt Gửi Chuyên Gia Tử Vi AI")
        prompt_tuvi = f"""Tôi cần bạn đóng vai một Chuyên gia Tử Vi Đẩu Số uyên bác, am tường thuật số Đông phương để an sao và luận giải chi tiết lá số:
- Họ tên đương số: {name.strip() if name.strip() else 'Ẩn danh'}
- Giới tính: {gender}
- Ngày sinh Dương lịch: {dob.strftime('%d/%m/%Y')}
- Giờ sinh: {birth_hour}
- Trọng tâm cần luận giải: {', '.join(view_focus) if view_focus else 'Tổng quan đại vận'}

Yêu cầu phân tích:
1. Xác định Can Chi năm/tháng/ngày/giờ, Ngũ hành nạp âm bản mệnh và Cục số (Thủy nhị cục, Mộc tam cục,...).
2. Bình giải thế đứng Cung Mệnh & Thân (Chính tinh tọa thủ, đắc/hãm địa, các cặp trung tinh Tả Phụ Hữu Bật, Xương Khúc, Khôi Việt...).
3. Luận giải chi tiết các cung trọng tâm mà đương số yêu cầu.
4. Đưa ra lời khuyên cải mệnh thực tế, tu thân tích đức và các lưu ý về thời vận."""

        st.text_area("Prompt Tử Vi:", value=prompt_tuvi, height=200)


# ==========================================
# 3. VIEW: BÓI BÀI TÂY (52 LÁ CARTOMANCY)
# ==========================================
def render_bai_tay_view():
    st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 2px;'>🃏 Bói Bài Tây (Cartomancy 52 Lá)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Dự đoán tài lộc, tình duyên, công việc qua 4 chất Cơ (Hearts) - Rô (Diamonds) - Chuồn (Clubs) - Bích (Spades)</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns([3, 2])
    with col1:
        question = st.text_input("💬 Nhập vấn đề bạn muốn bói bài Tây:", placeholder="Ví dụ: Khoản đầu tư hoặc tiền bạc tuần tới thế nào?", key="baitay_q")
    with col2:
        spread_type = st.selectbox("🎴 Kiểu trải bài Tây:", ["Trải 3 lá (Quá khứ - Hiện tại - Tương lai)", "Trải 5 lá (Ngũ hành sinh khắc)", "Trải Tình Duyên (Đôi bên hòa hợp)"])

    suits_info = [
        ("♥️ Cơ (Hearts)", "Nước / Cảm xúc, tình yêu, mối quan hệ, hôn nhân"),
        ("♦️ Rô (Diamonds)", "Đất / Tiền bạc, tài chính, hợp đồng, giấy tờ"),
        ("♣️ Chuồn (Clubs)", "Lửa / Công việc, học hành, sự nghiệp, giao thiệp"),
        ("♠️ Bích (Spades)", "Khí / Thử thách, trở ngại, sức khỏe, biến cố")
    ]

    st.markdown("#### 📖 Ý nghĩa 4 chất bài:")
    s_cols = st.columns(4)
    for i, (s_name, s_desc) in enumerate(suits_info):
        with s_cols[i]:
            st.markdown(textwrap.dedent(f"""
            <div style="background: rgba(30,41,59,0.7); border: 1px solid #475569; border-radius: 10px; padding: 12px; text-align: center;">
                <div style="font-weight: 700; color: #f1f5f9; font-size: 14px;">{s_name}</div>
                <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">{s_desc}</div>
            </div>
            """), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Xáo & Rút 3 Lá Bài Tây", use_container_width=True, type="primary"):
        ranks = ["Át", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suits = ["Cơ ♥️", "Rô ♦️", "Chuồn ♣️", "Bích ♠️"]
        drawn = [f"{random.choice(ranks)} {random.choice(suits)}" for _ in range(3)]
        
        d_cols = st.columns(3)
        positions = ["Quá khứ / Nguyên nhân", "Hiện tại / Thực trạng", "Tương lai / Kết quả"]
        for idx, c in enumerate(d_cols):
            with c:
                st.markdown(textwrap.dedent(f"""
                <div style="background: linear-gradient(135deg, #1e1b4b, #0f172a); border: 2px solid #8b5cf6; border-radius: 14px; padding: 24px 12px; text-align: center;">
                    <div style="font-size: 12px; color: #a5b4fc; text-transform: uppercase; font-weight: 700;">{positions[idx]}</div>
                    <div style="font-size: 26px; font-weight: 800; color: #f8fafc; margin: 12px 0;">{drawn[idx]}</div>
                </div>
                """), unsafe_allow_html=True)

        prompt_baitay = f"""Tôi có câu hỏi bói bài Tây: "{question}"
Kiểu trải: "{spread_type}"
3 Lá bài được rút:
1. {positions[0]}: {drawn[0]}
2. {positions[1]}: {drawn[1]}
3. {positions[2]}: {drawn[2]}

Hãy đóng vai Thầy bói bài Tây dân gian kết hợp tâm lý học hiện đại để luận giải ý nghĩa kết hợp giữa chất (Cơ/Rô/Chuồn/Bích) và số (Át đến K), đồng thời đưa ra lời khuyên thực tế."""
        st.text_area("Prompt Bài Tây:", value=prompt_baitay, height=180)


# ==========================================
# 4. VIEW: TIẾP SỨC KEY AI & SERVER (DONATE ĐỘC LẬP)
# ==========================================
def render_donate_view():
    st.markdown("<h2 style='text-align: center; color: #f8fafc; margin-bottom: 2px;'>☕ Tiếp Sức Server & Quỹ Mua Key AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Đóng góp duy trì hạn ngạch Quota Token AI, hosting server mượt mà và không bị nghẽn mạng</p>", unsafe_allow_html=True)
    st.divider()

    col_info, col_qr = st.columns([3, 2])

    with col_info:
        st.markdown("### 🎯 Dự án vận hành phi lợi nhuận")
        st.markdown("""
        Mỗi lần trải bài và phân tích chi tiết đều tiêu tốn một lượng **Token AI** nhất định. 
        Mọi sự ủng hộ của bạn đều được quy đổi trực tiếp thành năng lượng vận hành:
        - ⚡ **Mua Token/Key API**: Duy trì tốc độ phản hồi nhanh, không lo hết Quota.
        - ☁️ **Chi phí Server Hosting**: Giúp website luôn online 24/7 ổn định cho mọi người.
        - 🛠️ **Phát triển tính năng mới**: Nâng cấp thuật toán an sao Tử Vi và mở rộng bói Bài Tây.
        """)

        st.markdown("#### 🎁 Chọn gói tiếp năng lượng:")
        packages = {
            "🍵 10k - Gói Cốc Trà Đá": (10000, "Cảm ơn bạn! Đủ duy trì thêm 500 lượt rút bài mượt mà."),
            "☕ 25k - Gói Ly Cà Phê AI": (25000, "Tuyệt vời! Bơm thêm năng lượng cho AI luận giải sắc bén."),
            "⚡ 50k - Gói 100.000 Tokens": (50000, "Siêu cấp! Đóng góp đáng kể vào quỹ API Gemini/OpenAI."),
            "👑 100k - Gói Đấng Cứu Thế Server": (100000, "Bái phục đại gia! Server sống khỏe re cả tháng."),
            "🌟 Tùy tâm đóng góp": (0, "Mọi sự đóng góp tùy tâm đều vô cùng quý giá!")
        }

        selected_pkg = st.radio(
            "Lựa chọn mức ủng hộ:",
            options=list(packages.keys()),
            index=1
        )
        amount, pkg_note = packages[selected_pkg]
        st.info(f"💡 {pkg_note}")

    with col_qr:
        BANK_ID = "MB"
        ACCOUNT_NO = "43737918062006"
        ACCOUNT_NAME = "NGUYEN HUU VANG"
        DEFAULT_MEMO = "Tiep suc AI Tarot"

        amount_query = f"&amount={amount}" if amount > 0 else ""
        vietqr_url = f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png?accountName={ACCOUNT_NAME.replace(' ', '%20')}&addInfo={DEFAULT_MEMO.replace(' ', '%20')}{amount_query}"

        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.75); border: 1px solid #6366f1; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <div style="font-weight: 700; color: #a5b4fc; font-size: 16px; margin-bottom: 12px;">📱 Quét Mã VietQR Bằng App Ngân Hàng</div>
            <img src="{vietqr_url}" style="width: 100%; max-width: 240px; border-radius: 12px; border: 2px solid #475569;" alt="VietQR" />
            <div style="margin-top: 14px; text-align: left; background: rgba(15, 23, 42, 0.8); padding: 12px; border-radius: 10px; font-size: 13px; line-height: 1.6;">
                <div>🏦 <b>Ngân hàng</b>: <span style="color: #38bdf8; font-weight: 700;">MB (Quân Đội)</span></div>
                <div>🔢 <b>Số tài khoản</b>: <span style="color: #38bdf8; font-weight: 700; font-size: 15px;">{ACCOUNT_NO}</span></div>
                <div>👤 <b>Chủ tài khoản</b>: <b>{ACCOUNT_NAME}</b></div>
                <div>📝 <b>Nội dung CK</b>: <span style="color: #c084fc;">{DEFAULT_MEMO}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 5. THANH TÁC VỤ BÊN TRÁI (SIDEBAR) & ĐIỀU HƯỚNG
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🌌 Mystic Hub</h2>", unsafe_allow_html=True)
    st.caption("<div style='text-align: center; color: #94a3b8; margin-bottom: 20px;'>Hệ Thống Huyền Học Đa Năng</div>", unsafe_allow_html=True)

    app_mode = st.radio(
        "🔮 Chọn hình thức chiêm đoán:",
        options=[
            "🔮 Xem Tarot (78 Lá)",
            "📜 Xem Lá Số Tử Vi",
            "🃏 Xem Bài Tây (52 Lá)",
            "☕ Tiếp Sức Key AI (Donate)"
        ],
        index=0
    )

    st.divider()
    st.markdown("#### ⚙️ Thông tin hệ thống")
    st.info("Phiên bản: **v2.5 Mystic Hub**\n\nKiến trúc: Modular Domain-Driven Engine")


# Điều hướng View
if app_mode == "🔮 Xem Tarot (78 Lá)":
    render_tarot_view()
elif app_mode == "📜 Xem Lá Số Tử Vi":
    render_tu_vi_view()
elif app_mode == "🃏 Xem Bài Tây (52 Lá)":
    render_bai_tay_view()
elif app_mode == "☕ Tiếp Sức Key AI (Donate)":
    render_donate_view()