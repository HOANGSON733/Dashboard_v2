"""
Cấu hình chung cho Dashboard
"""

import streamlit as st

# ===================== PAGE CONFIG =====================
def setup_page_config():
    st.set_page_config(
        page_title="SEO Rank Dashboard ",
        page_icon="logocheck.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None
    )

# ===================== ANALYSIS MODES =====================
ANALYSIS_MODES = [
    "Tổng quan",
    "So sánh ngày",
    "Phân tích từ khóa",
    "Phân tích URL", 
    "Nhóm từ khóa",
    "Mục tiêu",
    "Dự báo",
    "Snapshots",
    "Lịch nhiệt",
    "Google Analytics"
]

# ===================== GOOGLE ANALYTICS WEBSITES =====================
GA_WEBSITES = {
    "Website 1 - huyenhocviet.com": "464855282",
    "Website 2 - drtuananh.com": "517078868",
    "Website 3 - sdtc.com": "517020245",
}

# ===================== CUSTOM CSS =====================
def get_custom_css():
    """Custom CSS - static colors"""
    css = """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .main {
        padding: 2rem;
        max-width: 1600px;
        margin: 0 auto;
    }
    
    .section-header {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding: 1rem 0 0.5rem 0;
        border-bottom: 3px solid #667eea;
    }
    
    .stButton > button {
        background: #667eea;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: #764ba2;
    }
    
    /* Hide specific pages from sidebar nav */
    section[data-testid="stSidebarNav"] a[href*="/pages/auth"],
    section[data-testid="stSidebarNav"] a[href*="/pages/profile"],
    section[data-testid="stSidebarNav"] a[href="/dashboard"] {
        display: none !important;
    }
    
    /* Navbar enabled, auth/profile/dashboard hidden */
    /* ===== ẨN NAVIGATION LIST MẶC ĐỊNH CỦA STREAMLIT ===== */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ===== DARK BLUE SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding-top: 1rem !important;
    }

    /* ===== TEXT trong sidebar ===== */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    /* ===== RADIO TEXT - màu trắng ===== */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label span,
    [data-testid="stSidebar"] [data-testid="stRadio"] div[data-testid="stMarkdownContainer"] p {
        color: #e2e8f0 !important;
    }

    /* Active item - màu xanh sáng */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
        color: #60a5fa !important;
    }
    /* ===== SECTION LABELS (bold texts) ===== */
    [data-testid="stSidebar"] strong {
        color: #60a5fa !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    /* ===== SELECTBOX ===== */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: rgba(30, 58, 138, 0.3) !important;
        border: 1px solid rgba(59, 130, 246, 0.35) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
        border-color: rgba(59, 130, 246, 0.7) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #60a5fa !important;
    }

    /* ===== RADIO BUTTONS (analysis mode) ===== */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 7px !important;
        padding: 0.4rem 0.75rem !important;
        transition: background 0.15s, color 0.15s !important;
        color: #94a3b8 !important;
        font-size: 13px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] ~ span {
        color: #60a5fa !important;
        font-weight: 600 !important;
    }
    /* Active radio item highlight */
    [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(59,130,246,0.2), rgba(59,130,246,0.05)) !important;
        border-left: 2px solid #3b82f6 !important;
        color: #60a5fa !important;
    }
    /* Radio dot color */
    [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        color: inherit !important;
        font-size: 13px !important;
    }

    /* ===== DIVIDER ===== */
    [data-testid="stSidebar"] hr {
        border-color: rgba(59, 130, 246, 0.15) !important;
    }

    /* ===== EXPANDER (Bộ lọc nâng cao) ===== */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        color: #60a5fa !important;
        font-size: 13px !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] svg {
        fill: #3b82f6 !important;
    }

    /* ===== CHECKBOX ===== */
    [data-testid="stSidebar"] [data-testid="stCheckbox"] span {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] [data-testid="stCheckbox"] [aria-checked="true"] {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }

    /* ===== SLIDER ===== */
    [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] div[class*="Track"] {
        background: #1e3a5f !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }
    /* ===== NÚT LỌC - giới hạn width ===== */
    [data-testid="stSidebar"] [data-testid="stButton"] {
        width: auto !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: auto !important;
        min-width: 80px !important;
        padding: 0.5rem 1.5rem !important;
    }
    /* ===== TEXT INPUT ===== */
    [data-testid="stSidebar"] input[type="text"] {
        background: rgba(30, 58, 138, 0.2) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 7px !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] input[type="text"]:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* ===== WARNING/ERROR boxes ===== */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 12px !important;
    }
    /* ===== DATE INPUT - target đúng component Streamlit ===== */
[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"] {
    background: rgba(30, 58, 138, 0.25) !important;
    border: 1px solid rgba(59, 130, 246, 0.35) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] div[data-baseweb="input"]:hover {
    border-color: rgba(59, 130, 246, 0.7) !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {
    background: transparent !important;
    color: #e2e8f0 !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] label {
    color: #60a5fa !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ===== Calendar icon ===== */
[data-testid="stSidebar"] [data-testid="stDateInput"] svg {
    fill: #3b82f6 !important;
}

/* ===== NÚT LỌC ===== */
[data-testid="stSidebar"] [data-testid="stButton"] button {
    width: auto !important;
    background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 0.5rem 2rem !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.55) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3) !important;
}


</style>
    """
    return css

