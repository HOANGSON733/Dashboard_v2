import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, register_user, logout, is_authenticated
from config import setup_page_config
from persistence import save_session_state, clear_all_session_files, init_session_state

setup_page_config()

# ── CSS: full-page two-column layout ─────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ── */
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
    font-family: 'Be Vietnam Pro', sans-serif;
}

/* Hide Streamlit chrome */
section[data-testid="stSidebar"]          { display: none !important; }
header[data-testid="stHeader"]            { display: none !important; }
[data-testid="stToolbar"]                 { display: none !important; }
footer                                    { display: none !important; }
#MainMenu                                 { display: none !important; }
[data-testid="stDecoration"]              { display: none !important; }

/* ── Full-screen wrapper ── */
[data-testid="stAppViewContainer"] > section:first-child {
    padding: 0 !important;
}
[data-testid="stMain"] {
    padding: 0 !important;
    overflow: hidden;
}
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Two-column shell ── */
.login-shell {
    display: flex;
    min-height: 100vh;
    width: 100%;
}

/* ── LEFT PANEL ── */
.left-panel {
    width: 46%;
    min-width: 380px;
    background: linear-gradient(145deg, #0d3b8e 0%, #1557c0 50%, #0a2d6e 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 40px;
    position: relative;
    overflow: hidden;
}

/* decorative blobs */
.left-panel::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(255,255,255,.08) 0%, transparent 70%);
    border-radius: 50%;
}
.left-panel::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,255,255,.06) 0%, transparent 70%);
    border-radius: 50%;
}

.left-logo {
    width: 180px;
    margin-bottom: 28px;
    filter: drop-shadow(0 4px 16px rgba(0,0,0,.3));
    z-index: 1;
}

/* screenshot / mockup images */
.left-mockup {
    position: relative;
    width: 100%;
    max-width: 440px;
    z-index: 1;
    margin-bottom: 32px;
}
.left-mockup img.img-main {
    width: 100%;
    border-radius: 14px;
    box-shadow: 0 20px 60px rgba(0,0,0,.45);
}
.left-mockup img.img-float {
    position: absolute;
    width: 56%;
    bottom: -24px;
    right: -18px;
    border-radius: 10px;
    box-shadow: 0 12px 36px rgba(0,0,0,.4);
    border: 3px solid rgba(255,255,255,.15);
}

.left-tagline {
    z-index: 1;
    text-align: center;
    color: #fff;
}
.left-tagline h2 {
    font-size: 1.45rem;
    font-weight: 800;
    letter-spacing: .5px;
    line-height: 1.35;
    margin-bottom: 12px;
    text-transform: uppercase;
}
.left-tagline p {
    font-size: .88rem;
    font-weight: 400;
    opacity: .82;
    line-height: 1.65;
    max-width: 360px;
}

/* ── RIGHT PANEL ── */
.right-panel {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f7f9fc;
    padding: 40px 32px;
}

.right-card {
    width: 100%;
    max-width: 460px;
    background: #fff;
    border-radius: 20px;
    padding: 48px 44px;
    box-shadow: 0 8px 40px rgba(13,59,142,.10);
}

/* tabs */
.tab-row {
    display: flex;
    border-bottom: 2px solid #e8edf5;
    margin-bottom: 32px;
}
.tab-btn {
    flex: 1;
    padding: 12px 0;
    background: none;
    border: none;
    cursor: pointer;
    font-family: 'Be Vietnam Pro', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #8fa0bb;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: color .2s, border-color .2s;
}
.tab-btn.active {
    color: #1557c0;
    border-bottom-color: #1557c0;
}

/* form heading */
.form-heading {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1557c0;
    margin-bottom: 28px;
    text-align: center;
}

/* field labels */
.field-label {
    display: block;
    font-size: .82rem;
    font-weight: 600;
    color: #4a5a78;
    margin-bottom: 6px;
    margin-top: 16px;
}

/* override Streamlit inputs */
[data-testid="stTextInput"] > div > div > input {
    border: 1.5px solid #dce4f0 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: .95rem !important;
    color: #1c2e4a !important;
    background: #f7f9fc !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #1557c0 !important;
    box-shadow: 0 0 0 3px rgba(21,87,192,.12) !important;
    background: #fff !important;
}

/* forgot password link */
.forgot-link {
    text-align: right;
    margin-top: 6px;
}
.forgot-link a {
    font-size: .8rem;
    color: #1557c0;
    text-decoration: none;
    font-weight: 500;
}

/* primary button */
[data-testid="stButton"] > button {
    width: 100% !important;
    background: #1557c0 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: .3px !important;
    cursor: pointer !important;
    margin-top: 24px !important;
    transition: background .2s, transform .1s, box-shadow .2s !important;
    box-shadow: 0 4px 18px rgba(21,87,192,.28) !important;
}
[data-testid="stButton"] > button:hover {
    background: #0d3b8e !important;
    box-shadow: 0 6px 24px rgba(13,59,142,.35) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* hide label text for inputs (we provide our own) */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label { display: none !important; }

/* tabs native streamlit */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 2px solid #e8edf5 !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Be Vietnam Pro', sans-serif !important;
    font-weight: 600 !important;
    font-size: .98rem !important;
    color: #8fa0bb !important;
    padding: 10px 32px !important;
    border-radius: 0 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #1557c0 !important;
    border-bottom: 3px solid #1557c0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

/* expander */
[data-testid="stExpander"] {
    border: 1.5px solid #dce4f0 !important;
    border-radius: 10px !important;
    margin-top: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Paths ──────────────────────────────────────────────────────────────────────
import base64, pathlib

def img_b64(path: str) -> str:
    p = pathlib.Path(path)
    if p.exists():
        return "data:image/" + p.suffix.lstrip(".").replace("jpg","jpeg") + ";base64," + base64.b64encode(p.read_bytes()).decode()
    return ""

LOGO  = img_b64(r"D:\Salon\Dashboard\logo.png")
ANH1  = img_b64(r"D:\Salon\Dashboard\anh1.jpg")
ANH2  = img_b64(r"D:\Salon\Dashboard\anh2.jpg")

# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([46, 54], gap="small")

with left_col:
    logo_html = f'<img class="left-logo" src="{LOGO}" alt="Logo">' if LOGO else \
                '<div style="color:#fff;font-size:1.6rem;font-weight:800;margin-bottom:28px;">🐉 SEA DRAGON</div>'
    
    img_main_html = f'<img class="img-main" src="{ANH1}" alt="Dashboard">' if ANH1 else \
                    '<div style="background:rgba(255,255,255,.15);height:220px;border-radius:14px;"></div>'
    
    img_float_html = f'<img class="img-float" src="{ANH2}" alt="Stats">' if ANH2 else ""
    
    st.markdown(f"""
    <div class="left-panel">
        {logo_html}
        <div class="left-mockup">
            {img_main_html}
            {img_float_html}
        </div>
        <div class="left-tagline">
            <h2>Giải pháp SEO toàn diện<br>cho doanh nghiệp</h2>
            <p>Website của chúng tôi được xây dựng nhằm cung cấp giải pháp SEO toàn diện, từ tối ưu kỹ thuật, nội dung đến chiến lược từ khóa, giúp nâng cao thứ hạng trên Google, thu hút lượng truy cập chất lượng và gia tăng chuyển đổi.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="right-panel"><div class="right-card">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký"])
    
    with tab1:
        st.markdown('<div class="form-heading">Thông tin đăng nhập</div>', unsafe_allow_html=True)
        
        st.markdown('<span class="field-label">Tên đăng nhập</span>', unsafe_allow_html=True)
        username = st.text_input("u", placeholder="Tên tài khoản", label_visibility="collapsed")
        
        st.markdown('<span class="field-label">Mật khẩu</span>', unsafe_allow_html=True)
        password = st.text_input("p", placeholder="••••••••", type="password", label_visibility="collapsed")
        
        st.markdown('<div class="forgot-link"><a href="#">Quên mật khẩu ?</a></div>', unsafe_allow_html=True)
        
        if st.button("Đăng Nhập", key="btn_login"):
            success, user_config = login_user(username, password)
            if success:
                st.session_state.user_id = username
                st.session_state.display_name = user_config.get('display_name', username)
                st.session_state.user_sheets_config = user_config['sheets_config']
                save_session_state()
                init_session_state(restore_auth=True)
                st.success("✅ Đăng nhập thành công!")
                st.switch_page("dashboard.py")
            else:
                st.error(f"❌ {user_config}")
    
    with tab2:
        st.markdown('<div class="form-heading">Tạo tài khoản mới</div>', unsafe_allow_html=True)
        
        st.markdown('<span class="field-label">Họ và tên</span>', unsafe_allow_html=True)
        new_display_name = st.text_input("dn", placeholder="Nguyễn Văn A", label_visibility="collapsed", key="register_display_name")
        
        st.markdown('<span class="field-label">Tên đăng nhập</span>', unsafe_allow_html=True)
        new_username = st.text_input("nu", placeholder="username", label_visibility="collapsed", key="register_username")
        
        st.markdown('<span class="field-label">Mật khẩu</span>', unsafe_allow_html=True)
        new_password = st.text_input("np", placeholder="••••••••", type="password", label_visibility="collapsed", key="register_password")
        
        st.markdown('<span class="field-label">Xác nhận mật khẩu</span>', unsafe_allow_html=True)
        confirm_password = st.text_input("cp", placeholder="••••••••", type="password", label_visibility="collapsed", key="register_confirm")
        
        st.markdown('<span class="field-label">Số domain</span>', unsafe_allow_html=True)
        num_domains = st.number_input("nd", min_value=1, max_value=10, value=1, label_visibility="collapsed")
        
        sheets_config = []
        for i in range(int(num_domains)):
            with st.expander(f"Domain {i+1}"):
                domain    = st.text_input(f"Tên domain",      key=f"domain_{i}", placeholder="vd: example.com")
                sheet_id  = st.text_input(f"Google Sheet ID", key=f"sheet_{i}",  placeholder="1abc...xyz")
                worksheet = st.text_input(f"Tên worksheet",   key=f"ws_{i}",     value="Ngày_22_01_2026", placeholder="Ngày_DD_MM_YYYY")
                if domain and sheet_id:
                    sheets_config.append({"domain": domain.strip(), "sheet_id": sheet_id.strip(), "worksheet": worksheet.strip()})
        
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
                        st.session_state.user_id = new_username
                        st.session_state.display_name = user_config.get('display_name', new_username)
                        st.session_state.user_sheets_config = user_config['sheets_config']
                        save_session_state()
                        init_session_state(restore_auth=True)
                        st.success(f"✅ Đăng ký thành công, chào {st.session_state.display_name}!")
                        st.switch_page("dashboard.py")
                    else:
                        st.success(f"✅ {msg}")
                        st.info("👆 Bây giờ bạn có thể đăng nhập")
                else:
                    st.error(f"❌ {msg}")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Already logged in ──────────────────────────────────────────────────────────
if is_authenticated():
    display = st.session_state.get('display_name', st.session_state.user_id)
    st.success(f"Đã đăng nhập: {display}")
    if st.button("🚪 Đăng xuất"):
        logout()
        clear_all_session_files()
        st.rerun()