"""
UI: Lịch nhiệt - Performance Heatmap Calendar
Clone theo ảnh mẫu: grid HTML, stats panel bên phải, legend bên dưới
"""

import streamlit as st
import calendar
from helpers import create_heatmap_data, get_calendar_heatmap


# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
LICHNHIET_CSS = """
<style>
/* ══ PAGE TITLE ══ */
.lh-page-title {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
}
.lh-page-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 20px 0;
}

/* ══ SECTION LABEL ══ */
.lh-section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 600;
    color: #2563eb;
    margin: 20px 0 16px 0;
}

/* ══ CALENDAR TABLE ══ */
.lh-cal {
    width: 100%;
    border-collapse: separate;
    border-spacing: 5px;
    font-size: 13px;
    table-layout: fixed;
}
.lh-cal th {
    text-align: center;
    font-weight: 500;
    color: #6b7280;
    font-size: 12.5px;
    padding: 6px 0;
}
.lh-cal th.lh-week-col {
    width: 56px;
    color: #9ca3af;
    font-size: 12px;
    text-align: center;
}
.lh-cal td.lh-week-label {
    width: 56px;
    font-size: 12px;
    color: #9ca3af;
    white-space: nowrap;
    vertical-align: middle;
    text-align: center;
}

/* ══ DAY CELL ══ */
.lh-day {
    height: 60px;
    border-radius: 8px;
    text-align: center;
    vertical-align: middle;
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    cursor: default;
}
.lh-day.empty {
    background: transparent;
    border: none;
}
.lh-day.no-data {
    background: #f3f4f6;
    color: #c9cdd4;
    font-weight: 500;
}
.lh-day.red    { background: #ef4444; }
.lh-day.orange { background: #f59e0b; }
.lh-day.blue   { background: #3b82f6; }
.lh-day.green  { background: #10b981; }

/* ══ STATS PANEL ══ */
.lh-stats {
    width: 100%;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 18px 18px 18px;
    background: #fff;
}
.lh-stats-title {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 18px 0;
}
.lh-stat-block { margin-bottom: 16px; }
.lh-stat-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    font-weight: 500;
    margin-bottom: 4px;
}
.lh-stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
}

/* ══ LEGEND ══ */
.lh-legend {
    display: flex;
    gap: 24px;
    margin-top: 14px;
    flex-wrap: wrap;
}
.lh-legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: #374151;
}
.lh-legend-dot {
    width: 22px;
    height: 22px;
    border-radius: 5px;
    flex-shrink: 0;
}
</style>
"""


# ─────────────────────────────────────────
# HELPER: score → css class
# ─────────────────────────────────────────
def _score_class(score):
    if score is None: return "no-data"
    if score <= 40:   return "red"
    if score <= 60:   return "orange"
    if score <= 80:   return "blue"
    return "green"


# ─────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────
def render_lichnhiet(df):
    st.markdown(LICHNHIET_CSS, unsafe_allow_html=True)

    st.markdown('<p class="lh-page-title">Quản lý xu hướng lịch nhiệt</p>', unsafe_allow_html=True)
    st.markdown('<hr class="lh-page-divider">', unsafe_allow_html=True)

    # ── Filters ──
    fc1, fc2 = st.columns(2)
    with fc1:
        year = st.selectbox("Năm", range(2020, 2030), index=6, key="lh_year", label_visibility="hidden")
    with fc2:
        month = st.selectbox("Tháng", range(1, 13), index=2, key="lh_month", label_visibility="hidden")

    st.markdown(
        f'<div class="lh-section-label">📅 Lịch hiệu suất Tháng {month}/{year}</div>',
        unsafe_allow_html=True,
    )

    # ── Build data ──
    daily_scores, daily_keywords = create_heatmap_data(df, year, month)

    # ── Build calendar HTML ──
    weeks = calendar.monthcalendar(year, month)
    day_headers = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    header_row = '<th class="lh-week-col">Giờ</th>' + "".join(f"<th>{d}</th>" for d in day_headers)

    body_rows = ""
    for wi, week in enumerate(weeks):
        cells = f'<td class="lh-week-label">Tuần {wi+1}</td>'
        for day in week:
            if day == 0:
                cells += '<td class="lh-day empty"></td>'
            else:
                score = daily_scores.get(day)
                cls   = _score_class(score)
                cells += f'<td class="lh-day {cls}">{day:02d}</td>'
        body_rows += f"<tr>{cells}</tr>"

    calendar_html = f"""
    <table class="lh-cal">
        <thead><tr>{header_row}</tr></thead>
        <tbody>{body_rows}</tbody>
    </table>
    """

    # ── Tính stats ──
    if daily_scores:
        avg_score  = round(sum(daily_scores.values()) / len(daily_scores), 2)
        max_score  = round(max(daily_scores.values()), 2)
        min_score  = round(min(daily_scores.values()), 2)
        best_day   = max(daily_scores, key=daily_scores.get)
        best_label = f"{best_day:02d}/{month:02d}"
    else:
        avg_score = max_score = min_score = "—"
        best_label = "—"

    # ── Render: calendar trái, stats phải ──
    col_cal, col_stats = st.columns([3, 1])

    with col_cal:
        st.markdown(calendar_html, unsafe_allow_html=True)

    with col_stats:
        st.markdown('<div class="lh-stats"><p class="lh-stats-title">Thống kê nhanh</p></div>', unsafe_allow_html=True)

        for icon, label, val, color in [
            ("↕️", "Score trung bình", f"{avg_score}/100", "#2563eb"),
            ("↗️", "Cao nhất",         f"{max_score}/100", "#10b981"),
            ("↘️", "Thấp nhất",        f"{min_score}/100", "#ef4444"),
            ("📅", "Ngày tốt nhất",    best_label,         "#111827"),
        ]:
            st.markdown(f"""
            <div class="lh-stat-block">
                <div class="lh-stat-label" style="color:{color}">{icon} {label}</div>
                <div class="lh-stat-value">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Legend ──
    st.markdown("""
    <div class="lh-legend">
        <div class="lh-legend-item"><div class="lh-legend-dot" style="background:#ef4444"></div> Yếu (0-40)</div>
        <div class="lh-legend-item"><div class="lh-legend-dot" style="background:#f59e0b"></div> Trung bình (41-60)</div>
        <div class="lh-legend-item"><div class="lh-legend-dot" style="background:#3b82f6"></div> Tốt (61-80)</div>
        <div class="lh-legend-item"><div class="lh-legend-dot" style="background:#10b981"></div> Xuất sắc (81-100)</div>
    </div>
    """, unsafe_allow_html=True)