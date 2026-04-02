# pages/profile.py
import streamlit as st
import sys, os, base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import logout, update_user
from persistence import save_session_state, init_session_state

# ─── HIDE SIDEBAR ─────────────────────────────────────────────────────────────
st.markdown("""<style>section[data-testid="stSidebar"]{display:none!important;}</style>""",
            unsafe_allow_html=True)

# ─── AUTH GUARD ───────────────────────────────────────────────────────────────
from streamlit_cookies_controller import CookieController
from db import SessionsManager

# Khởi tạo cookie_manager DUY NHẤT một lần ở đầu file
cookie_manager = CookieController()

def restore_auth():
    """Sync with dashboard.py - Cookie priority, silent restore"""
    # 1. Session already has user_id
    if st.session_state.get("user_id"):
        return st.session_state["user_id"]

    token = None
    
    # 2. PRIORITY: Cookie (persists across restarts)
    try:
        token = cookie_manager.get("session_token")
    except Exception:
        pass
    
    # 3. Fallback: session_state  
    if not token:
        token = st.session_state.get("session_token")

    if not token:
        return None  # Silent - UI handles gracefully

    # 4. Validate token with MongoDB
    try:
        user_id = SessionsManager().get_user_by_token(token)
    except Exception:
        # Clear invalid cookie
        try:
            cookie_manager.delete("session_token")
        except:
            pass
        return None

    if not user_id:
        # Clear invalid storage
        st.markdown("""
        <script>
        localStorage.removeItem('session_token');
        </script>
        """, unsafe_allow_html=True)
        try:
            cookie_manager.delete("session_token")
        except:
            pass
        st.session_state.pop("session_token", None)
        return None

    # 5. Load user profile into session
    try:
        from user_auth import UserManager
        user_doc = UserManager().get_user(user_id)
        if user_doc:
            st.session_state["user_id"] = user_id
            st.session_state["session_token"] = token
            st.session_state["user_sheets_config"] = user_doc.get("sheets_config", [])
            st.session_state["display_name"] = user_doc.get("display_name", user_id)
            st.session_state["avatar_path"] = user_doc.get("avatar_path")
            
            # ENSURE cookie is set for persistence
            try:
                cookie_manager.set("session_token", token, max_age=72*3600)
            except:
                pass
        else:
            return None
    except Exception:
        return None

    return st.session_state.get("user_id")


user_id = restore_auth()

if not user_id:
    st.switch_page("pages/auth.py")

init_session_state()

# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif; }
.stApp { background: #f5f7fa; color: #1a202c; }

.hero-card {
    background: linear-gradient(135deg, #ffffff 0%, #ebf4ff 60%, #dbeafe 100%);
    border: 1px solid rgba(66,153,225,0.18);
    border-radius: 20px; padding: 28px;
    display: flex; align-items: center; gap: 28px;
    margin-bottom: 28px; position: relative; overflow: hidden;
    box-shadow: 0 2px 16px rgba(66,153,225,0.08);
}
.hero-card::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,179,237,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.avatar-ring {
    width: 90px; height: 90px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 36px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.hero-info h2 {
    font-family: 'Playfair Display', serif; font-size: 1.55rem;
    font-weight: 600; color: #1a202c; margin: 0 0 4px;
}
.hero-info p { font-size: 0.82rem; color: #718096; margin: 0; }
.status-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: #48bb78; margin-right: 6px; box-shadow: 0 0 6px #48bb78;
}
.section-title {
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.5px; color: #3182ce; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after { content: ''; flex: 1; height: 1px; background: rgba(66,153,225,0.2); }
.stTabs [data-baseweb="tab-list"] {
    background: #edf2f7; border-radius: 10px; padding: 4px;
    gap: 2px; border: 1px solid rgba(0,0,0,0.06); margin-bottom: 24px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #718096;
    font-family: 'Be Vietnam Pro', sans-serif;
    font-size: 0.85rem; font-weight: 500; padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important; color: #1a202c !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTextInput > div > div > input {
    background: #ffffff !important; border: 1px solid #d1d5db !important;
    border-radius: 10px !important; color: #1a202c !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 0.88rem !important; padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4299e1 !important;
    box-shadow: 0 0 0 3px rgba(66,153,225,0.15) !important;
}
.stTextInput label {
    font-size: 0.78rem !important; font-weight: 500 !important;
    color: #4a5568 !important;
}
.stFileUploader > div {
    background: #f8fafc !important;
    border: 1px dashed rgba(66,153,225,0.4) !important;
    border-radius: 12px !important;
}
.stButton > button {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    border-radius: 10px !important; padding: 10px 20px !important;
    transition: all 0.2s !important; border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4299e1, #2b6cb0) !important;
    color: #fff !important; box-shadow: 0 4px 14px rgba(66,153,225,0.3) !important;
}
.stButton > button:not([kind]) {
    background: #ffffff !important; color: #4a5568 !important;
    border: 1px solid #d1d5db !important;
}
hr { border-color: #e2e8f0 !important; }
.logout-btn rect { transition: fill 0.2s; }
.logout-btn path { transition: stroke 0.2s; }
.logout-btn:hover rect { fill: #fee2e2 !important; }
.logout-btn:hover path { stroke: #c53030 !important; }
</style>
""", unsafe_allow_html=True)

# ─── BACK BUTTON ──────────────────────────────────────────────────────────────
if st.button("← Quay lại Dashboard"):
    st.switch_page("dashboard.py")

st.markdown("<br>", unsafe_allow_html=True)

# ─── RELOAD AVATAR TỪ DB ─────────────────────────────────────────────────────
try:
    from user_auth import UserManager
    um = UserManager()
    user_doc = um.users.find_one({'username': user_id})
    if user_doc:
        st.session_state.avatar_path = user_doc.get('avatar_path')
except:
    pass

avatar_path  = st.session_state.get('avatar_path')
display_name = st.session_state.get('display_name', user_id)

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
    avatar_html = f'<div class="avatar-ring" style="background:#3b82f6;">{initials}</div>'

st.markdown(f"""
<div class="hero-card">
    {avatar_html}
    <div class="hero-info">
        <h2>{display_name or user_id}</h2>
        <p><span class="status-dot"></span>Đang hoạt động &nbsp;·&nbsp; {user_id}</p>
    </div>
    <div style="margin-left:auto; flex-shrink:0;">
        <a href="?logout=1" target="_self" class="logout-btn" style="display:inline-flex;align-items:center;border-radius:50%;text-decoration:none;">
            <svg width="59" height="59" viewBox="0 0 59 59" fill="none" xmlns="http://www.w3.org/2000/svg">
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

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  📝  Thông tin cá nhân  ", "  🌐  Quản lý Domain  "])

with tab1:
    st.markdown('<div class="section-title">✦ Thông tin hiển thị</div>', unsafe_allow_html=True)
    new_display_name = st.text_input("Họ và tên", value=display_name, placeholder="Nhập họ và tên...", help="Tối thiểu 2 ký tự")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">✦ Ảnh đại diện</div>', unsafe_allow_html=True)
    avatar_file = st.file_uploader("Kéo thả hoặc nhấn để chọn ảnh", type=["png", "jpg", "jpeg"], key="avatar_upload")
    new_avatar_path = avatar_path

    if avatar_file is not None:
        os.makedirs("avatars", exist_ok=True)
        new_avatar_path = f"avatars/{user_id}.png"
        with open(new_avatar_path, "wb") as f:
            f.write(avatar_file.read())
        st.session_state.avatar_path = new_avatar_path
        current_display_name = st.session_state.get('display_name', user_id)
        current_sheets_config = st.session_state.get('user_sheets_config', [])
        success, msg = update_user(user_id, current_display_name, current_sheets_config, avatar=new_avatar_path)
        if success:
            save_session_state()
            st.success("✅ Ảnh đại diện đã được tải lên và lưu!")
            st.rerun()
        else:
            st.error(f"❌ Lỗi lưu ảnh: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">✦ Đổi mật khẩu</div>', unsafe_allow_html=True)
    old_password     = st.text_input("Mật khẩu hiện tại", type="password", placeholder="••••••••")
    new_password     = st.text_input("Mật khẩu mới",      type="password", placeholder="••••••••")
    confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password", placeholder="••••••••")

with tab2:
    user_sheets_config = st.session_state.get('user_sheets_config', [])
    st.markdown('<div class="section-title">✦ Google Sheets Domain</div>', unsafe_allow_html=True)
    num_domains = st.number_input("Số lượng domain", min_value=1, max_value=10, value=max(1, len(user_sheets_config)))
    new_sheets_config = []
    for i in range(int(num_domains)):
        with st.expander(f"🔗  Domain {i+1}", expanded=(i == 0)):
            c1, c2, c3 = st.columns([2, 2, 2])
            with c1:
                domain = st.text_input("Tên domain",
                    value=user_sheets_config[i]['domain'] if i < len(user_sheets_config) else '',
                    key=f"prof_domain_{i}", placeholder="example.com")
            with c2:
                sheet_id = st.text_input("Google Sheet ID",
                    value=user_sheets_config[i].get('sheet_id', '') if i < len(user_sheets_config) else '',
                    key=f"prof_sheet_{i}", placeholder="1BxiMVs0XRA5...")
            with c3:
                worksheet = st.text_input("Tên worksheet",
                    value=user_sheets_config[i].get('worksheet', 'Ngày_22_01_2026') if i < len(user_sheets_config) else 'Ngày_22_01_2026',
                    key=f"prof_ws_{i}", placeholder="Sheet1")
            if domain.strip() and sheet_id:
                new_sheets_config.append({"domain": domain.strip(), "sheet_id": sheet_id.strip(), "worksheet": worksheet.strip()})

# ─── ACTION BUTTONS ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">✦ Hành động</div>', unsafe_allow_html=True)

col_save, col_save_domains, col_pw_btn = st.columns([3, 3, 3])

with col_save:
    if st.button("💾  Lưu thông tin cá nhân", type="primary", use_container_width=True):
        current_sheets_config = st.session_state.get('user_sheets_config', [])
        success, msg = update_user(user_id, new_display_name, current_sheets_config, avatar=None)
        if success:
            st.session_state.display_name = new_display_name
            save_session_state()
            st.success(f"✅ {msg}!")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

with col_save_domains:
    if st.button("💾  Lưu Domain", use_container_width=True):
        current_display_name = st.session_state.get('display_name', display_name)
        success, msg = update_user(user_id, current_display_name, new_sheets_config, avatar=None)
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
                                       old_password=old_password, new_password=new_password)
            st.success(f"✅ {msg}!") if success else st.error(f"❌ {msg}")