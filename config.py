"""
Cấu hình chung cho Dashboard
"""

import streamlit as st

# ===================== PAGE CONFIG =====================
def setup_page_config():
    st.set_page_config(
        page_title="SEO Rank Dashboard Pro",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ===================== THEME COLORS =====================
THEMES = {
    'light': {
        'bg': '#ffffff',
        'text': '#1e293b',
        'primary': '#667eea',
        'secondary': '#764ba2',
        'card_bg': '#f8fafc'
    },
    'dark': {
        'bg': '#0f172a',
        'text': '#e2e8f0',
        'primary': '#818cf8',
        'secondary': '#a78bfa',
        'card_bg': '#1e293b'
    }
}

def get_current_theme():
    """Lấy theme hiện tại"""
    return THEMES.get(st.session_state.get('theme', 'dark'), THEMES['dark'])

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
    """Lấy custom CSS dựa trên theme hiện tại"""
    theme = get_current_theme()
    
    return f"""
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body {{
        background-color: {theme['bg']};
        color: {theme['text']};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }}
    
    .main {{
        padding: 2rem 2rem;
        background-color: {theme['bg']};
        color: {theme['text']};
        max-width: 1600px;
        margin: 0 auto;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {theme['card_bg']} 0%, {theme['bg']} 100%);
        border-right: 2px solid {theme['primary']};
    }}
    
    [data-testid="stSidebar"] h3 {{
        color: {theme['primary']};
        font-weight: 600;
        margin-top: 1.5rem;
    }}
    
    [data-testid="stSidebar"] p {{
        color: {theme['text']};
    }}
    
    [data-testid="stSidebar"] label {{
        color: {theme['text']};
    }}
    
    .section-header {{
        color: {theme['primary']};
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding: 1rem 0 0.5rem 0;
        border-bottom: 3px solid {theme['primary']};
        letter-spacing: 0.5px;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        border-bottom: 2px solid rgba(0,0,0,0.1);
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {theme['primary']};
        border-bottom: 3px solid {theme['primary']};
    }}
    
    [data-testid="metric-container"] {{
        background: {theme['card_bg']};
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    .alert-box {{
        padding: 1.25rem;
        border-radius: 10px;
        margin: 0.75rem 0;
        border-left: 5px solid;
        background-color: transparent;
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    
    .alert-critical {{
        background: rgba(239, 68, 68, 0.08);
        border-color: #ef4444;
        color: #991b1b;
    }}
    
    .alert-warning {{
        background: rgba(245, 158, 11, 0.08);
        border-color: #f59e0b;
        color: #92400e;
    }}
    
    .alert-success {{
        background: rgba(16, 185, 129, 0.08);
        border-color: #10b981;
        color: #065f46;
    }}
    
    .alert-info {{
        background: rgba(59, 130, 246, 0.08);
        border-color: #3b82f6;
        color: #1e40af;
    }}
    
    .score-box {{
        background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .score-number {{
        font-size: 3.5rem;
        font-weight: 800;
        margin: 1rem 0;
        letter-spacing: -1px;
    }}
    
    .stButton > button {{
        background: {theme['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .stButton > button:hover {{
        background: {theme['secondary']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }}
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {{
        border: 1px solid {theme['primary']} !important;
        border-radius: 8px;
        padding: 0.75rem;
        background: {theme['card_bg']} !important;
        color: {theme['text']} !important;
    }}
    
    .snapshot-card {{
        background: {theme['card_bg']};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        border: 2px solid rgba(0,0,0,0.05);
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .snapshot-card:hover {{
        border-color: {theme['primary']};
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }}
    
    .goal-progress {{
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        margin: 0.75rem 0;
    }}
    
    .goal-progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        transition: width 0.6s ease;
        border-radius: 10px;
    }}
    
    hr {{
        border: none;
        border-top: 1px solid rgba(0,0,0,0.08);
        margin: 2rem 0;
    }}
    
    .stAlert {{
        border-radius: 10px;
        padding: 1.25rem;
        border-left: 5px solid;
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        letter-spacing: -0.5px;
    }}
    
    h4 {{
        color: {theme['text']};
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    @media (max-width: 768px) {{
        .main {{
            padding: 1rem 1rem;
        }}
        
        .score-number {{
            font-size: 2.5rem;
        }}
        
        .section-header {{
            font-size: 1.1rem;
        }}
    }}
    
    html {{
        scroll-behavior: smooth;
    }}
    
    .block-container {{
        padding-top: 4rem !important;
    }}
</style>
"""

