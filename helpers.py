"""
Các hàm helper xử lý dữ liệu SEO
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import calendar
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter


# ===================== DATE HELPERS =====================
def extract_date(sheet_name: str):
    """Trích xuất ngày từ tên sheet"""
    try:
        return datetime.strptime(sheet_name.replace("Ngày_", ""), "%d_%m_%Y")
    except:
        return None


def get_date_worksheets(sheet):
    """Lấy danh sách worksheet theo ngày"""
    result = []
    for ws in sheet.worksheets():
        if ws.title.startswith("Ngày_"):
            dt = extract_date(ws.title)
            if dt:
                result.append((ws.title, dt))
    result.sort(key=lambda x: x[1])
    return result


# ===================== RANK HELPERS =====================
def compare_ranks(old_rank, new_rank):
    """So sánh thứ hạng giữa 2 ngày"""
    if pd.isna(old_rank) and pd.isna(new_rank):
        return "Không đổi hạng", 0, "⚪"
    elif pd.isna(old_rank) and not pd.isna(new_rank):
        return "Mới có rank", 0, "🆕"
    elif not pd.isna(old_rank) and pd.isna(new_rank):
        return "Mất rank", 0, "❌"
    else:
        change = old_rank - new_rank
        if change > 0:
            return "Tăng hạng", change, "📈"
        elif change < 0:
            return "Giảm hạng", change, "📉"
        else:
            return "Không đổi hạng", 0, "➡️"


def rank_group(rank):
    """Nhóm thứ hạng"""
    if pd.isna(rank):
        return "Chưa có rank"
    elif rank <= 3:
        return "Top 3"
    elif rank <= 10:
        return "Top 10"
    elif rank <= 20:
        return "Top 20"
    else:
        return "Ngoài Top 20"


# ===================== KEYWORD HELPERS =====================
def extract_keyword_groups(keywords):
    """Nhóm từ khóa theo cụm từ"""
    groups = {}
    for kw in keywords:
        words = str(kw).lower().split()
        if len(words) >= 2:
            group = ' '.join(words[:2])
        else:
            group = words[0] if words else 'Khác'
        
        if group not in groups:
            groups[group] = []
        groups[group].append(kw)
    
    filtered_groups = {k: v for k, v in groups.items() if len(v) >= 3}
    grouped_kws = set([kw for kws in filtered_groups.values() for kw in kws])
    other_kws = [kw for kw in keywords if kw not in grouped_kws]
    
    if other_kws:
        filtered_groups['Khác'] = other_kws
    
    return filtered_groups


# ===================== SEO SCORE CALCULATION =====================
def calculate_seo_score(df):
    """
    Tính SEO Performance Score (0-100)
    - Top 3: 10 điểm
    - Top 10: 5 điểm
    - Top 20: 2 điểm
    - Không rank: 0.5 điểm
    - Max: 100 điểm (khi tất cả từ khóa trong Top 3)
    """
    if df.empty:
        return 0
    
    total = len(df)
    top3 = (df["Thứ hạng"] <= 3).sum()
    top10 = ((df["Thứ hạng"] > 3) & (df["Thứ hạng"] <= 10)).sum()
    top20 = ((df["Thứ hạng"] > 10) & (df["Thứ hạng"] <= 20)).sum()
    no_rank = df["Thứ hạng"].isna().sum()
    outside_top20 = total - top3 - top10 - top20 - no_rank
    
    score = (
        (top3 * 10) +
        (top10 * 5) +
        (top20 * 2) +
        (outside_top20 * 0.5) +
        (no_rank * 0)
    )
    
    max_score = total * 10
    final_score = (score / max_score * 100) if max_score > 0 else 0
    
    return round(min(final_score, 100), 1)


# ===================== FORECASTING =====================
def forecast_rank(kw_data, days_ahead=7):
    """Dự báo thứ hạng sử dụng linear regression"""
    if len(kw_data) < 3:
        return None, None
    
    kw_data = kw_data.sort_values("Ngày_Sort")
    kw_data = kw_data[kw_data["Thứ hạng"].notna()]
    
    if len(kw_data) < 3:
        return None, None
    
    X = np.array(range(len(kw_data))).reshape(-1, 1)
    y = kw_data["Thứ hạng"].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.array(range(len(kw_data), len(kw_data) + days_ahead)).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    trend = "up" if model.coef_[0] < 0 else "down" if model.coef_[0] > 0 else "stable"
    
    return predictions, trend


# ===================== AI INSIGHTS =====================
def generate_ai_insights(df, comparison_data=None):
    """Tạo AI insights tự động"""
    insights = []
    
    # Top performers
    top_kws = df[df["Thứ hạng"] <= 3].groupby("Từ khóa").size().nlargest(3)
    if not top_kws.empty:
        insights.append({
            "type": "success",
            "title": "🌟 Top Performers",
            "message": f"Từ khóa '{top_kws.index[0]}' đang có hiệu suất xuất sắc với {top_kws.values[0]} lần xuất hiện trong Top 3."
        })
    
    # Declining keywords
    if comparison_data is not None and not comparison_data.empty:
        declining = comparison_data[comparison_data["Thay đổi"] < -5]
        if len(declining) > 0:
            insights.append({
                "type": "warning",
                "title": "⚠️ Cần chú ý",
                "message": f"{len(declining)} từ khóa đang giảm >5 bậc. Cần review và tối ưu lại content."
            })
    
    # Opportunity
    near_top10 = df[(df["Thứ hạng"] > 10) & (df["Thứ hạng"] <= 15)]
    if len(near_top10) > 0:
        insights.append({
            "type": "info",
            "title": "💡 Cơ hội",
            "message": f"{len(near_top10)} từ khóa đang ở vị trí 11-15. Đây là cơ hội tốt để push vào Top 10!"
        })
    
    # URL analysis
    url_counts = df[df["URL"].notna() & (~df["URL"].str.contains("Không có kết quả", na=False))].groupby("URL").size()
    if not url_counts.empty and url_counts.max() > 10:
        top_url = url_counts.idxmax()
        insights.append({
            "type": "success",
            "title": "🔗 URL xuất sắc",
            "message": f"URL '{top_url[:50]}...' đang rank cho {url_counts.max()} từ khóa. Nên mở rộng nội dung liên quan."
        })
    
    return insights


# ===================== HEATMAP CALENDAR =====================
def create_heatmap_data(df, year, month):
    """Tạo dữ liệu heatmap calendar"""
    daily_scores = {}
    daily_keywords = {}
    
    for _, row in df.iterrows():
        date = row["Ngày_Sort"]
        if pd.notna(date) and date.year == year and date.month == month:
            day = date.day
            day_data = df[df["Ngày_Sort"] == date]
            score = calculate_seo_score(day_data)
            daily_scores[day] = score
            daily_keywords[day] = len(day_data)
    
    return daily_scores, daily_keywords


def get_calendar_heatmap(year, month, daily_scores, daily_keywords):
    """Tạo heatmap từ dữ liệu"""
    cal = calendar.monthcalendar(year, month)
    weekdays = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    
    heatmap_data = []
    text_data = []
    hover_data = []
    
    for week in cal:
        week_scores = []
        week_text = []
        week_hover = []
        
        for day in week:
            if day == 0:
                week_scores.append(None)
                week_text.append("")
                week_hover.append("")
            else:
                score = daily_scores.get(day, 0)
                kw_count = daily_keywords.get(day, 0)
                week_scores.append(score)
                week_text.append(str(day))
                
                if score > 0:
                    if score >= 81:
                        label = "Xuất sắc"
                    elif score >= 61:
                        label = "Tốt"
                    elif score >= 41:
                        label = "Trung bình"
                    else:
                        label = "Yếu"
                    week_hover.append(f"Ngày {day}<br>Score: {score:.1f}/100<br>{label}<br>{kw_count} từ khóa")
                else:
                    week_hover.append(f"Ngày {day}<br>Không có dữ liệu")
        
        heatmap_data.append(week_scores)
        text_data.append(week_text)
        hover_data.append(week_hover)
    
    return heatmap_data, text_data, hover_data, weekdays


# ===================== DATA CLEANING =====================
def clean_rank_data(df):
    """Làm sạch dữ liệu thứ hạng"""
    df = df.copy()
    
    # Clean rank column
    df["Thứ hạng"] = (
        df["Thứ hạng"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["Thứ hạng"] = pd.to_numeric(df["Thứ hạng"], errors="coerce")
    
    # Clean page column
    df["Trang"] = (
        df["Trang"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["Trang"] = pd.to_numeric(df["Trang"], errors="coerce")
    
    # Clean position column
    df["Vị trí"] = (
        df["Vị trí"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["Vị trí"] = pd.to_numeric(df["Vị trí"], errors="coerce")
    
    return df


def normalize_columns(df):
    """Chuẩn hóa các cột DataFrame"""
    expected_columns = [
        "Từ khóa", "Trang", "Vị trí", "Thứ hạng", "URL",
        "Tiêu đề", "Domain mục tiêu", "Ngày tìm kiếm", "Ngày", "Ngày_Sort"
    ]
    
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""
    
    return df


# ===================== CHARTS =====================
def create_rank_distribution_chart(filtered):
    """Tạo biểu đồ phân bố thứ hạng"""
    filtered["Nhóm hạng"] = filtered["Thứ hạng"].apply(rank_group)
    chart_rank = filtered.groupby("Nhóm hạng").size().reset_index(name="Số lượng")
    return chart_rank


def create_trend_chart(filtered):
    """Tạo biểu đồ xu hướng theo thời gian"""
    # Handle empty or invalid filtered data
    if filtered is None or filtered.empty:
        return pd.DataFrame(columns=["Ngày", "Top 3", "Top 10", "Top 20"])
    
    trend_data = filtered[filtered["Thứ hạng"].notna()].copy()
    
    # Handle case where no ranked keywords exist
    if trend_data.empty:
        return pd.DataFrame(columns=["Ngày", "Top 3", "Top 10", "Top 20"])
    
    trend_data = trend_data.sort_values("Ngày_Sort")
    
    trend_top3 = trend_data[trend_data["Thứ hạng"] <= 3].groupby("Ngày")["Từ khóa"].count().reset_index(name="Top 3")
    trend_top10 = trend_data[trend_data["Thứ hạng"] <= 10].groupby("Ngày")["Từ khóa"].count().reset_index(name="Top 10")
    trend_top20 = trend_data[trend_data["Thứ hạng"] <= 20].groupby("Ngày")["Từ khóa"].count().reset_index(name="Top 20")
    
    trend = trend_top3.merge(trend_top10, on="Ngày", how="outer").merge(trend_top20, on="Ngày", how="outer").fillna(0)
    
    # Ensure numeric types
    trend["Top 3"] = trend["Top 3"].astype(int)
    trend["Top 10"] = trend["Top 10"].astype(int)
    trend["Top 20"] = trend["Top 20"].astype(int)
    
    return trend


def create_comparison_chart(comparison):
    """Tạo biểu đồ so sánh"""
    status_counts = comparison["Trạng thái"].value_counts().reset_index()
    status_counts.columns = ["Trạng thái", "Số lượng"]
    return status_counts

