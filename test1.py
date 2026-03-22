import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, register_user, logout, is_authenticated
from config import setup_page_config
from persistence import save_session_state, clear_all_session_files, init_session_state

setup_page_config()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    height: 100%; font-family: 'Be Vietnam Pro', sans-serif;
}
section[data-testid="stSidebar"]     { display: none !important; }
header[data-testid="stHeader"]       { display: none !important; }
[data-testid="stToolbar"]            { display: none !important; }
footer                               { display: none !important; }
#MainMenu                            { display: none !important; }
[data-testid="stDecoration"]         { display: none !important; }

/* Remove ALL padding/margin from Streamlit wrappers */
[data-testid="stAppViewContainer"] > section:first-child { padding: 0 !important; }
[data-testid="stMain"]               { padding: 0 !important; margin: 0 !important; }
[data-testid="stMainBlockContainer"] {
    padding: 0 !important; margin: 0 !important;
    max-width: 100% !important;
}
/* This is the key: remove the default top padding Streamlit injects */
[data-testid="stMainBlockContainer"] > div:first-child {
    padding: 0 !important; margin: 0 !important;
}

/* ── Columns ── */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh !important;
}
[data-testid="stColumn"] {
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh !important;
}
[data-testid="stColumn"] > div:first-child {
    padding: 0 !important;
    margin: 0 !important;
    min-height: 100vh !important;
}
/* iframe fills column fully */
[data-testid="stColumn"]:first-child iframe {
    display: block !important;
    border: none !important;
    width: 100% !important;
    height: 100vh !important;
    min-height: 100vh !important;
}

/* ── Right column ── */
[data-testid="stColumn"]:nth-child(2) {
    background: #f0f4fb !important;
}
[data-testid="stColumn"]:nth-child(2) > div:first-child {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 100vh !important;
    padding: 40px 32px !important;
}
[data-testid="stColumn"]:nth-child(2) > div > div:first-child {
    width: 100% !important;
    max-width: 440px !important;
    background: #ffffff !important;
    border-radius: 24px !important;
    padding: 40px 40px 36px !important;
    box-shadow: 0 8px 40px rgba(18,82,190,.10), 0 1px 4px rgba(0,0,0,.04) !important;
    border: 1px solid #e4ecf7 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #edf0f7 !important; border-radius: 12px !important;
    padding: 4px !important; border: none !important; gap: 4px !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Be Vietnam Pro', sans-serif !important; font-weight: 700 !important;
    font-size: .88rem !important; color: #8fa0bb !important;
    border-radius: 9px !important; padding: 10px 0 !important; flex: 1 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #1252be !important; background: #fff !important;
    box-shadow: 0 2px 8px rgba(18,82,190,.12) !important; border-bottom: none !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* ── Form ── */
.form-heading {
    font-size: 1.5rem; font-weight: 900; color: #1252be;
    text-align: center; margin-bottom: 6px; margin-top: 20px; letter-spacing: -.3px;
}
.form-sub { font-size: .8rem; color: #a0aec0; text-align: center; margin-bottom: 20px; }
.field-label {
    display: block; font-size: .72rem; font-weight: 700; color: #5a6a85;
    margin-bottom: 6px; margin-top: 16px; letter-spacing: .4px; text-transform: uppercase;
}

/* ── Inputs ── */
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] input {
    border: 1.5px solid #dce4f0 !important; border-radius: 12px !important;
    padding: 12px 16px !important; font-family: 'Be Vietnam Pro', sans-serif !important;
    font-size: .92rem !important; color: #1c2e4a !important;
    background: #f7faff !important; height: 48px !important;
}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #1252be !important;
    box-shadow: 0 0 0 3px rgba(18,82,190,.1) !important; background: #fff !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label { display: none !important; }

.forgot-link { text-align: right; margin-top: 6px; }
.forgot-link a { font-size: .74rem; color: #1252be; text-decoration: none; font-weight: 600; }

/* ── Button ── */
[data-testid="stButton"] > button {
    width: 100% !important; height: 50px !important;
    background: linear-gradient(135deg, #1a5ed4 0%, #1252be 60%, #0d3b8e 100%) !important;
    color: #fff !important; border: none !important; border-radius: 13px !important;
    font-family: 'Be Vietnam Pro', sans-serif !important; font-size: .97rem !important;
    font-weight: 800 !important; margin-top: 22px !important;
    box-shadow: 0 4px 18px rgba(18,82,190,.35) !important;
    transition: transform .15s, box-shadow .2s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(18,82,190,.45) !important;
}

/* ── Divider / Social / Trust ── */
.or-divider {
    display: flex; align-items: center; gap: 12px; margin: 22px 0 16px;
    color: #c0cad8; font-size: .73rem; font-weight: 600;
    letter-spacing: .3px; text-transform: uppercase;
}
.or-divider::before, .or-divider::after { content:''; flex:1; height:1px; background:#e8eef7; }
.soc-row { display: flex; gap: 10px; }
.soc-btn {
    flex: 1; height: 44px; background: #fff; border: 1.5px solid #dce4f0;
    border-radius: 11px; cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    font-family: 'Be Vietnam Pro', sans-serif; font-size: .82rem; font-weight: 700; color: #2d3a52;
    transition: all .2s;
}
.soc-btn:hover { background:#f4f7ff; border-color:#a8bde0; transform:translateY(-1px); }
.trust-row { display: flex; gap: 8px; margin-top: 20px; }
.trust-item {
    flex: 1; display: flex; align-items: center; gap: 7px;
    padding: 10px 8px; background: #f4f7ff; border-radius: 11px; border: 1px solid #e4ecf7;
}
.trust-icon { font-size: 15px; flex-shrink: 0; }
.trust-label { font-size: .62rem; color: #6a7fa0; font-weight: 700; line-height: 1.3; }
[data-testid="stExpander"] {
    border: 1.5px solid #dce4f0 !important; border-radius: 11px !important; margin-top: 8px !important;
}
/* Thêm vào cuối phần CSS */
.block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

LEFT_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden;font-family:'Be Vietnam Pro',sans-serif;}
.lp{width:100%;height:100vh;background:linear-gradient(150deg,#0b3a92 0%,#1252be 40%,#0a2560 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:44px 36px;position:relative;overflow:hidden;}
.pt{position:absolute;border-radius:50%;background:rgba(255,255,255,.06);animation:floatUp linear infinite;}
@keyframes floatUp{0%{transform:translateY(0) scale(1);opacity:.6;}100%{transform:translateY(-140px) scale(.3);opacity:0;}}
.wave{position:absolute;bottom:0;left:0;right:0;height:80px;overflow:hidden;}
.logo-w{z-index:2;display:flex;align-items:center;gap:12px;margin-bottom:32px;animation:slideDown .7s cubic-bezier(.23,1,.32,1) both;}
.logo-box{width:50px;height:50px;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.22);border-radius:14px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
.logo-box::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.18) 0%,transparent 60%);}
.logo-txt strong{display:block;font-size:.95rem;font-weight:900;letter-spacing:2px;text-transform:uppercase;color:white;line-height:1;}
.logo-txt span{font-size:.65rem;color:rgba(255,255,255,.6);letter-spacing:.8px;text-transform:uppercase;}
.dash-w{z-index:2;width:100%;max-width:360px;margin-bottom:32px;position:relative;animation:slideUp .8s .1s cubic-bezier(.23,1,.32,1) both;}
.card{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:16px;backdrop-filter:blur(8px);}
.dtop{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,.08);}
.dots{display:flex;gap:5px;}.dot{width:8px;height:8px;border-radius:50%;}
.dtitle{font-size:.68rem;font-weight:700;color:rgba(255,255,255,.8);letter-spacing:.6px;text-transform:uppercase;}
.live{font-size:.6rem;background:rgba(74,222,128,.15);color:#4ade80;padding:2px 8px;border-radius:20px;font-weight:600;}
.kpis{display:flex;gap:8px;margin-bottom:12px;}
.kpi{flex:1;background:rgba(255,255,255,.06);border-radius:10px;padding:8px 10px;border:1px solid rgba(255,255,255,.08);}
.kl{font-size:.58rem;color:rgba(255,255,255,.55);font-weight:500;margin-bottom:2px;}
.kv{font-size:.92rem;color:white;font-weight:800;line-height:1;}
.kd{font-size:.6rem;font-weight:600;margin-top:2px;}
.up{color:#4ade80;}.dn{color:#f87171;}
.bars{display:flex;align-items:flex-end;gap:4px;height:48px;margin-bottom:12px;}
.bar{flex:1;border-radius:4px 4px 0 0;animation:growBar .6s ease both;}
@keyframes growBar{from{transform:scaleY(0);transform-origin:bottom;}to{transform:scaleY(1);transform-origin:bottom;}}
.blo{background:rgba(255,255,255,.18);}.bhi{background:rgba(99,179,255,.7);}.btp{background:linear-gradient(to top,rgba(99,179,255,.8),rgba(147,210,255,.95));}
.kwl{display:flex;flex-direction:column;gap:5px;}
.kwr{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.05);border-radius:8px;padding:6px 10px;border:1px solid rgba(255,255,255,.06);}
.kr{font-size:.6rem;color:rgba(255,255,255,.45);width:14px;text-align:center;}
.kn{flex:1;font-size:.67rem;color:rgba(255,255,255,.85);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.kp{font-size:.6rem;font-weight:700;padding:2px 7px;border-radius:5px;}
.pg{background:rgba(74,222,128,.15);color:#4ade80;}.py{background:rgba(251,191,36,.15);color:#fbbf24;}
.badge{position:absolute;bottom:-14px;right:-14px;z-index:3;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:12px;padding:8px 14px;backdrop-filter:blur(10px);animation:floatBadge 4s ease-in-out infinite;}
@keyframes floatBadge{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}
.bnum{font-size:1.2rem;color:white;font-weight:900;line-height:1;}.bsub{font-size:.6rem;color:rgba(255,255,255,.65);}
.tag{z-index:2;text-align:center;color:white;animation:slideUp .9s .25s cubic-bezier(.23,1,.32,1) both;}
.tag h2{font-size:1rem;font-weight:900;letter-spacing:.8px;text-transform:uppercase;line-height:1.45;margin-bottom:8px;}
.tag p{font-size:.75rem;opacity:.68;line-height:1.7;max-width:260px;}
@keyframes slideDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:none;}}
@keyframes slideUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:none;}}
</style></head><body>
<div class="lp">
  <div class="pt" style="width:60px;height:60px;left:10%;top:20%;animation-duration:8s;"></div>
  <div class="pt" style="width:40px;height:40px;left:75%;top:60%;animation-duration:10s;animation-delay:2s;"></div>
  <div class="pt" style="width:25px;height:25px;left:50%;top:80%;animation-duration:7s;animation-delay:4s;"></div>
  <div class="pt" style="width:50px;height:50px;left:85%;top:15%;animation-duration:12s;animation-delay:1s;"></div>
  <div class="pt" style="width:18px;height:18px;left:30%;top:70%;animation-duration:6s;animation-delay:3s;"></div>
  <div class="logo-w">
    <div class="logo-box">
      <svg width="28" height="28" fill="white" viewBox="0 0 24 24" style="position:relative;z-index:1;">
        <path d="M12 2C8 2 4.5 4.5 3 8c1 .5 2.5.8 4 .5 1.5-.3 3-1.5 4-3 1 1.5 2.5 2.7 4 3 1.5.3 3 0 4-.5C17.5 4.5 16 2 12 2zm0 4c-.5 1-1.5 2-2.5 2.5C10.5 9 11.2 9 12 9s1.5 0 2.5-.5C13.5 8 12.5 7 12 6zm-7 8c0 3.9 3.1 7 7 7s7-3.1 7-7c0-1.2-.3-2.3-.8-3.3-1.2.6-2.6.9-4.1.6-1-.2-2-.7-2.8-1.3-.8.6-1.8 1.1-2.8 1.3-1.5.3-2.9 0-4.1-.6C5.3 11.7 5 12.8 5 14z"/>
      </svg>
    </div>
    <div class="logo-txt"><strong>Sea Dragon</strong><span>Technology</span></div>
  </div>
  <div class="dash-w">
    <div class="card">
      <div class="dtop">
        <div class="dots">
          <div class="dot" style="background:#ff5f57"></div>
          <div class="dot" style="background:#ffbd2e"></div>
          <div class="dot" style="background:#28ca42"></div>
        </div>
        <div class="dtitle">SEO Rank Dashboard</div>
        <div class="live">Live</div>
      </div>
      <div class="kpis">
        <div class="kpi"><div class="kl">Score</div><div class="kv">79<span style="font-size:.55rem;opacity:.6">/100</span></div><div class="kd up">+5.2%</div></div>
        <div class="kpi"><div class="kl">T&#7915; kh&#243;a</div><div class="kv">35</div><div class="kd up">+3 m&#7899;i</div></div>
        <div class="kpi"><div class="kl">Top 10</div><div class="kv">12</div><div class="kd dn">-1</div></div>
      </div>
      <div class="bars">
        <div class="bar blo" style="height:40%;animation-delay:.3s"></div>
        <div class="bar blo" style="height:60%;animation-delay:.36s"></div>
        <div class="bar blo" style="height:35%;animation-delay:.42s"></div>
        <div class="bar bhi" style="height:75%;animation-delay:.48s"></div>
        <div class="bar blo" style="height:50%;animation-delay:.54s"></div>
        <div class="bar btp" style="height:88%;animation-delay:.6s"></div>
        <div class="bar bhi" style="height:62%;animation-delay:.66s"></div>
        <div class="bar btp" style="height:95%;animation-delay:.72s"></div>
        <div class="bar bhi" style="height:70%;animation-delay:.78s"></div>
        <div class="bar btp" style="height:82%;animation-delay:.84s"></div>
      </div>
      <div class="kwl">
        <div class="kwr"><span class="kr">1</span><span class="kn">d&#7883;ch v&#7909; seo website</span><span class="kp pg">Top 3</span></div>
        <div class="kwr"><span class="kr">2</span><span class="kn">seo t&#7893;ng th&#7875; h&#224; n&#7897;i</span><span class="kp pg">Top 5</span></div>
        <div class="kwr"><span class="kr">3</span><span class="kn">t&#7889;i &#432;u t&#7915; kh&#243;a google</span><span class="kp py">Top 12</span></div>
      </div>
    </div>
    <div class="badge"><div class="bnum">97.3</div><div class="bsub">Performance</div></div>
  </div>
  <div class="tag">
    <h2>Gi&#7843;i ph&#225;p SEO to&#224;n di&#7879;n<br>cho doanh nghi&#7879;p</h2>
    <p>T&#7889;i &#432;u k&#7929; thu&#7853;t, n&#7897;i dung v&#224; chi&#7871;n l&#432;&#7907;c t&#7915; kh&#243;a &#8212; n&#226;ng cao th&#7913; h&#7841;ng, thu h&#250;t traffic ch&#7845;t l&#432;&#7907;ng cao.</p>
  </div>
  <div class="wave">
    <svg viewBox="0 0 400 80" preserveAspectRatio="none">
      <path d="M0,40 C80,10 160,70 240,40 C320,10 380,60 400,40 L400,80 L0,80 Z" fill="rgba(255,255,255,.04)"/>
    </svg>
  </div>
</div>
<script>
  // Tell parent iframe to resize itself to match content
  window.addEventListener('load', function() {
    const h = document.documentElement.scrollHeight;
    window.parent.postMessage({type: 'streamlit:setFrameHeight', height: h}, '*');
  });
</script>
</body></html>"""

# ── Inject JS to remove Streamlit's top padding ────────────────────────────────
st.markdown("""
<script>
// Remove top gap added by Streamlit
const style = document.createElement('style');
style.textContent = `
  .block-container { padding-top: 0 !important; }
  [data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
`;
document.head.appendChild(style);
</script>
""", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([46, 54], gap="small")

with left_col:
    components.html(LEFT_HTML, height=800, scrolling=False)

with right_col:
    tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký"])

    with tab1:
        st.markdown('<div class="form-heading">Chào mừng trở lại</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-sub">Đăng nhập để quản lý SEO của bạn</div>', unsafe_allow_html=True)

        st.markdown('<span class="field-label">Tên đăng nhập</span>', unsafe_allow_html=True)
        username = st.text_input("u", placeholder="Nhập tên tài khoản", label_visibility="collapsed")

        st.markdown('<span class="field-label">Mật khẩu</span>', unsafe_allow_html=True)
        password = st.text_input("p", placeholder="••••••••", type="password", label_visibility="collapsed")

        st.markdown('<div class="forgot-link"><a href="#">Quên mật khẩu?</a></div>', unsafe_allow_html=True)

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

        st.markdown("""
        <div class="or-divider">hoặc tiếp tục với</div>
        <div class="soc-row">
            <button class="soc-btn">
                <svg width="16" height="16" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Google
            </button>
            <button class="soc-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#1877F2">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook
            </button>
        </div>
        <div class="trust-row">
            <div class="trust-item"><span class="trust-icon">🔒</span><span class="trust-label">SSL 256-bit</span></div>
            <div class="trust-item"><span class="trust-icon">⚡</span><span class="trust-label">Realtime data</span></div>
            <div class="trust-item"><span class="trust-icon">🤖</span><span class="trust-label">AI Insights</span></div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="form-heading">Tạo tài khoản mới</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-sub">Bắt đầu hành trình SEO của bạn</div>', unsafe_allow_html=True)

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
                domain    = st.text_input("Tên domain",      key=f"domain_{i}", placeholder="vd: example.com")
                sheet_id  = st.text_input("Google Sheet ID", key=f"sheet_{i}",  placeholder="1abc...xyz")
                worksheet = st.text_input("Tên worksheet",   key=f"ws_{i}",     value="Ngày_22_01_2026", placeholder="Ngày_DD_MM_YYYY")
                if domain and sheet_id:
                    sheets_config.append({"domain": domain.strip(), "sheet_id": sheet_id.strip(), "worksheet": worksheet.strip()})

        if st.button("Đăng Ký ngay →", key="btn_register"):
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

if is_authenticated():
    display = st.session_state.get('display_name', st.session_state.user_id)
    st.success(f"Đã đăng nhập: {display}")
    if st.button("🚪 Đăng xuất"):
        logout()
        clear_all_session_files()
        st.rerun()