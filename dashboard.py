"""
dashboard.py
SEO Rank Dashboard Pro - Main Application
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import modules
from config import setup_page_config, get_custom_css, ANALYSIS_MODES
from auth import init_sheets_client
from persistence import save_session_state, init_session_state, clear_all_session_files, load_auth_state, load_marked_keywords, save_marked_keywords
from data_loader import load_sheet_data_cached, get_available_days, apply_filters, get_date_range_days

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
from streamlit_cookies_controller import CookieController
from db import SessionsManager

# ===================== INITIALIZE =====================
setup_page_config()
cookie_manager = CookieController()
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ===================== AUTH =====================
def restore_auth_from_cookie():
    """Restore auth silently with cookie priority"""
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


user_id = restore_auth_from_cookie()

if not user_id:
    st.warning("🔄 Session đã hết hạn do refresh trang. Vui lòng đăng nhập lại.")
    if st.button("Đăng nhập lại"):
        st.switch_page("pages/auth.py")
    st.stop()
else:
    st.session_state.pop("cookie_retry_dash", None)
    # Đảm bảo cookie được set nếu chưa có
    if st.session_state.get("session_token"):
        try:
            existing_token = cookie_manager.get("session_token")
            if not existing_token:
                cookie_manager.set("session_token", st.session_state["session_token"], max_age=72*3600)
        except Exception:
            pass
    # Load saved user session state including marked keywords from MongoDB
    try:
        init_session_state()
    except Exception:
        pass

# ===================== LOGO =====================
import base64
try:
    logo_base64 = base64.b64encode(open('LOGO1.png', 'rb').read()).decode()
except:
    logo_base64 = None

if 'sidebar_collapsed' not in st.session_state:
    st.session_state.sidebar_collapsed = False

if logo_base64:
    st.sidebar.markdown(f"""
        <div style='display:flex; justify-content:center; margin-bottom:-2rem; margin-top:0.5rem;'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo' style='width:180px; border-radius:12px; transform: translateY(-60px);'>
        </div>
    """, unsafe_allow_html=True)

# ===================== HEADER =====================
col_left, col_right = st.columns([4, 1])
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

    try:
        from user_auth import UserManager
        um = UserManager()
        user_doc = um.users.find_one({'username': user_id})
        if user_doc and user_doc.get('avatar_path'):
            st.session_state.avatar_path = user_doc.get('avatar_path')
    except:
        pass
    avatar_path = st.session_state.get('avatar_path')

    if avatar_path and os.path.exists(avatar_path):
        ext = avatar_path.rsplit('.', 1)[-1].replace('jpg', 'jpeg')
        src = f"data:image/{ext};base64," + _b64.b64encode(open(avatar_path, 'rb').read()).decode()
        avatar_html = f'<img src="{src}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid #3b82f6;">'
    else:
        initials = st.session_state.get('display_name', st.session_state.get('user_id', 'U'))[0].upper()
        avatar_html = f'<div style="width:42px;height:42px;border-radius:50%;background:#3b82f6;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:17px;border:2px solid #2563eb;">{initials}</div>'

    st.markdown(f"""
    <style>
    div[data-testid="column"]:last-child {{ display:flex;align-items:center;justify-content:flex-end; }}
    .avatar-link {{ display:inline-block;cursor:pointer;border-radius:50%;line-height:0;transition:transform .15s,box-shadow .15s;text-decoration:none; }}
    .avatar-link:hover {{ transform:scale(1.08);box-shadow:0 0 0 3px rgba(59,130,246,.35);border-radius:50%; }}
    </style>
    <a href="/profile" target="_self" class="avatar-link">{avatar_html}</a>
    """, unsafe_allow_html=True)

# ===================== SIDEBAR =====================
if 'user_id' in st.session_state:
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

    selected_config = next((cfg for cfg in user_sheets_config if cfg['domain'] == selected_domain), None)
    if not selected_config:
        st.error(f"❌ Không tìm thấy config cho domain {selected_domain}")
        st.stop()
    sheet_id = selected_config['sheet_id']

    client = init_sheets_client()
    if not client:
        st.error("❌ Sheets client unavailable")
        st.stop()
        
    sheet_map = get_available_days(sheet_id, client)
    if not sheet_map:
        st.warning("⚠️ No date sheets - check fallbacks. Using empty data.")
        sheet_map = {}

    if 'selected_days' not in locals():
        selected_days = [list(sheet_map.keys())[-1]]

    orig_len = len(selected_days)
    selected_days = [day for day in selected_days if day in sheet_map]
    if len(selected_days) < orig_len:
        st.sidebar.warning(f"⚠️ Filtered {orig_len - len(selected_days)} stale/missing days.")

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

max_days = 365
total_available_days = len(sheet_map) if 'sheet_map' in locals() else 0
if total_available_days > max_days:
    st.sidebar.warning(f"⚠️ Có {total_available_days} ngày dữ liệu. Khuyến nghị chọn ≤ {max_days} ngày.")

st.sidebar.markdown("**📅 Chọn khoảng thời gian**")
use_date_range = st.sidebar.checkbox("Sử dụng bộ chọn khoảng", value=False)

if 'filtered_date_range' not in st.session_state:
    st.session_state.filtered_date_range = None

if use_date_range and 'sheet_map' in locals():
    available_dates = sorted([v.date() for v in sheet_map.values()])
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.selectbox("Từ ngày", options=available_dates, index=0, format_func=lambda x: x.strftime("%d/%m/%Y"))
    with col_end:
        end_date = st.selectbox("Đến ngày", options=available_dates, index=len(available_dates)-1, format_func=lambda x: x.strftime("%d/%m/%Y"))
    if st.sidebar.button("Lọc"):
        if start_date > end_date:
            st.sidebar.error("❌ Ngày bắt đầu phải trước hoặc bằng ngày kết thúc")
        else:
            range_days = get_date_range_days(sheet_map, start_date, end_date)
            if range_days:
                st.session_state.filtered_date_range = [d for d in range_days if d in sheet_map]
            else:
                st.sidebar.warning("⚠️ Không có dữ liệu trong khoảng ngày đã chọn")
    if st.session_state.filtered_date_range:
        selected_days = st.session_state.filtered_date_range
else:
    if 'sheet_map' in locals():
        day_options = sorted(sheet_map.keys(), key=lambda x: sheet_map[x])
        current_index = 0 if not selected_days else max(0, day_options.index(selected_days[0]) if selected_days[0] in day_options else 0)
        selected_day = st.sidebar.selectbox("📅 Chọn ngày", options=day_options, index=current_index)
        selected_days = [selected_day]

if not selected_days:
    st.info("ℹ️ No days selected - using latest available")
    if sheet_map:
        selected_days = [list(sheet_map.keys())[-1]]

if len(selected_days) > max_days:
    st.sidebar.error(f"⚠️ Đã chọn {len(selected_days)} ngày!")
elif len(selected_days) > 15:
    st.sidebar.warning(f"📊 Đã chọn {len(selected_days)} ngày")

st.sidebar.divider()
st.sidebar.markdown("**📊 Chế độ phân tích**")
analysis_mode = st.sidebar.radio("Chọn chế độ", ANALYSIS_MODES, index=0, label_visibility="collapsed")

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
if 'user_id' in st.session_state:
    df, sheet_map = load_sheet_data_cached(client, sheet_id, selected_days)
    if df is None or df.empty:
        st.warning("⚠️ Không có dữ liệu")
        st.stop()
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
st.markdown('<p class="section-header">📄 Bảng dữ liệu chi tiết</p>', unsafe_allow_html=True)
st.markdown(f"**Hiển thị {len(filtered):,} từ khóa**")

column_order = ["Từ khóa", "Trang", "Vị trí", "Thứ hạng", "URL", "Tiêu đề", "Domain mục tiêu", "Ngày tìm kiếm", "Ngày"]
display_columns = [col for col in column_order if col in filtered.columns]
filtered_display = filtered[display_columns].copy()
filtered_display.index = range(1, len(filtered_display) + 1)

from persistence import load_marked_keywords, save_marked_keywords

if 'marked_keywords' not in st.session_state:
    st.session_state.marked_keywords = load_marked_keywords()

def _normalize_mark_key(keyword, day_value):
    if isinstance(day_value, (datetime,)):
        day_value = day_value.strftime("%d-%m-%Y")
    return (str(keyword).strip(), str(day_value).strip())

ngay_col = 'Ngày' if 'Ngày' in filtered_display.columns else 'Ngày tìm kiếm'
filtered_display.insert(
    0, '⭐',
    filtered_display.apply(lambda r: _normalize_mark_key(r['Từ khóa'], r[ngay_col]) in st.session_state.marked_keywords, axis=1)
)

st.markdown("""
<style>
[data-testid="stDataFrame"] tr:nth-child(even) td { background-color: rgba(59,130,246,0.05) !important; }
[data-testid="stDataFrame"] thead tr th {
    background-color: rgba(21,87,212,0.08) !important;
    font-weight: 700 !important; font-size: 13px !important;
    border-bottom: 2px solid rgba(21,87,212,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

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

if '⭐' in edited_df.columns and 'Từ khóa' in edited_df.columns:
    for _, row in edited_df.iterrows():
        key = _normalize_mark_key(row['Từ khóa'], row[ngay_col])
        if row['⭐']:
            st.session_state.marked_keywords.add(key)
        else:
            st.session_state.marked_keywords.discard(key)
    save_marked_keywords()

## Không hiển thị thêm bảng 'Đã đánh dấu' theo yêu cầu

csv = filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="⬇️ Tải xuống dữ liệu (CSV)",
    data=csv,
    file_name=f"seo_data_{selected_domain}_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

save_session_state()
