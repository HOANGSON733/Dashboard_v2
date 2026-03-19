"""
SEO Rank Dashboard Pro - Main Application
Tách file: config.py, auth.py, helpers.py, persistence.py, data_loader.py
UI Modules: ui_tongquan.py, ui_sosanh.py, ui_keyword.py, ui_analysis.py, ui_forecast.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from config import setup_page_config, get_current_theme, get_custom_css, ANALYSIS_MODES
from auth import init_sheets_client
from persistence import save_session_state, init_session_state
from data_loader import load_sheet_data_cached, get_available_days, apply_filters, get_date_range_days
from sheets_config import SHEETS

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
init_session_state()

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Encode logo once at startup (used in both header and sidebar)
import base64
try:
    logo_base64 = base64.b64encode(open('logo.png', 'rb').read()).decode()
except:
    logo_base64 = None

else:
    st.markdown("""
        <div style='text-align: left; margin: 0; padding: 0;'>
            <h1 style='font-size: 2.5rem; font-weight: 800; margin: 0; padding: 0;'>SEO Rank</h1>
            <p style='font-size: 1rem; opacity: 0.7; margin: 0; padding: 0;'>Phân tích SEO toàn diện với AI Insights & Forecasting</p>
        </div>
    """, unsafe_allow_html=True)


# ===================== SIDEBAR =====================
# Encode logo for sidebar (reuse the one already loaded)
try:
    if logo_base64 is None:
        logo_base64 = base64.b64encode(open('logo.png', 'rb').read()).decode()
    st.sidebar.markdown(f"""
        <style>
            [data-testid="stSidebar"] > div:first-child {{ padding-top: 0rem !important; }}
            .sidebar-logo {{ 
                display: flex; 
                justify-content: center; 
                transform: translateY(-40px);
            }}
            .sidebar-logo img {{
                width: 180px;
                border-radius: 12px;
                
            }}
        </style>
        <div class='sidebar-logo'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo'>
        </div>
    """, unsafe_allow_html=True)
except Exception as e:
    st.sidebar.error(f"Logo error: {e}")

# Domain selector
st.sidebar.markdown("**🌐 Domain**")
domains = list(SHEETS.keys())
selected_domain = st.sidebar.selectbox("🌐 Domain", domains, label_visibility="collapsed")
st.session_state.selected_domain = selected_domain
sheet_id = SHEETS[selected_domain]["sheet_id"]

# Theme selector
st.sidebar.markdown("**🎨 Giao diện**")
selected_theme = st.sidebar.selectbox("Chế độ", options=['light', 'dark'], index=0 if st.session_state.theme == 'light' else 1, label_visibility="collapsed")
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    save_session_state()
    st.rerun()

# Load data
client = init_sheets_client()
sheet_map = get_available_days(sheet_id, client)

if not sheet_map:
    st.error("❌ Không tìm thấy worksheet dạng Ngày_DD_MM_YYYY")
    st.stop()

# Filter configuration
st.sidebar.markdown("**💾 Bộ lọc đã lưu**")
if st.session_state.saved_filters:
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
    selected_days = [list(sheet_map.keys())[-1]]
    keyword_filter_default = ""
    rank_limit_default = 100

# Quick selection
max_days = 30
total_available_days = len(sheet_map)

if total_available_days > max_days:
    st.sidebar.warning(f"⚠️ Có {total_available_days} ngày dữ liệu. Khuyến nghị chọn ≤ {max_days} ngày.")
    st.sidebar.markdown("#### 🚀 Chọn nhanh")
    col_quick1, col_quick2 = st.sidebar.columns(2)
    with col_quick1:
        if st.button("📅 7 ngày"):
            selected_days = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:7]
            st.rerun()
    with col_quick2:
        if st.button("📅 30 ngày"):
            selected_days = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:30]
            st.rerun()

# Date range picker
st.sidebar.markdown("**📅 Chọn khoảng thời gian**")
use_date_range = st.sidebar.checkbox("Sử dụng bộ chọn khoảng", value=False)

if use_date_range:
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.date_input("Từ ngày", value=min(sheet_map.values()), min_value=min(sheet_map.values()), max_value=max(sheet_map.values()))
    with col_end:
        end_date = st.date_input("Đến ngày", value=max(sheet_map.values()), min_value=min(sheet_map.values()), max_value=max(sheet_map.values()))
    if start_date <= end_date:
        range_days = get_date_range_days(sheet_map, start_date, end_date)
        if range_days:
            selected_days = range_days
            st.sidebar.success(f"✅ Đã chọn {len(selected_days)} ngày")
else:
    selected_days = st.sidebar.multiselect("📅 Chọn ngày", options=list(sheet_map.keys()), default=selected_days, max_selections=50)

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
            st.session_state.saved_filters[filter_name] = {"days": selected_days, "keyword": keyword_filter, "rank_limit": rank_limit}
            save_session_state()
            st.success(f"✅ Đã lưu bộ lọc '{filter_name}'")
        else:
            st.error("Vui lòng nhập tên bộ lọc")


# ===================== LOAD SHEET DATA =====================
df, sheet_map = load_sheet_data_cached(client, sheet_id, selected_days)

if df is None:
    st.warning("⚠️ Không có dữ liệu")
    st.stop()

# Apply filters
filtered = apply_filters(df, keyword_filter, rank_limit, only_no_rank, only_with_rank)




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
st.markdown('<p class="section-header">📄 Bảng dữ liệu chi tiết</p>', unsafe_allow_html=True)
st.markdown(f"**Hiển thị {len(filtered):,} từ khóa**")

column_order = ["Từ khóa", "Trang", "Vị trí", "Thứ hạng", "URL", "Tiêu đề", "Domain mục tiêu", "Ngày tìm kiếm", "Ngày"]
display_columns = [col for col in column_order if col in filtered.columns]
filtered_display = filtered[display_columns].copy()
filtered_display.index = range(1, len(filtered_display) + 1)

st.dataframe(
    filtered_display.drop(columns=["Ngày_Sort"], errors="ignore"),
    width='stretch', height=600,
    column_config={
        "Thứ hạng": st.column_config.NumberColumn("Thứ hạng", format="%d"),
        "URL": st.column_config.LinkColumn("URL")
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

