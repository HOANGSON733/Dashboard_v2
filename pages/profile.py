import streamlit as st
import sys, os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, logout, is_authenticated, update_user
from config import setup_page_config
from persistence import save_session_state, init_session_state, load_auth_state_file
from user_auth import validate_session

# ─── HIDE SIDEBAR ──────────────────────────────────────────────────────────────
st.markdown("""<style>section[data-testid="stSidebar"]{display:none!important;}</style>""",
            unsafe_allow_html=True)

# ─── AUTH GUARD ────────────────────────────────────────────────────────────────
# ─── NEW SECURE AUTH GUARD WITH FILE PERSISTENCE ──
user_id = st.session_state.get('user_id')
if not user_id:
    # Try to load from file (for F5 refresh)
    user_id = load_auth_state_file()
    if user_id:
        st.session_state.user_id = user_id

if not validate_session():
    st.switch_page("pages/auth.py")
init_session_state()

setup_page_config()

# ─── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Be Vietnam Pro', sans-serif;
}
.stApp {
    background: #f5f7fa;
    color: #1a202c;
}

/* ── Page wrapper ── */
.profile-wrapper {
    max-width: 780px;
    margin: 0 auto;
    padding: 0 8px 80px;
}

/* ── Hero card ── */
.hero-card {
    background: linear-gradient(135deg, #ffffff 0%, #ebf4ff 60%, #dbeafe 100%);
    border: 1px solid rgba(66,153,225,0.18);
    border-radius: 20px;
    padding: 28px;
    display: flex;
    align-items: center;
    gap: 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(66,153,225,0.08);
}
.hero-card::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,179,237,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.avatar-ring {
    width: 90px; height: 90px;
    border-radius: 50%;
    
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; font-weight: 700; color: #fff;
    flex-shrink: 0;
    
}
.hero-info h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    font-weight: 600;
    color: #1a202c;
    margin: 0 0 4px;
}
.hero-info p {
    font-size: 0.82rem;
    color: #718096;
    margin: 0;
    letter-spacing: 0.3px;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #48bb78;
    margin-right: 6px;
    box-shadow: 0 0 6px #48bb78;
}

/* ── Section card ── */
.section-card {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
}
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #3182ce;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(66,153,225,0.2);
}

/* ── Tabs override ── */
.stTabs [data-baseweb="tab-list"] {
    background: #edf2f7;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border: 1px solid rgba(0,0,0,0.06);
    margin-bottom: 24px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #718096;
    font-family: 'Be Vietnam Pro', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 8px 20px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1a202c !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"]    { display: none; }

/* ── Input fields ── */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    color: #1a202c !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #4299e1 !important;
    box-shadow: 0 0 0 3px rgba(66,153,225,0.15) !important;
}
.stTextInput label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #4a5568 !important;
    letter-spacing: 0.2px;
    margin-bottom: 4px;
}

/* ── File uploader ── */
.stFileUploader > div {
    background: #f8fafc !important;
    border: 1px dashed rgba(66,153,225,0.4) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s;
}
.stFileUploader > div:hover {
    border-color: #4299e1 !important;
}

/* ── Number input ── */
.stNumberInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 10px !important;
    color: #1a202c !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #4a5568 !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 0.85rem !important;
}
.streamlit-expanderContent {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    border: none !important;
    letter-spacing: 0.2px;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4299e1, #2b6cb0) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(66,153,225,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #63b3ed, #3182ce) !important;
    box-shadow: 0 6px 20px rgba(66,153,225,0.45) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: #ffffff !important;
    color: #4a5568 !important;
    border: 1px solid #d1d5db !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: #f7fafc !important;
    color: #1a202c !important;
    border-color: #a0aec0 !important;
    transform: translateY(-1px);
}

/* ── Danger button (Đăng xuất) ── */
.btn-danger button {
    background: rgba(254,215,215,0.5) !important;
    color: #c53030 !important;
    border: 1px solid rgba(245,101,101,0.3) !important;
}
.btn-danger button:hover {
    background: rgba(254,215,215,0.85) !important;
    color: #9b2c2c !important;
    border-color: rgba(245,101,101,0.55) !important;
    transform: translateY(-1px);
}


/* ── Divider ── */
hr { border-color: #e2e8f0 !important; }

/* ── Alerts ── */
.stSuccess > div, .stError > div {
    border-radius: 10px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Sub-labels ── */
.field-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #4a5568;
    margin-bottom: 2px;
}
/* ── Action buttons alignment ── */
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}
</style>
""", unsafe_allow_html=True)
# ─── BACK BUTTON ──────────────────────────────────────────────────────────────
if st.button("← Quay lại Dashboard"):
    st.switch_page("dashboard.py")

st.markdown("<br>", unsafe_allow_html=True)
# ─── DATA ──────────────────────────────────────────────────────────────────────
# Safe reload avatar from DB
try:
    from user_auth import UserManager
    um = UserManager()
    # Get profile without password check
    user_doc = um.users.find_one({'username': user_id})
    if user_doc:
        st.session_state.avatar_path = user_doc.get('avatar_path')
except:
    pass

avatar_path    = st.session_state.get('avatar_path')
display_name   = st.session_state.get('display_name', user_id)

# ─── HERO CARD ────────────────────────────────────────────────────────────────
# ─── HERO CARD ────────────────────────────────────────────────────────────────
initials = (display_name or user_id or 'U')[0].upper()
try:
    if avatar_path and os.path.exists(avatar_path):
        with open(avatar_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        avatar_html = f'<img src="data:image/png;base64,{b64}" style="width:90px;height:90px;border-radius:50%;object-fit:cover;">'
    else:
        raise ValueError()
except Exception:
    avatar_html = f'<div class="avatar-ring">{initials}</div>'

# Nhúng nút logout thẳng vào HTML hero card qua query param
logout_key = st.session_state.get("_logout_trigger", 0)
st.markdown(f"""
<style>
.logout-btn rect {{ transition: fill 0.2s; }}
.logout-btn path {{ transition: stroke 0.2s; }}
.logout-btn:hover rect {{ fill: #fee2e2 !important; }}
.logout-btn:hover path {{ stroke: #c53030 !important; }}
</style>
<div class="hero-card">
    {avatar_html}
    <div class="hero-info">
        <h2>{display_name or user_id}</h2>
        <p><span class="status-dot"></span>Đang hoạt động &nbsp;·&nbsp; {user_id}</p>
    </div>
    <div style="margin-left:auto; flex-shrink:0;">
        <a href="?logout=1" target="_self" class="logout-btn" style="
            display: inline-flex; align-items: center;
            border-radius: 50%;
            text-decoration: none;
        "><svg width="59" height="59" viewBox="0 0 59 59" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="59" height="59" rx="29.5" fill="white"/>
<path d="M35.5 37L43 29.5M43 29.5L35.5 22M43 29.5H25M25 43H19C18.2044 43 17.4413 42.6839 16.8787 42.1213C16.3161 41.5587 16 40.7956 16 40V19C16 18.2044 16.3161 17.4413 16.8787 16.8787C17.4413 16.3161 18.2044 16 19 16H25" stroke="#0056C6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Xử lý logout qua query param
if st.query_params.get("logout") == "1":
    st.query_params.clear()
    logout()
    st.rerun()

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  📝  Thông tin cá nhân  ", "  🌐  Quản lý Domain  "])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — PERSONAL INFO
# ════════════════════════════════════════════════════════════════════
with tab1:

    # — Display name —
    st.markdown('<div class="section-title">✦ Thông tin hiển thị</div>', unsafe_allow_html=True)
    new_display_name = st.text_input(
        "Họ và tên",
        value=display_name,
        placeholder="Nhập họ và tên...",
        help="Tối thiểu 2 ký tự"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # — Avatar —
    st.markdown('<div class="section-title">✦ Ảnh đại diện</div>', unsafe_allow_html=True)
    avatar_file = st.file_uploader(
        "Kéo thả hoặc nhấn để chọn ảnh",
        type=["png", "jpg", "jpeg"],
        key="avatar_upload",
        help="Định dạng: PNG, JPG. Khuyến nghị ảnh vuông."
    )
    new_avatar_path = avatar_path  # Default to current avatar
    if avatar_file is not None:
        os.makedirs("avatars", exist_ok=True)
        new_avatar_path = f"avatars/{user_id}.png"
        with open(new_avatar_path, "wb") as f:
            f.write(avatar_file.read())
        # Update session state immediately when file is uploaded
        st.session_state.avatar_path = new_avatar_path
        
        # Save to DB immediately (AVATAR ONLY - keep current display_name & sheets_config)
        current_display_name = st.session_state.get('display_name', user_id)
        current_sheets_config = st.session_state.get('user_sheets_config', [])
        success, msg = update_user(
            user_id, current_display_name, current_sheets_config,
            avatar=new_avatar_path
        )
        if success:
            save_session_state()
            st.session_state.avatar_path = new_avatar_path  # Ensure sync
            st.success("✅ Ảnh đại diện đã được tải lên và lưu!")
            st.rerun()
        else:
            st.error(f"❌ Lỗi lưu ảnh: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)

    # — Password —
    st.markdown('<div class="section-title">✦ Đổi mật khẩu</div>', unsafe_allow_html=True)
    old_password     = st.text_input("Mật khẩu hiện tại", type="password", placeholder="••••••••")
    new_password     = st.text_input("Mật khẩu mới",      type="password", placeholder="••••••••")
    confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password", placeholder="••••••••")
        

# ════════════════════════════════════════════════════════════════════
# TAB 2 — DOMAIN MANAGEMENT
# ════════════════════════════════════════════════════════════════════
with tab2:
    user_sheets_config = st.session_state.get('user_sheets_config', [])

    st.markdown('<div class="section-title">✦ Google Sheets Domain</div>', unsafe_allow_html=True)

    num_domains = st.number_input(
        "Số lượng domain",
        min_value=1, max_value=10,
        value=max(1, len(user_sheets_config))
    )

    new_sheets_config = []
    for i in range(int(num_domains)):
        with st.expander(f"🔗  Domain {i+1}", expanded=(i == 0)):
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                domain = st.text_input(
                    "Tên domain",
                    value=user_sheets_config[i]['domain'] if i < len(user_sheets_config) else '',
                    key=f"prof_domain_{i}",
                    placeholder="example.com"
                )
            with c2:
                sheet_id = st.text_input(
                    "Google Sheet ID",
                    value=user_sheets_config[i].get('sheet_id', '') if i < len(user_sheets_config) else '',
                    key=f"prof_sheet_{i}",
                    placeholder="1BxiMVs0XRA5..."
                )
            with c3:
                worksheet = st.text_input(
                    "Tên worksheet",
                    value=user_sheets_config[i].get('worksheet', 'Ngày_22_01_2026') if i < len(user_sheets_config) else 'Ngày_22_01_2026',
                    key=f"prof_ws_{i}",
                    placeholder="Sheet1"
                )
            if domain.strip() and sheet_id:
                new_sheets_config.append({
                    "domain":    domain.strip(),
                    "sheet_id":  sheet_id.strip(),
                    "worksheet": worksheet.strip()
                })

# ─── ACTION BUTTONS ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">✦ Hành động</div>', unsafe_allow_html=True)

col_save, col_save_domains, col_pw_btn = st.columns([3, 3, 3])

with col_save:
    if st.button("💾  Lưu thông tin cá nhân", type="primary", use_container_width=True):
        # PERSONAL ONLY - keep current sheets_config & avatar
        current_sheets_config = st.session_state.get('user_sheets_config', [])
        success, msg = update_user(
            user_id, new_display_name, current_sheets_config,
            avatar=None
        )
        if success:
            st.session_state.display_name = new_display_name
            save_session_state()
            st.success(f"✅ {msg}!")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

with col_save_domains:
    if st.button("💾  Lưu Domain", use_container_width=True):
        # DOMAIN ONLY - keep current display_name & avatar
        current_display_name = st.session_state.get('display_name', display_name)
        success, msg = update_user(
            user_id, current_display_name, new_sheets_config,
            avatar=None
        )
        if success:
            st.session_state.user_sheets_config = new_sheets_config
            save_session_state()
            st.success(f"✅ {msg}!")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

with col_pw_btn:
    if st.button("🔑  Đổi mật khẩu", use_container_width=True):
        if new_password != confirm_password:
            st.error("Mật khẩu xác nhận không khớp")
        elif len(new_password) < 6:
            st.error("Mật khẩu quá ngắn (tối thiểu 6 ký tự)")
        else:
            success, msg = update_user(user_id, display_name,
                                        st.session_state.get('user_sheets_config', []),
                                        old_password, new_password)
            st.success(f"✅ {msg}!") if success else st.error(f"❌ {msg}")
    st.markdown('</div>', unsafe_allow_html=True)
# with col_logout:
#     st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
#     if st.button("🚪  Đăng xuất", use_container_width=True):
#         logout()
#         st.rerun()
#     st.markdown('</div>', unsafe_allow_html=True)