"""
Cấu hình chung cho Dashboard
"""

import streamlit as st

# ===================== PAGE CONFIG =====================
def setup_page_config():
    st.set_page_config(
        page_title="SEO Rank Dashboard Pro",
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
    # "Google Analytics"
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
    
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Hide default top navbar/header completely */
    section[data-testid="stHeader"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .st-emotion-cache-1me7uk0 {
        display: none !important;
    }
    .stAppViewContainer {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 1rem !important;
    }
</style>
    """
    return css

