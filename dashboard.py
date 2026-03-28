"""
SEO Rank Dashboard Pro - Main Application
Tách file: config.py, auth.py, helpers.py, persistence.py, data_loader.py
UI Modules: ui_tongquan.py, ui_sosanh.py, ui_keyword.py, ui_analysis.py, ui_forecast.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from config import setup_page_config, get_custom_css, ANALYSIS_MODES
from auth import init_sheets_client
from persistence import save_session_state, init_session_state, clear_all_session_files, load_auth_state
from data_loader import load_sheet_data_cached, get_available_days, apply_filters, get_date_range_days
# from sheets_config import SHEETS  # Removed: now per-user

# Import UI modules
from ui_tongquan import render_tongquan
from ui_sosanh import render_sosanh
from ui_keyword import render_keyword
from ui_url import render_url
from ui_nhomkeyword import render_nhomkeyword
from ui_muctieu import render_muctieu
from ui_dubao import render_dubao
from ui_snapshots import render_snapshots
from ui_lichnhiet import render_lichnhiet
from ui_ga import render_ga_ui

# ===================== INITIALIZE =====================
setup_page_config()

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ✅ NEW SECURE AUTH: Browser-only session + File persistence for F5
user_id = st.session_state.get('user_id')

# For multi-user security, do not import shared file-based auth state.
# Each browser session must have its own session_state set via login.

if not user_id:
    from user_auth import validate_session
    if not validate_session():
        st.switch_page("pages/auth.py")
else:
    from user_auth import validate_session
    if not validate_session():
        del st.session_state['user_id']
        st.switch_page("pages/auth.py")

# Load APP data only (safe)
init_session_state()

# ✅ Restore config if missing (including empty value)
if not st.session_state.get('user_sheets_config'):
    from user_auth import UserManager
    um = UserManager()
    user_doc = um.get_user(user_id)
    if user_doc:
        st.session_state.user_sheets_config = user_doc.get('sheets_config', []) or []
        st.session_state.display_name = user_doc.get('display_name', user_id)

# Clear stale avatar
# Safe sync avatar from DB
    try:
        from user_auth import UserManager
        um = UserManager()
        user_doc = um.users.find_one({'username': st.session_state.user_id})
        if user_doc:
            st.session_state.avatar_path = user_doc.get('avatar_path')
    except:
        pass

# col_left, col_right = st.columns([4,1])
# with col_right:
#     st.page_link("pages/profile.py", label="👤 Profile", icon="👤")

# Encode logo once at startup (used in both header and sidebar)
import base64
try:
    logo_base64 = base64.b64encode(open('logo.png', 'rb').read()).decode()
except:
    logo_base64 = None

# Sidebar toggle state
if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

def toggle_sidebar():
    st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
    # Rerun to apply CSS change
    st.rerun()

if logo_base64:
    st.sidebar.markdown(f"""
        <style>
            [data-testid="stSidebar"] > div:first-child {{ padding-top: 0rem !important;margin-bottom: -10rem !important; }}
            .sidebar-logo {{ 
                display: flex; 
                justify-content: center; 
                transform: translateY(-50px);
            }}
            .sidebar-logo img {{
                width: 180px;
                border-radius: 12px;
            }}
            /* Hide nav links */
            [data-testid="stSidebar"] nav a[href*="/pages/auth"], 
            [data-testid="stSidebar"] nav a[href="/dashboard"],
            [data-testid="stSidebarNav"] {{
                display: none !important;
            }}
        </style>
        <div class='sidebar-logo'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo'>
        </div>
    """, unsafe_allow_html=True)

# Sidebar toggle CSS + hide when collapsed (moved here to work properly)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

/* ══ SIDEBAR NỀN BLUE GRADIENT ══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0c3cbf 0%, #1557d4 50%, #0b2e9e 100%) !important;
    width: 18rem !important;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
    background-size: 36px 36px;
}
section[data-testid="stSidebar"] > div { position: relative; z-index: 1; }

/* ══ TEXT MÀU TRẮNG ══ */
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,.85) !important;
    font-family: 'Be Vietnam Pro', sans-serif !important;
}

/* ══ SECTION LABELS (markdown bold) ══ */
section[data-testid="stSidebar"] p strong,
section[data-testid="stSidebar"] .stMarkdown strong {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    color: rgba(255,255,255,.5) !important;
}

/* ══ SELECTBOX - fix dropdown trắng ══ */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,.15) !important;
    border: 1.5px solid rgba(255,255,255,.4) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div > div {
    color: #ffffff !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    fill: rgba(255,255,255,.7) !important;
}
/* Selectbox text color when displaying value */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
    color: #ffffff !important;
}

/* Force selected value / placeholder / menu option text to white */
section[data-testid="stSidebar"] [data-testid="stSelectbox"] *,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] *,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="menu"] *,
div[data-baseweb="menu"] li,
div[data-baseweb="menu"] li span,
div[data-baseweb="menu"] li div {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div {
    color: #ffffff !important;
}

/* Superforce all selectbox text to white in sidebar */
section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stSelectbox *,
section[data-testid="stSidebar"] .stSelectbox div,
section[data-testid="stSidebar"] .stSelectbox span,
section[data-testid="stSidebar"] .stSelectbox p,
section[data-testid="stSidebar"] .stSelectbox button {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stSelectbox [data-testid="stMarkdown"] {
    color: #ffffff !important;
}
/* ══ DROPDOWN LIST (popup) ══ */
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {
    background: #1a4fd6 !important;
    box-shadow: 0 8px 32px rgba(0,0,0,.3) !important;
}

/* Item thường */
div[data-baseweb="menu"] li {
    background: transparent !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
}

/* Force all text inside li to be white */
div[data-baseweb="menu"] li *,
div[data-baseweb="menu"] li span,
div[data-baseweb="menu"] li div,
div[data-baseweb="menu"] li p {
    color: #ffffff !important;
}

/* Item hover */
div[data-baseweb="menu"] li:hover {
    background: rgba(255,255,255,.15) !important;
    color: #ffffff !important;
}

div[data-baseweb="menu"] li:hover *,
div[data-baseweb="menu"] li:hover span,
div[data-baseweb="menu"] li:hover div {
    color: #ffffff !important;
}

/* Item đang được highlight/focus (keyboard nav) */
div[data-baseweb="menu"] li[data-highlighted="true"],
div[data-baseweb="menu"] li:focus {
    background: rgba(255,255,255,.18) !important;
    color: #ffffff !important;
}

div[data-baseweb="menu"] li[data-highlighted="true"] *,
div[data-baseweb="menu"] li[data-highlighted="true"] span,
div[data-baseweb="menu"] li:focus * {
    color: #ffffff !important;
}

/* Item đang được chọn (selected) */
div[data-baseweb="menu"] li[aria-selected="true"] {
    background: rgba(255,255,255,.28) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

div[data-baseweb="menu"] li[aria-selected="true"] *,
div[data-baseweb="menu"] li[aria-selected="true"] span,
div[data-baseweb="menu"] li[aria-selected="true"] div {
    color: #ffffff !important;
}

/* Scrollbar trong dropdown */
div[data-baseweb="menu"] ul::-webkit-scrollbar {
    width: 4px !important;
}
div[data-baseweb="menu"] ul::-webkit-scrollbar-track {
    background: transparent !important;
}
div[data-baseweb="menu"] ul::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,.3) !important;
    border-radius: 4px !important;
}
/* ══ DATE INPUT - override hoàn toàn ══ */
section[data-testid="stSidebar"] [data-testid="stDateInput"] > div {
    background: rgba(255,255,255,.15) !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
section[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
    background: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"],
section[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: transparent !important;
    border: none !important;
    color: #fff !important;
    caret-color: #fff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-align: center !important;
}

/* ══ CHECKBOX - nuclear override ══ */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 0 !important;
    gap: 10px !important;
    align-items: center !important;
}
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child {
    width: 18px !important;
    height: 18px !important;
    min-width: 18px !important;
    background: rgba(255,255,255,.15) !important;
    border: 2px solid rgba(255,255,255,.5) !important;
    border-radius: 4px !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child > div {
    background: transparent !important;
}
/* ══ CHECKBOX CLEAN & OPTIMIZED ══ */
/* Wrapper label */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
section[data-testid="stSidebar"] [data-baseweb="checkbox"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 6px 0 !important;
    gap: 10px !important;
    align-items: center !important;
    display: flex !important;
    cursor: pointer !important;
    transition: all .2s ease !important;
}

/* Checkbox box - unchecked state */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child,
section[data-testid="stSidebar"] [data-baseweb="checkbox"] span[role="checkbox"] {
    width: 20px !important;
    height: 20px !important;
    min-width: 20px !important;
    min-height: 20px !important;
    background: rgba(255,255,255,.12) !important;
    border: 2.5px solid rgba(255,255,255,.5) !important;
    border-radius: 5px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all .2s ease !important;
}

/* Checkbox box - checked state */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked ~ label > div:first-child,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child[aria-checked="true"],
section[data-testid="stSidebar"] [data-baseweb="checkbox"] input:checked ~ span[role="checkbox"],
section[data-testid="stSidebar"] [data-baseweb="checkbox"] span[role="checkbox"][aria-checked="true"] {
    background: #ffffff !important;
    border-color: #ffffff !important;
    box-shadow: 0 0 8px rgba(255,255,255,.3) !important;
}

/* Checkmark icon - inside checkbox */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked ~ label > div:first-child > div svg,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked ~ label > div:first-child svg,
section[data-testid="stSidebar"] [data-baseweb="checkbox"] input:checked ~ span[role="checkbox"] svg,
section[data-testid="stSidebar"] [data-baseweb="checkbox"] span[role="checkbox"][aria-checked="true"] svg {
    color: #1557d4 !important;
    fill: #1557d4 !important;
    width: 14px !important;
    height: 14px !important;
}

/* Checkbox label text */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:last-child,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:last-child p,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label span:not([role]),
section[data-testid="stSidebar"] [data-baseweb="checkbox"] span {
    color: rgba(255,255,255,.88) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Hover effect */
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover > div:first-child,
section[data-testid="stSidebar"] [data-baseweb="checkbox"]:hover span[role="checkbox"] {
    border-color: rgba(255,255,255,.8) !important;
    background: rgba(255,255,255,.2) !important;
}

/* ══ LABEL (Từ ngày / Đến ngày) ══ */
section[data-testid="stSidebar"] [data-testid="stDateInput"] label {
    color: rgba(255,255,255,.7) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* ══ RADIO BUTTONS (chế độ phân tích) ══ */
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 9px !important;
    padding: 8px 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    transition: background .15s !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,.1) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
section[data-testid="stSidebar"] [data-testid="stRadio"] input:checked ~ label {
    background: rgba(255,255,255,.2) !important;
    border: 1px solid rgba(255,255,255,.35) !important;
    font-weight: 600 !important;
}
/* Radio circle */
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"] {
    border-color: rgba(255,255,255,.5) !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
    background: #fff !important;
    border-color: #fff !important;
}
/* ══ TEXT INPUT ══ */
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    border-radius: 8px !important;
    color: #fff !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,.35) !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: rgba(255,255,255,.6) !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,.15) !important;
}

/* ══ SLIDER ══ */
section[data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stTickBar"] {
    color: rgba(255,255,255,.4) !important;
}
section[data-testid="stSidebar"] .stSlider > div > div > div {
    background: rgba(255,255,255,.25) !important;
}
section[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: #fff !important;
}
section[data-testid="stSidebar"] .stSlider [role="slider"] {
    background: #fff !important;
    border: 2px solid #1557d4 !important;
}

/* ══ BUTTONS ══ */
section[data-testid="stSidebar"] button {
    background: rgba(255,255,255,.15) !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: background .15s !important;
}
section[data-testid="stSidebar"] button:hover {
    background: rgba(255,255,255,.25) !important;
    border-color: rgba(255,255,255,.4) !important;
}

/* ══ EXPANDER ══ */
section[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,.1) !important;
    border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    color: rgba(255,255,255,.85) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
    fill: rgba(255,255,255,.6) !important;
}

/* ══ DIVIDER ══ */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.15) !important;
}

/* ══ WARNING / ERROR / SUCCESS alerts ══ */
section[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.2) !important;
    border-radius: 8px !important;
    color: #fff !important;
}

/* ══ DATE INPUT ══ */
section[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    border-radius: 8px !important;
    color: #fff !important;
}

/* ══ MULTISELECT ══ */
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: rgba(255,255,255,.25) !important;
    border-radius: 6px !important;
}
/* ══ FIX INPUT TRẮNG TRONG EXPANDER SIDEBAR ══ */

/* Text input wrapper */
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="base-input"] {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.22) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="base-input"] input {
    background: transparent !important;
    color: #fff !important;
    caret-color: #fff !important;
}

/* Slider track */
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div {
    background: rgba(255,255,255,.25) !important;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #fff !important;
    border: 2px solid #1048c8 !important;
}
/* Slider filled track */
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div:nth-child(5) {
    background: rgba(255,255,255,.7) !important;
}

/* (Checkbox styles consolidated above) */

/* Expander border đỏ → xanh trong */
section[data-testid="stSidebar"] details {
    background: rgba(255,255,255,.1) !important;
    border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] details[open] {
    border-color: rgba(255,255,255,.3) !important;
}

/* Button Lưu bộ lọc */
section[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: rgba(255,255,255,.18) !important;
    border: 1px solid rgba(255,255,255,.3) !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: rgba(255,255,255,.28) !important;
}

/* Label text trong expander */
section[data-testid="stSidebar"] [data-testid="stSlider"] label,
section[data-testid="stSidebar"] [data-testid="stTextInput"] label,
section[data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stTickBarMax"],
section[data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stTickBarMin"] {
    color: rgba(255,255,255,.7) !important;
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([4,1])
with col_left:
    st.markdown("""
        <div style='text-align: left; margin: 0; padding: 0;'>
            <h1 style='font-size: 2.5rem; font-weight: 800; margin: 0; padding: 0;'>SEO Rank</h1>
            <p style='font-size: 1rem; opacity: 0.7; margin: 0; padding: 0;'>Phân tích SEO toàn diện với AI Insights & Forecasting</p>
        </div>
    """, unsafe_allow_html=True)
with col_right:
    import os
    import base64 as _b64

    # Force reload avatar
    try:
        from user_auth import UserManager
        um = UserManager()
        user_doc = um.users.find_one({'username': user_id})
        if user_doc and user_doc.get('avatar_path'):
            st.session_state.avatar_path = user_doc.get('avatar_path')
    except:
        pass
    avatar_path = st.session_state.get('avatar_path')

    # Build avatar HTML
    if avatar_path and os.path.exists(avatar_path):
        ext = avatar_path.rsplit('.', 1)[-1].replace('jpg', 'jpeg')
        src = f"data:image/{ext};base64," + _b64.b64encode(open(avatar_path, 'rb').read()).decode()
        avatar_html = f'''<img src="{src}" style="
            display: flex; jutify-content: end;
            width:42px; height:42px; border-radius:50%;
            object-fit:cover; border:2px solid #3b82f6;
            ">'''
    else:
        initials = st.session_state.get('display_name', st.session_state.get('user_id', 'U'))[0].upper()
        avatar_html = f'''<div style="
            width:42px; height:42px; border-radius:50%;
            background:#3b82f6; color:#fff;
            display:flex; align-items:center; justify-content:center;
            font-weight:700; font-size:17px; border:2px solid #2563eb;">
            {initials}
        </div>'''

    # Render avatar as clickable link → profile page
    # dùng st.page_link ẩn + HTML avatar hiển thị đè lên
    st.markdown(f"""
    <style>
    div[data-testid="column"]:last-child {{
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }}
    .avatar-link {{
        display: inline-block;
        cursor: pointer;
        border-radius: 50%;
        line-height: 0;
        transition: transform .15s, box-shadow .15s;
        text-decoration: none;
    }}
    .avatar-link:hover {{
        transform: scale(1.08);
        box-shadow: 0 0 0 3px rgba(59,130,246,.35);
        border-radius: 50%;
    }}
    z
    
    
    </style>

    <a href="/profile" target="_self" class="avatar-link">
        {avatar_html}
    </a>
    """, unsafe_allow_html=True)
# ===================== SIDEBAR =====================
if 'user_id' in st.session_state:
    # Only render sidebar for authenticated users
    # st.sidebar.markdown("---")

    # if st.sidebar.button("🚪 Đăng xuất"):
    #     # FIXED: Proper logout with full session clear
    #     clear_all_session_files()
    #     if 'user_id' in st.session_state:
    #         del st.session_state['user_id']
    #     if 'user_domains' in st.session_state:
    #         del st.session_state['user_domains']
    #     # st.switch_page("pages/auth.py")

    # Domain selector
    user_sheets_config = st.session_state.get('user_sheets_config') or []
    if not isinstance(user_sheets_config, list):
        user_sheets_config = []
    domains = [cfg.get('domain') for cfg in user_sheets_config if isinstance(cfg, dict) and cfg.get('domain')]
    if not domains:
        st.error("❌ Không có domain nào được phép truy cập")
        st.stop()
    st.sidebar.markdown("**🌐 Domain**")
    selected_domain = st.sidebar.selectbox("🌐 Domain", domains, label_visibility="collapsed")
    st.session_state.selected_domain = selected_domain
    
    # Get sheet config for selected domain
    selected_config = next((cfg for cfg in user_sheets_config if cfg['domain'] == selected_domain), None)
    if not selected_config:
        st.error(f"❌ Không tìm thấy config cho domain {selected_domain}")
        st.stop()
    sheet_id = selected_config['sheet_id']

    # Load data early for filters
    client = init_sheets_client()
    sheet_map = get_available_days(sheet_id, client)
    
    if not sheet_map:
        st.error("❌ Không tìm thấy worksheet dạng Ngày_DD_MM_YYYY")
        st.stop()
    
    # Initialize selected_days if not defined (before validation)
    if 'selected_days' not in locals():
        selected_days = [list(sheet_map.keys())[-1]]
    
    # Validate selected_days against current sheet_map to prevent KeyError
    orig_len = len(selected_days)
    selected_days = [day for day in selected_days if day in sheet_map]
    if len(selected_days) < orig_len:
        st.sidebar.warning(f"⚠️ Filtered {orig_len - len(selected_days)} stale/missing days. Now using {len(selected_days)} days.")

# Filter configuration
# st.sidebar.markdown("**💾 Bộ lọc đã lưu**")
if 'saved_filters' in st.session_state and st.session_state.saved_filters:
    filter_names = list(st.session_state.saved_filters.keys())
    selected_saved_filter = st.sidebar.selectbox("Chọn bộ lọc", ["Mới"] + filter_names)
    if selected_saved_filter != "Mới":
        saved = st.session_state.saved_filters[selected_saved_filter]
        selected_days = saved.get("days", [list(sheet_map.keys())[-1]])
        keyword_filter_default = saved.get("keyword", "")
        rank_limit_default = saved.get("rank_limit", 100)
    else:
        selected_days = [list(sheet_map.keys())[-1]]
        keyword_filter_default = ""
        rank_limit_default = 100
else:
    selected_days = [list(sheet_map.keys())[-1]] if 'sheet_map' in locals() else []
    keyword_filter_default = ""
    rank_limit_default = 100

# Quick selection
# Allow users to load a larger date range (up to 365 days recommended)
max_days = 365
total_available_days = len(sheet_map) if 'sheet_map' in locals() else 0

if total_available_days > max_days:
    st.sidebar.warning(f"⚠️ Có {total_available_days} ngày dữ liệu. Khuyến nghị chọn ≤ {max_days} ngày (vẫn có thể chọn thêm nhưng có thể chậm).")

# if total_available_days > 0:
#     st.sidebar.markdown("#### 🚀 Chọn nhanh")
#     col_quick1, col_quick2 = st.sidebar.columns(2)
#     with col_quick1:
#         if st.button("📅 7 ngày"):
#             selected_days = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:7]
#             st.rerun()
#     with col_quick2:
#         if st.button("📅 30 ngày"):
#             selected_days = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:30]
#             st.rerun()

# Date range picker
st.sidebar.markdown("**📅 Chọn khoảng thời gian**")
use_date_range = st.sidebar.checkbox("Sử dụng bộ chọn khoảng", value=False)

# Initialize date range session state
if 'filtered_date_range' not in st.session_state:
    st.session_state.filtered_date_range = None

if use_date_range and 'sheet_map' in locals():
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.date_input("Từ ngày", value=min(sheet_map.values()),
        min_value=min(sheet_map.values()), max_value=max(sheet_map.values()),
        key='date_range_start', format="DD/MM/YYYY")
    with col_end:
        end_date = st.date_input("Đến ngày", value=max(sheet_map.values()),
        min_value=min(sheet_map.values()), max_value=max(sheet_map.values()),
        key='date_range_end', format="DD/MM/YYYY")
    if st.sidebar.button("Lọc"):
        if start_date > end_date:
            st.sidebar.error("❌ Ngày bắt đầu phải trước hoặc bằng ngày kết thúc")
        else:
            range_days = get_date_range_days(sheet_map, start_date, end_date)
            if range_days:
                st.session_state.filtered_date_range = range_days
                st.session_state.filtered_date_range = [day for day in st.session_state.filtered_date_range if day in sheet_map]
                # st.sidebar.success(f"✅ Đã lọc {len(range_days)} ngày")
            else:
                st.sidebar.warning("⚠️ Không có dữ liệu trong khoảng ngày đã chọn")
    # Apply persisted date range if it exists
    if st.session_state.filtered_date_range:
        selected_days = st.session_state.filtered_date_range
else:
    if 'sheet_map' in locals():
        day_options = sorted(sheet_map.keys(), key=lambda x: sheet_map[x])
        current_index = 0 if not selected_days else max(0, day_options.index(selected_days[0]) if selected_days[0] in day_options else 0)
        selected_day = st.sidebar.selectbox("📅 Chọn ngày", options=day_options, index=current_index)
        selected_days = [selected_day]

if not selected_days:
    st.warning("⚠️ Vui lòng chọn ít nhất một ngày")
    st.stop()

if len(selected_days) > max_days:
    st.sidebar.error(f"⚠️ Đã chọn {len(selected_days)} ngày!")
elif len(selected_days) > 15:
    st.sidebar.warning(f"📊 Đã chọn {len(selected_days)} ngày")

# Analysis mode
st.sidebar.divider()
st.sidebar.markdown("**📊 Chế độ phân tích**")
analysis_mode = st.sidebar.radio("Chọn chế độ", ANALYSIS_MODES, index=0, label_visibility="collapsed")

# Advanced filters
st.sidebar.divider()
with st.sidebar.expander("🔍 Bộ lọc nâng cao", expanded=False):
    keyword_filter = st.text_input("Tìm kiếm từ khóa", value=keyword_filter_default, placeholder="Nhập từ khóa...")
    rank_limit = st.slider("Hiển thị top ≤", min_value=1, max_value=100, value=rank_limit_default)
    col1, col2 = st.columns(2)
    with col1:
        only_no_rank = st.checkbox("Chưa có rank")
    with col2:
        only_with_rank = st.checkbox("Có rank")
    filter_name = st.text_input("Tên bộ lọc", placeholder="VD: Top 10 only")
    if st.button("💾 Lưu bộ lọc"):
        if filter_name:
            if 'saved_filters' not in st.session_state:
                st.session_state.saved_filters = {}
            st.session_state.saved_filters[filter_name] = {"days": selected_days, "keyword": keyword_filter, "rank_limit": rank_limit}
            save_session_state()
            st.success(f"✅ Đã lưu bộ lọc '{filter_name}'")
        else:
            st.error("Vui lòng nhập tên bộ lọc")

# ===================== LOAD SHEET DATA =====================
# If not authenticated, skip data load
if 'user_id' in st.session_state:
    df, sheet_map = load_sheet_data_cached(client, sheet_id, selected_days)

    if df is None or df.empty:
        st.warning("⚠️ Không có dữ liệu")
        st.stop()

    # Apply filters
    filtered = apply_filters(df, keyword_filter, rank_limit, only_no_rank, only_with_rank)
else:
    df = pd.DataFrame()
    filtered = pd.DataFrame()
    sheet_map = {}
    selected_days = []
    keyword_filter = ""
    rank_limit = 100
    only_no_rank = False
    only_with_rank = False

# ===================== RENDER MODES =====================
MODE_DISPATCH = {
    "Tổng quan": lambda: render_tongquan(filtered, sheet_map, selected_days),
    "So sánh ngày": lambda: render_sosanh(filtered, sheet_map, selected_days),
    "Phân tích từ khóa": lambda: render_keyword(filtered, df),
    "Phân tích URL": lambda: render_url(filtered, df),
    "Nhóm từ khóa": lambda: render_nhomkeyword(filtered),
    "Mục tiêu": lambda: render_muctieu(filtered),
    "Dự báo": lambda: render_dubao(df),
    "Snapshots": lambda: render_snapshots(),
    "Lịch nhiệt": lambda: render_lichnhiet(df),
    "Google Analytics": lambda: render_ga_ui(filtered, df),
}

if analysis_mode in MODE_DISPATCH:
    MODE_DISPATCH[analysis_mode]()
else:
    st.error(f"❌ Chế độ '{analysis_mode}' chưa được implement")

# ===================== DATA TABLE =====================
# ===================== DATA TABLE =====================
st.markdown('<p class="section-header">📄 Bảng dữ liệu chi tiết</p>', unsafe_allow_html=True)
st.markdown(f"**Hiển thị {len(filtered):,} từ khóa**")

column_order = ["Từ khóa", "Trang", "Vị trí", "Thứ hạng", "URL", "Tiêu đề", "Domain mục tiêu", "Ngày tìm kiếm", "Ngày"]
display_columns = [col for col in column_order if col in filtered.columns]
filtered_display = filtered[display_columns].copy()
filtered_display.index = range(1, len(filtered_display) + 1)

# ── File lưu riêng theo user ──
import json, os

MARKED_FILE = f"session_marked_{st.session_state.get('user_id', 'default')}.json"

def save_marked():
    with open(MARKED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(st.session_state.marked_keywords), f, ensure_ascii=False)

def load_marked():
    if os.path.exists(MARKED_FILE):
        with open(MARKED_FILE, encoding='utf-8') as f:
            return set(tuple(x) for x in json.load(f))  # convert list→tuple
    return set()

# ── Init ──
if 'marked_keywords' not in st.session_state:
    st.session_state.marked_keywords = load_marked()

# ── Tạo key = (Từ khóa, Ngày) ──
# Xác định cột ngày
ngay_col = 'Ngày' if 'Ngày' in filtered_display.columns else 'Ngày tìm kiếm'

filtered_display.insert(
    0, '⭐',
    filtered_display.apply(
        lambda r: (r['Từ khóa'], str(r[ngay_col])) in st.session_state.marked_keywords,
        axis=1
    )
)

# ── CSS ──
st.markdown("""
<style>
[data-testid="stDataFrame"] tr:nth-child(even) td {
    background-color: rgba(59, 130, 246, 0.05) !important;
}
[data-testid="stDataFrame"] thead tr th {
    background-color: rgba(21, 87, 212, 0.08) !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-bottom: 2px solid rgba(21, 87, 212, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Render bảng ──
edited_df = st.data_editor(
    filtered_display.drop(columns=["Ngày_Sort"], errors="ignore"),
    height=600,
    use_container_width=True,
    key="data_table_editor",
    column_config={
        "⭐": st.column_config.CheckboxColumn("⭐", help="Đánh dấu", default=False, width="small"),
        "Thứ hạng": st.column_config.NumberColumn("Thứ hạng", format="%d"),
        "URL": st.column_config.LinkColumn("URL"),
    },
    disabled=[col for col in filtered_display.columns if col != '⭐'],
)

# ── Lưu đánh dấu theo (Từ khóa, Ngày) ──
if '⭐' in edited_df.columns and 'Từ khóa' in edited_df.columns:
    for _, row in edited_df.iterrows():
        key = (row['Từ khóa'], str(row[ngay_col]))
        if row['⭐']:
            st.session_state.marked_keywords.add(key)
        else:
            st.session_state.marked_keywords.discard(key)
    save_marked()

# ── Hiển thị danh sách đã đánh dấu ──
if st.session_state.marked_keywords:
    # Lọc từ filtered_display (đã có đủ thông tin)
    marked_df = filtered_display[filtered_display['⭐'] == True].drop(columns=['⭐'], errors='ignore')

    col_mark1, col_mark2 = st.columns([6, 1])
    with col_mark1:
        st.markdown(f"#### ⭐ Đã đánh dấu ({len(marked_df)})")
    with col_mark2:
        if st.button("🗑️ Xóa tất cả"):
            st.session_state.marked_keywords = set()
            save_marked()
            st.rerun()

    st.dataframe(
        marked_df.drop(columns=["Ngày_Sort"], errors='ignore'),
        use_container_width=True,
        height=min(300, len(marked_df) * 35 + 40),
        column_config={
            "Thứ hạng": st.column_config.NumberColumn("Thứ hạng", format="%d"),
            "URL": st.column_config.LinkColumn("URL"),
        }
    )

# Download
csv = filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="⬇️ Tải xuống dữ liệu (CSV)",
    data=csv,
    file_name=f"seo_data_{selected_domain}_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Auto-save session on interaction
save_session_state()

