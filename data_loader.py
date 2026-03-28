"""
Load dữ liệu từ Google Sheets
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from helpers import extract_date, get_date_worksheets, clean_rank_data, normalize_columns
from auth import get_gcp_credentials


# ===================== LOAD SHEET DATA =====================
@st.cache_data(ttl=3600)
def load_sheet_data_cached(_client, sheet_id, selected_days):
    """Load và cache dữ liệu từ Google Sheets"""
    import gspread
    from google.oauth2 import service_account

    creds_dict = get_gcp_credentials()
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)

    try:
        sh = client.open_by_key(sheet_id)
        date_sheets = get_date_worksheets(sh)

        if not date_sheets:
            return None, None

        sheet_map = {name: dt for name, dt in date_sheets}
        
        # Filter to only available days to prevent KeyError
        valid_days = [day for day in selected_days if day in sheet_map]
        missing_days = set(selected_days) - set(sheet_map.keys())
        if missing_days:
            st.warning(f"⚠️ Missing sheets for days: {', '.join(sorted(missing_days))}. Using {len(valid_days)}/{len(selected_days)} available days.")

        all_data = []
        for ws_name in valid_days:
            try:

                ws = sh.worksheet(ws_name)
                rows = ws.get_all_records()
                df_day = pd.DataFrame(rows)

                if df_day.empty:
                    continue

                df_day["Ngày"] = sheet_map[ws_name].strftime("%d-%m-%Y")
                df_day["Ngày_Sort"] = sheet_map[ws_name]
                all_data.append(df_day)
            except Exception as e:
                st.warning(f"⚠️ Lỗi tải sheet '{ws_name}': {str(e)}")
                continue

        if not all_data:
            return None, None

        df = pd.concat(all_data, ignore_index=True)
        df = normalize_columns(df)
        df = clean_rank_data(df)

        return df, sheet_map

    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        return None, None


def get_available_days(sheet_id, client):
    """Lấy danh sách các ngày có dữ liệu"""
    try:
        sh = client.open_by_key(sheet_id)
        date_sheets = get_date_worksheets(sh)
        return {name: dt for name, dt in date_sheets}
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        return {}


def apply_filters(df, keyword_filter="", rank_limit=100, only_no_rank=False, only_with_rank=False):
    """Áp dụng bộ lọc cho dữ liệu"""
    filtered = df.copy()

    if keyword_filter:
        filtered = filtered[
            filtered["Từ khóa"]
            .astype(str)
            .str.contains(keyword_filter, case=False, na=False)
        ]

    if only_no_rank and only_with_rank:
        pass
    elif only_no_rank:
        filtered = filtered[filtered["Thứ hạng"].isna()]
    elif only_with_rank:
        filtered = filtered[filtered["Thứ hạng"].notna()]
    else:
        filtered = filtered[
            (filtered["Thứ hạng"].isna()) |
            (filtered["Thứ hạng"] <= rank_limit)
        ]

    return filtered


# ===================== QUICK DATE SELECTION =====================
def get_quick_date_options(sheet_map):
    """Lấy các tùy chọn chọn nhanh ngày"""
    options = {}

    recent_days = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:7]
    options["7 ngày gần nhất"] = recent_days

    recent_30 = sorted(list(sheet_map.keys()), key=lambda x: sheet_map[x], reverse=True)[:30]
    options["30 ngày gần nhất"] = recent_30

    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_str = f"Ngày_{day.day:02d}_{day.month:02d}_{day.year}"
        if day_str in sheet_map:
            week_days.append(day_str)
    if week_days:
        options["Tuần này"] = week_days

    month_days = [k for k, v in sheet_map.items() if v.year == today.year and v.month == today.month]
    if month_days:
        options["Tháng này"] = sorted(month_days, key=lambda x: sheet_map[x])

    return options


def get_date_range_days(sheet_map, start_date, end_date):
    """Lấy danh sách ngày trong khoảng thời gian"""
    range_days = [k for k, v in sheet_map.items() if start_date <= v.date() <= end_date]
    return sorted(range_days, key=lambda x: sheet_map[x])


# ===================== COMPARISON DATA =====================
def get_comparison_data(filtered, selected_days, sheet_map):
    """Tạo dữ liệu so sánh giữa 2 ngày"""
    # Filter valid days to prevent KeyError
    valid_days = [d for d in selected_days if d in sheet_map]
    if len(valid_days) < 2:
        st.warning("⚠️ Need at least 2 valid days in sheet_map for comparison.")
        return None
    
    dates_sorted = sorted(valid_days, key=lambda x: sheet_map[x])
    latest_date = sheet_map[dates_sorted[-1]].strftime("%d-%m-%Y")
    prev_date = sheet_map[dates_sorted[-2]].strftime("%d-%m-%Y")

    df_latest = filtered[filtered["Ngày"] == latest_date][["Từ khóa", "Thứ hạng"]].copy()
    df_prev = filtered[filtered["Ngày"] == prev_date][["Từ khóa", "Thứ hạng"]].copy()

    df_latest.rename(columns={"Thứ hạng": "Rank_New"}, inplace=True)
    df_prev.rename(columns={"Thứ hạng": "Rank_Old"}, inplace=True)

    comparison_data = pd.merge(df_prev, df_latest, on="Từ khóa", how="inner")
    comparison_data["Thay đổi"] = comparison_data["Rank_Old"] - comparison_data["Rank_New"]

    return comparison_data


# ===================== KEYWORD ANALYSIS =====================
def get_keyword_data(df, keyword):
    """Lấy dữ liệu của một từ khóa cụ thể"""
    kw_data = df[df["Từ khóa"] == keyword].sort_values("Ngày_Sort")
    return kw_data


def get_keyword_data_by_month(df, keyword, month, year):
    """
    Lấy dữ liệu của một từ khóa trong một tháng cụ thể.
    Dùng cho biểu đồ so sánh nhiều từ khoá theo tháng.

    Args:
        df      : DataFrame toàn bộ dữ liệu
        keyword : tên từ khoá
        month   : số tháng (1–12)
        year    : năm (int)

    Returns:
        DataFrame đã lọc và sắp xếp theo ngày
    """
    kw_data = df[df["Từ khóa"] == keyword].copy()
    kw_data = kw_data[
        (kw_data["Ngày_Sort"].dt.month == month) &
        (kw_data["Ngày_Sort"].dt.year == year)
    ]
    return kw_data.sort_values("Ngày_Sort")


def get_available_months(df):
    """
    Trả về danh sách các tháng có dữ liệu, dạng list of dict:
        [{"label": "Tháng 3/2025", "month": 3, "year": 2025}, ...]
    Sắp xếp mới nhất lên đầu.
    """
    if "Ngày_Sort" not in df.columns:
        return []

    months = (
        df[["Ngày_Sort"]]
        .dropna()
        .assign(month=lambda x: x["Ngày_Sort"].dt.month,
                year=lambda x: x["Ngày_Sort"].dt.year)
        [["month", "year"]]
        .drop_duplicates()
        .sort_values(["year", "month"], ascending=False)
    )

    result = []
    for _, row in months.iterrows():
        result.append({
            "label": f"Tháng {int(row['month'])}/{int(row['year'])}",
            "month": int(row["month"]),
            "year": int(row["year"]),
        })
    return result


def get_keyword_stats(kw_data):
    """Tính thống kê cho một từ khóa"""
    if kw_data.empty:
        return None

    latest_rank = kw_data.iloc[-1]["Thứ hạng"]
    best_rank = kw_data["Thứ hạng"].min() if kw_data["Thứ hạng"].notna().any() else None
    avg_rank = kw_data["Thứ hạng"].mean() if kw_data["Thứ hạng"].notna().any() else None

    trend_change = 0
    if len(kw_data) > 1:
        first_rank = kw_data.iloc[0]["Thứ hạng"]
        if pd.notna(latest_rank) and pd.notna(first_rank):
            trend_change = latest_rank - first_rank

    return {
        "latest_rank": latest_rank,
        "best_rank": best_rank,
        "avg_rank": avg_rank,
        "trend_change": trend_change,
    }


# ===================== URL ANALYSIS =====================
def get_url_stats(filtered):
    """Tính thống kê theo URL"""
    url_data = filtered[filtered["URL"].notna() & (filtered["URL"] != "")].copy()

    if url_data.empty:
        return pd.DataFrame()

    url_stats = url_data.groupby("URL").agg({
        "Từ khóa": "count",
        "Thứ hạng": ["mean", "min"]
    }).reset_index()

    url_stats.columns = ["URL", "Số từ khóa", "Rank TB", "Rank tốt nhất"]
    url_stats = url_stats.sort_values("Số từ khóa", ascending=False)

    return url_stats


def get_url_declining(df, top_n=9):
    """
    Tìm các URL có nhiều từ khoá đang giảm hạng nhất.
    So sánh ngày mới nhất vs ngày liền trước.
    Returns DataFrame: URL, Thay đổi (dương = giảm hạng), Số từ khoá giảm
    """
    url_data = df[df["URL"].notna() & (df["URL"] != "") & df["Thứ hạng"].notna()].copy()
    if url_data.empty or "Ngày_Sort" not in url_data.columns:
        return pd.DataFrame()
    dates = sorted(url_data["Ngày_Sort"].dt.date.unique())
    if len(dates) < 2:
        return pd.DataFrame()
    latest_date = dates[-1]
    prev_date   = dates[-2]
    df_latest = url_data[url_data["Ngày_Sort"].dt.date == latest_date][["URL", "Từ khóa", "Thứ hạng"]].rename(columns={"Thứ hạng": "Rank_New"})
    df_prev   = url_data[url_data["Ngày_Sort"].dt.date == prev_date][["URL", "Từ khóa", "Thứ hạng"]].rename(columns={"Thứ hạng": "Rank_Old"})
    merged = pd.merge(df_prev, df_latest, on=["URL", "Từ khóa"], how="inner")
    merged["Thay đổi"] = merged["Rank_New"] - merged["Rank_Old"]
    declining = (
        merged[merged["Thay đổi"] > 0]
        .groupby("URL")
        .agg({"Thay đổi": "sum", "Từ khóa": "count"})
        .reset_index()
        .rename(columns={"Từ khóa": "Số từ khoá giảm"})
        .sort_values("Thay đổi", ascending=False)
        .head(top_n)
    )
    return declining



def get_url_comparison(url_data, selected_days, sheet_map):
    """So sánh URL giữa 2 ngày"""
    # Filter valid days to prevent KeyError
    valid_days = [d for d in selected_days if d in sheet_map]
    if len(valid_days) < 2:
        st.warning("⚠️ Need at least 2 valid days in sheet_map for URL comparison.")
        return pd.DataFrame()
    
    dates_sorted = sorted(valid_days, key=lambda x: sheet_map[x])
    latest_date = sheet_map[dates_sorted[-1]].strftime("%d-%m-%Y")
    prev_date = sheet_map[dates_sorted[-2]].strftime("%d-%m-%Y")

    url_latest = url_data[url_data["Ngày"] == latest_date][["URL", "Từ khóa", "Thứ hạng"]].copy()
    url_prev = url_data[url_data["Ngày"] == prev_date][["URL", "Từ khóa", "Thứ hạng"]].copy()

    url_latest.rename(columns={"Thứ hạng": "Rank_New"}, inplace=True)
    url_prev.rename(columns={"Thứ hạng": "Rank_Old"}, inplace=True)

    url_comp = pd.merge(url_prev, url_latest, on=["URL", "Từ khóa"], how="inner")
    url_comp["Change"] = url_comp["Rank_Old"] - url_comp["Rank_New"]

    return url_comp