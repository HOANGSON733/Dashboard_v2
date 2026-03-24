import streamlit as st
import sys, os, base64, pathlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, register_user, logout, is_authenticated
from config import setup_page_config
from persistence import save_session_state, clear_all_session_files, init_session_state

setup_page_config()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    background: #eef2f9 !important;
}

/* ── Hide Streamlit chrome ── */
section[data-testid="stSidebar"]  { display: none !important; }
header[data-testid="stHeader"]    { display: none !important; }
[data-testid="stToolbar"]         { display: none !important; }
footer                            { display: none !important; }
#MainMenu                         { display: none !important; }
[data-testid="stDecoration"]      { display: none !important; }
[data-testid="stStatusWidget"]    { display: none !important; }

/* ── Layout resets ── */
[data-testid="stMain"]               { padding: 0 !important; overflow: hidden !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] > section:first-child { padding: 0 !important; }
[data-testid="stVerticalBlock"]      { gap: 0 !important; }
div[data-testid="element-container"] { margin: 0 !important; padding: 0 !important; }

/* ── Full-height two columns ── */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    align-items: stretch !important;
    min-height: 100vh;
    width: 100% !important;
    flex-wrap: nowrap !important;    
}
[data-testid="stHorizontalBlock"] > div {
    padding: 0 !important;
    min-height: 100vh;
    flex-shrink: 0 !important; 
}
[data-testid="stHorizontalBlock"] > div:first-child {
    display: flex;
    flex-direction: column;
}
[data-testid="stHorizontalBlock"] > div:last-child {
    background: #eef2f9 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 24px 20px !important;
    overflow-y: auto !important;
    overflow-x: visible !important;
    min-height: 100vh;
    min-width: 340px !important;
}

/* ════ CARD via st.container(border=True) ════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    width: 100% !important;                                                                                                 
    max-width: 320px !important;
    background: #fff !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 6px 40px rgba(13,59,142,.13), 0 2px 8px rgba(0,0,0,.05) !important;
    overflow: hidden !important;
    padding: 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 24px 24px 28px !important;
    border: none !important;
}

/* ════ LEFT PANEL ════ */
.left-panel {
    flex: 1;
    background: linear-gradient(150deg, #0c3cbf 0%, #1557d4 45%, #0b2e9e 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 52px 44px;
    position: relative;
    overflow: hidden;
    border-radius: 0 28px 28px 0;
    min-height: 100vh;
}
.left-panel::before {
    content: '';
    position: absolute; top: -100px; right: -100px;
    width: 380px; height: 380px;
    background: radial-gradient(circle, rgba(255,255,255,.09) 0%, transparent 68%);
    border-radius: 50%; pointer-events: none;
}
.left-panel::after {
    content: '';
    position: absolute; bottom: -70px; left: -70px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,.07) 0%, transparent 68%);
    border-radius: 50%; pointer-events: none;
}
.left-panel .grid-bg {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
    background-size: 40px 40px;
}
.left-logo {
    width: 250px; 
    margin-left: -280px;margin-bottom: 48px;
    filter: drop-shadow(0 4px 18px rgba(0,0,0,.35));
    z-index: 1; position: relative;
}
.left-mockup {
    position: relative; width: 100%; max-width: 550px ;
    z-index: 1; margin-bottom: 36px;
}
.left-mockup .img-main {
    width: 100%; border-radius: 16px;
    box-shadow: 0 24px 64px rgba(0,0,0,.5); display: block;
}
.left-mockup .img-float {
    position: absolute; width: 55%; bottom: 220px; right: -60px;
    border-radius: 12px; box-shadow: 0 14px 40px rgba(0,0,0,.45);
    border: 3px solid rgba(255,255,255,.18);
}
.left-tagline { z-index:1; position:relative; text-align:center; color:#fff; margin-top:12px; }
.left-tagline h2 {
    font-size: 36px; font-weight: 700;
    letter-spacing: .6px; line-height: 1.4;
    margin-bottom: 14px; text-transform: uppercase;
}
.left-tagline p {
    font-size: 20px; opacity: .80;
    line-height: 1.7; max-width: 450px; margin: 0 auto;
}

/* ════ TABS ════ */
[data-testid="stTabs"] { margin: 0 !important; }
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #e4eaf5 !important;
    gap: 0 !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 0 4px 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 600 !important;
    font-size: .97rem !important;
    color: #9baabf !important;
    padding: 10px 28px !important;
    border-radius: 0 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important;
    transition: color .2s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #1557d4 !important;
    border-bottom: 3px solid #1557d4 !important;
}
[data-testid="stTabs"] button[role="tab"]:hover:not([aria-selected="true"]) {
    color: #4a6090 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
[data-testid="stTabsContent"] { padding: 24px 0 0 !important; }

/* ════ FORM HEADING ════ */
.form-heading {
    font-size: 1.45rem;
    font-weight: 700;
    color: #1557d4;
    margin-bottom: 20px;
    text-align: center;
    letter-spacing: -.2px;
    font-family: 'Be Vietnam Pro', sans-serif;
}

/* ════ FIELD LABEL ════ */
.field-label {
    font-size: .82rem;
    font-weight: 600;
    color: #3a4a6a;
    margin-bottom: 4px;
    margin-top: 12px;
    font-family: 'Be Vietnam Pro', sans-serif;
    line-height: 1;
}

/* ════ FORGOT LINK ════ */
.forgot-row { display: flex; justify-content: flex-end; margin-top: 4px; }
.forgot-row a {
    font-size: .8rem; color: #1557d4;
    text-decoration: none; font-weight: 500;
    font-family: 'Be Vietnam Pro', sans-serif;
}
.forgot-row a:hover { text-decoration: underline; }

/* ════ Hide default input labels (we use .field-label instead) ════ */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label { display: none !important; }

/* ════ TEXT INPUT — đồng đều height, style giống ảnh ════ */
[data-testid="stTextInput"] > div > div {
    height: 40px !important;
    min-height: 40px !important;
    display: flex !important;
    align-items: center !important;
    border: 1.5px solid #d0d8e8 !important;
    border-radius: 7px !important;
    background: #fff !important;
    box-shadow: none !important;
    overflow: hidden !important;
    transition: border-color .2s !important;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #1557d4 !important;
    box-shadow: 0 0 0 3px rgba(21,87,212,.10) !important;
}
[data-testid="stTextInput"] > div > div input {
    height: 40px !important;
    min-height: 40px !important;
    padding: 0 16px !important;
    border: none !important;
    outline: none !important;
    background: transparent !important;
    font-size: .95rem !important;
    color: #1c2e4a !important;
    font-family: "Be Vietnam Pro", sans-serif !important;
    box-shadow: none !important;
    flex: 1 !important;
}
[data-testid="stTextInput"] > div > div input::placeholder {
    color: #b0bccc !important;
}
/* eye icon — căn giữa theo chiều dọc */
[data-testid="stTextInput"] > div > div button {
    height: 52px !important;
    width: 48px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border: none !important;
    color: #9baabf !important;
    flex-shrink: 0 !important;
}

/* ════ BUTTON — FULL WIDTH ════ */
[data-testid="stButton"] {
    width: 100% !important;
    display: block !important;
}
[data-testid="stButton"] > button {
    width: 100% !important;
    display: block !important;
    background: #1557d4 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    height: 52px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
    cursor: pointer !important;
    margin-top: 20px !important;
    box-shadow: 0 4px 18px rgba(21,87,212,.28) !important;
    transition: background .2s, transform .15s, box-shadow .2s !important;
}
[data-testid="stButton"] > button:hover {
    background: #0d40b8 !important;
    box-shadow: 0 6px 24px rgba(13,59,142,.36) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }
[data-testid="stButton"] > button p {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #fff !important;
}

/* ════ ALERTS ════ */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: .88rem !important;
    margin-top: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Image helpers ──────────────────────────────────────────────────────────────
def img_b64(path: str) -> str:
    p = pathlib.Path(path)
    if p.exists():
        ext = p.suffix.lstrip(".").replace("jpg", "jpeg")
        return f"data:image/{ext};base64," + base64.b64encode(p.read_bytes()).decode()
    return ""

LOGO = img_b64(str(pathlib.Path(__file__).parent.parent / "LOGO1.png"))
ANH1 = img_b64(str(pathlib.Path(__file__).parent.parent / "anh1.jpg"))
ANH2 = img_b64(str(pathlib.Path(__file__).parent.parent / "anh2.jpg"))

# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([50, 50], gap="small")

# ════ LEFT ════════════════════════════════════
with left_col:
    logo_html = (
        f'<img class="left-logo" src="{LOGO}" alt="Sea Dragon Technology">'
        if LOGO else
        '<div style="color:#fff;font-size:1.8rem;font-weight:800;margin-bottom:28px;z-index:1;position:relative;"> SEA DRAGON</div>'
    )
    img_main_html = (
        f'<img class="img-main" src="{ANH1}" alt="Dashboard">'
        if ANH1 else
        '<div style="background:rgba(255,255,255,.13);height:220px;border-radius:16px;"></div>'
    )
    img_float_html = f'<img class="img-float" src="{ANH2}" alt="Stats">' if ANH2 else ""

    st.markdown(f"""
    <div class="left-panel">
        <div class="grid-bg"></div>
        {logo_html}
        <div class="left-mockup">
            {img_main_html}
            {img_float_html}
        </div>
        <div class="left-tagline">
            <h2>Giải pháp SEO toàn diện<br>cho doanh nghiệp</h2>
            <p>Website của chúng tôi được xây dựng nhằm cung cấp giải pháp SEO toàn diện,
            từ tối ưu kỹ thuật, nội dung đến chiến lược từ khóa, giúp nâng cao thứ hạng
            trên Google, thu hút lượng truy cập chất lượng và gia tăng chuyển đổi.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ════ RIGHT ═══════════════════════════════════
with right_col:
    with st.container():

        tab_login, tab_register = st.tabs(["Đăng Nhập", "Đăng Ký"])

        # ── ĐĂNG NHẬP ──────────────────────────
        with tab_login:
            st.markdown('<div class="form-heading">Thông tin đăng nhập</div>', unsafe_allow_html=True)

            st.markdown('<span class="field-label">Tên đăng nhập</span>', unsafe_allow_html=True)
            username = st.text_input(
                "login_user", placeholder="Tên tài khoản",
                label_visibility="collapsed"
            )

            st.markdown('<span class="field-label">Mật khẩu</span>', unsafe_allow_html=True)
            password = st.text_input(
                "login_pass", placeholder="••••••••",
                type="password", label_visibility="collapsed"
            )

            st.markdown(
                '<div class="forgot-row"><a href="#">Quên mật khẩu ?</a></div>',
                unsafe_allow_html=True
            )

            if st.button("Đăng Nhập", key="btn_login"):
                success, user_config = login_user(username, password)
                if success:
                    st.session_state.user_id            = username
                    st.session_state.display_name       = user_config.get("display_name", username)
                    st.session_state.user_sheets_config = user_config["sheets_config"]
                    # ✅ Clear then set avatar post-login
                    if 'avatar' in st.session_state:
                        del st.session_state['avatar']
                    st.session_state.avatar = user_config.get('avatar')
                    save_session_state()
                    init_session_state(restore_auth=True)
                    st.success("✅ Đăng nhập thành công!")
                    st.switch_page("dashboard.py")
                else:
                    st.error(f"❌ {user_config}")

        # ── ĐĂNG KÝ ────────────────────────────
        with tab_register:
            st.markdown('<div class="form-heading">Tạo tài khoản mới</div>', unsafe_allow_html=True)

            st.markdown('<span class="field-label">Họ và tên</span>', unsafe_allow_html=True)
            new_display_name = st.text_input(
                "reg_dn", placeholder="Nguyễn Văn A",
                label_visibility="collapsed", key="register_display_name"
            )

            st.markdown('<span class="field-label">Tên đăng nhập</span>', unsafe_allow_html=True)
            new_username = st.text_input(
                "reg_u", placeholder="username",
                label_visibility="collapsed", key="register_username"
            )

            st.markdown('<span class="field-label">Mật khẩu</span>', unsafe_allow_html=True)
            new_password = st.text_input(
                "reg_p", placeholder="••••••••",
                type="password", label_visibility="collapsed", key="register_password"
            )

            st.markdown('<span class="field-label">Xác nhận mật khẩu</span>', unsafe_allow_html=True)
            confirm_password = st.text_input(
                "reg_cp", placeholder="••••••••",
                type="password", label_visibility="collapsed", key="register_confirm"
            )

            st.markdown('<span class="field-label">Số domain</span>', unsafe_allow_html=True)
            num_domains = st.number_input(
                "reg_nd", min_value=1, max_value=10, value=1,
                label_visibility="collapsed"
            )

            sheets_config = []
            for i in range(int(num_domains)):
                with st.expander(f"Domain {i + 1}"):
                    domain    = st.text_input("Tên domain",      key=f"domain_{i}", placeholder="vd: example.com")
                    sheet_id  = st.text_input("Google Sheet ID", key=f"sheet_{i}",  placeholder="1abc...xyz")
                    worksheet = st.text_input(
                        "Tên worksheet", key=f"ws_{i}",
                        value="Ngày_22_01_2026", placeholder="Ngày_DD_MM_YYYY"
                    )
                    if domain and sheet_id:
                        sheets_config.append({
                            "domain":    domain.strip(),
                            "sheet_id":  sheet_id.strip(),
                            "worksheet": worksheet.strip(),
                        })

            if st.button("Đăng Ký", key="btn_register"):
                if new_password != confirm_password:
                    st.error("❌ Mật khẩu không khớp")
                elif len(new_username) < 3:
                    st.error("❌ Tên đăng nhập quá ngắn")
                elif len(new_display_name.strip()) < 2:
                    st.error("❌ Họ và tên quá ngắn")
                elif not sheets_config:
                    st.error("❌ Phải nhập ít nhất 1 domain đầy đủ")
                else:
                    success, msg = register_user(new_username, new_password, new_display_name, sheets_config)
                    if success:
                        succ, user_config = login_user(new_username, new_password)
                        if succ:
                            st.session_state.user_id            = new_username
                            st.session_state.display_name       = user_config.get("display_name", new_username)
                            st.session_state.user_sheets_config = user_config["sheets_config"]
                            # ✅ Clear then set avatar post-register
                            if 'avatar' in st.session_state:
                                del st.session_state['avatar']
                            st.session_state.avatar = user_config.get('avatar')
                            save_session_state()
                            init_session_state(restore_auth=True)
                            st.success(f"✅ Đăng ký thành công, chào {st.session_state.display_name}!")
                            st.switch_page("dashboard.py")
                        else:
                            st.success(f"✅ {msg}")
                            st.info("👆 Bây giờ bạn có thể đăng nhập")
                    else:
                        st.error(f"❌ {msg}")

# ── Already authenticated ──────────────────────────────────────────────────────
if is_authenticated():
    display = st.session_state.get("display_name", st.session_state.user_id)
    st.success(f"Đã đăng nhập: {display}")
    if st.button("🚪 Đăng xuất"):
        logout()
        clear_all_session_files()
        st.rerun()