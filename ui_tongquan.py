"""
UI: Tổng quan Dashboard - Card layout dùng st.container(border=True)
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit_echarts import st_echarts
from datetime import datetime
from persistence import save_session_state
from helpers import calculate_seo_score, create_rank_distribution_chart, create_trend_chart


def make_gauge_chart(value, max_val, unit, color="#1f6feb"):
    if value is None or (isinstance(value, float) and pd.isna(value)) or (isinstance(value, str) and value.strip() == ""):
        value = 0
    if max_val is None or (isinstance(max_val, float) and pd.isna(max_val)) or max_val == 0 or (isinstance(max_val, str) and max_val.strip() == ""):
        max_val = 1
    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0
    try:
        max_val = float(max_val)
    except (ValueError, TypeError):
        max_val = 1

    percent = value / max_val if max_val > 0 else 0
    percent = max(0, min(1, percent))

    option = {
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0,
            "max": int(max_val),
            "radius": "100%",
            "center": ["50%", "70%"],
            "progress": {"show": True, "width": 18, "roundCap": True, "itemStyle": {"color": color}},
            "axisLine": {
                "lineStyle": {
                    "width": 18,
                    "color": [[percent, color], [1, "#e5e7eb"]]
                }
            },
            "axisTick": {"show": False},
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "pointer": {"show": False},
            "detail": {
                "formatter": f"{{value}}/{int(max_val)}\n{unit}",
                "fontSize": 24,
                "fontWeight": "700",
                "color": "#0f172a",
                "offsetCenter": [0, "-5%"]
            },
            "data": [{"value": int(value)}]
        }]
    }
    st_echarts(option, height="200px")


def make_mini_line(x_labels, y_values, color="#7c3aed", height=130):
    try:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        fill_color = f"rgba({r},{g},{b},0.10)"
    except Exception:
        fill_color = "rgba(124,58,237,0.10)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_values,
        mode="lines+markers+text",
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=7, color=color, line=dict(color="#fff", width=1.5)),
        text=[None] * (len(y_values) - 1) + [str(y_values[-1])],
        textposition="top right",
        textfont=dict(size=11, color=color, family="DM Sans, sans-serif"),
        fill="tozeroy",
        fillcolor=fill_color,
    ))
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=28, t=8, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=True, gridcolor="#f3f4f6", gridwidth=1,
            zeroline=False, tickfont=dict(size=10, color="#9ca3af"), showline=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#f3f4f6", gridwidth=1,
            zeroline=False, tickfont=dict(size=10, color="#9ca3af"), showline=False,
        ),
    )
    return fig


def render_tongquan(filtered, sheet_map, selected_days):
    """Render trang Tổng quan"""

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

    /* Enhanced card containers with hover effects */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 12px 32px rgba(0,0,0,0.06) !important;
        background: linear-gradient(145deg, #ffffff, #fafbfc) !important;
        transition: all 0.3s ease !important;
        min-height: 240px !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12), 0 20px 48px rgba(0,0,0,0.10) !important;
    }
    @media (max-width: 768px) {
        [data-testid="stVerticalBlockBorderWrapper"] { min-height: 220px !important; }
    }

    .card-title {
        font-size: 13px; font-weight: 700; color: #374151;
        margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
    }
    .badge-green {
        background: #d1fae5; color: #065f46; font-size: 10px; font-weight: 700;
        padding: 2px 8px; border-radius: 20px; display: inline-block;
    }
    .badge-blue {
        background: #dbeafe; color: #1e40af; font-size: 10px; font-weight: 700;
        padding: 2px 8px; border-radius: 20px; display: inline-block;
    }
    .rank-bar-row { margin-bottom: 9px; }
    .rank-bar-labels {
        display: flex; justify-content: space-between;
        font-size: 11px; color: #6b7280; margin-bottom: 3px;
    }
    .rank-bar-track { background: #f3f4f6; border-radius: 6px; height: 8px; overflow: hidden; }
    .rank-bar-fill  { height: 100%; border-radius: 6px; }
    .kw-item {
        display: flex; align-items: center; gap: 10px;
        padding: 6px 10px; border-radius: 8px;
        margin-bottom: 6px; background: #f9fafb;
    }
    .kw-badge {
        min-width: 50px; height: 22px; border-radius: 20px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 11px; font-weight: 700; white-space: nowrap;
    }
    .kw-label { font-size: 12px; color: #374151; line-height: 1.4; }
    .insight-box {
        background: #fefce8; border: 1px solid #fde68a; border-radius: 10px;
        padding: 12px 14px; font-size: 12px; color: #78350f; line-height: 1.6;
    }
    .alert-box { border-radius: 8px; padding: 10px 14px; font-size: 12px; margin-bottom: 8px; }
    .alert-critical { background: #fef2f2; border-left: 3px solid #ef4444; }
    .alert-warning  { background: #fffbeb; border-left: 3px solid #f59e0b; }
    .alert-success  { background: #f0fdf4; border-left: 3px solid #10b981; }
    .alert-info     { background: #eff6ff; border-left: 3px solid #3b82f6; }
    .section-header {
        font-size: 15px; font-weight: 700; color: #111827;
        margin: 20px 0 12px; padding-bottom: 6px;
        border-bottom: 2px solid #f3f4f6;
    }
    .stButton>button {
        border-radius: 8px !important; font-size: 13px !important;
        font-weight: 500 !important; border: 1px solid #d1d5db !important;
        background: #fff !important; color: #374151 !important; padding: 8px 16px !important;
    }
    .stButton>button:hover { background: #f9fafb !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Quick Actions (bên phải) ─────────────────────────────────────────────────
    # ── Quick Actions ─────────────────────────────────────────────────────────────
    col_empty, col_btns = st.columns([5, 3])
    with col_btns:
        st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button,
        div[data-testid="stHorizontalBlock"] > div:nth-child(3) button,
        div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {
            border-radius: 10px !important;
            border: 1.5px solid #e5e7eb !important;
            background: #ffffff !important;
            color: #374151 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 9px 14px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.07) !important;
            height: auto !important;
        }
        </style>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📄 Export PDF", width="stretch"):
                st.info("Đang phát triển...")
        with c2:
            if st.button("📊 Create Snapshot", width="stretch"):
                domain = st.session_state.get("selected_domain", "Unknown")
                name = f"{domain[:20]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                st.session_state.snapshots[name] = {
                    "date": datetime.now(), 
                    "domain": domain,
                    "data": filtered.copy(),
                    "score": calculate_seo_score(filtered), 
                    "note": ""
                }
                try:
                    save_session_state()
                except Exception:
                    pass
                st.session_state.selected_snapshot = name
                st.success(f"✅ {name} ({domain})")
        with c3:
            if st.button("🔄 Refresh Data", width="stretch"):
                st.rerun()

    st.markdown('<p class="section-header">Tổng quan hiệu suất</p>', unsafe_allow_html=True)

    from data_loader import get_comparison_data
    from helpers import generate_ai_insights
    comparison_data = get_comparison_data(filtered, selected_days, sheet_map)
    insights = generate_ai_insights(filtered, comparison_data)

    score     = calculate_seo_score(filtered)
    total_kw  = len(filtered)
    ranked_kw = int(filtered["Thứ hạng"].notna().sum())

    trend       = create_trend_chart(filtered)
    week_labels = list(trend["Ngày"].astype(str))[-3:] if not trend.empty else ["Tuần 1", "Tuần 2", "Tuần 3"]
    top3_vals   = list(trend["Top 3"])[-3:]    if not trend.empty else [0, 0, 0]
    top10_vals  = list(trend["Top 10"])[-3:]   if not trend.empty else [0, 0, 0]
    norank_vals = list(trend["Chưa rank"])[-3:] if (not trend.empty and "Chưa rank" in trend.columns) else [0, 0, 0]

    def _delta(vals):
        if vals[0]:
            sign = "↑" if vals[-1] >= vals[0] else "↓"
            return f"{sign} {abs((vals[-1]-vals[0])/max(vals[0],1)*100):.1f}%"
        return "—"

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT: 4 cột — card trái | card giữa | (Top3 + NoRank) | (Top10 + KWlist)
    # ══════════════════════════════════════════════════════════════════════════
    col_left, col_mid, col_r1, col_r2 = st.columns([1.1, 1.2, 1.2, 1.3])

    # ── CARD 1: SEO Score + AI Insights ──────────────────────────────────────
    with col_left:
        st.markdown('<div style="padding: 0.5rem 0;"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "<div style='padding: 1.5rem; text-align:center;'>"
                "<div style='font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;'>"
                "SEO Performance Score</div>"
                "</div>",
                unsafe_allow_html=True
            )
            make_gauge_chart(score, 100, "điểm", color="#3b82f6")

            st.divider()

            st.markdown('<div class="card-title" style="padding: 0 1.5rem 0.5rem;">🤖 AI Insights</div>', unsafe_allow_html=True)
            top_insight = next((i for i in insights if i["type"] == "success"), None)
            if top_insight:
                st.markdown(f"""
                <div class="insight-box" style="margin: 0 1.5rem 1rem;">
                    <strong style="color:#92400e">🥇 {top_insight['title']}</strong><br/>
                    {top_insight['message']}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="insight-box" style="margin: 0 1.5rem 1rem;"><strong style="color:#92400e">📊 Đang phân tích...</strong>'
                    '<br/>Chưa có đủ dữ liệu.</div>',
                    unsafe_allow_html=True
                )

    # ── CARD 2: Tổng từ khoá + Phân bố thứ hạng ─────────────────────────────
    with col_mid:
        st.markdown('<div style="padding: 0.5rem 0;"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                "<div style='padding: 1.5rem; text-align:center;'>"
                "<div style='font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;'>"
                "Tổng số từ khoá</div>"
                "</div>",
                unsafe_allow_html=True
            )
            make_gauge_chart(ranked_kw, total_kw, "từ khoá", color="#3b82f6")

            st.divider()

            st.markdown('<div class="card-title" style="padding: 0 1.5rem 0.5rem;">📊 Phân bố thứ hạng</div>', unsafe_allow_html=True)
            chart_rank = create_rank_distribution_chart(filtered)
            if not chart_rank.empty:
                clr_map = {
                    "Top 3": "#10b981", "Top 4–10": "#3b82f6",
                    "Top 11–20": "#f59e0b", "Ngoài Top 20": "#ef4444", "Chưa có rank": "#9ca3af"
                }
                total_r = chart_rank["Số lượng"].sum() or 1
                for _, row in chart_rank.iterrows():
                    pct   = row["Số lượng"] / total_r * 100
                    color = clr_map.get(row["Nhóm hạng"], "#6b7280")
                    st.markdown(f"""
                    <div class="rank-bar-row" style="padding: 0 1.5rem;">
                        <div class="rank-bar-labels">
                            <span>{row['Nhóm hạng']}</span>
                            <span style="font-weight:700;color:#374151">{pct:.1f}%</span>
                        </div>
                        <div class="rank-bar-track">
                            <div class="rank-bar-fill" style="width:{pct}%;background:{color}"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

    # ── CỘT R1: Top 3 card + Chưa rank card ──────────────────────────────────
    with col_r1:
        with st.container(border=True):
            st.markdown(f"""
            <div class="card-title">
                🥇 Top 3 tìm kiếm nhiều nhất
                <span class="badge-green">{_delta(top3_vals)}</span>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(
                make_mini_line(week_labels, top3_vals, "#7c3aed"),
                width="stretch", config={"displayModeBar": False}, key="top3_trend"
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"""
            <div class="card-title">
                ❌ Chưa có rank tìm kiếm
                <span class="badge-green">{_delta(norank_vals)}</span>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(
                make_mini_line(week_labels, norank_vals, "#7c3aed"),
                width="stretch", config={"displayModeBar": False}, key="norank_trend"
            )

    # ── CỘT R2: Top 10 card + Keyword list card ───────────────────────────────
    with col_r2:
        with st.container(border=True):
            st.markdown(f"""
            <div class="card-title">
                🏆 Top 10 tìm kiếm nhiều nhất
                <span class="badge-blue">{_delta(top10_vals)}</span>
            </div>""", unsafe_allow_html=True)
            st.plotly_chart(
                make_mini_line(week_labels, top10_vals, "#7c3aed"),
                width="stretch", config={"displayModeBar": False}, key="top10_trend"
            )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="card-title">📋 Xếp hạng từ khoá tìm kiếm</div>', unsafe_allow_html=True)
            top_kws = filtered[filtered["Thứ hạng"].notna()].nsmallest(5, "Thứ hạng")
            for _, row in top_kws.iterrows():
                rank = int(row["Thứ hạng"])
                if rank <= 3:
                    color, bg, label = "#10b981", "#d1fae5", f"Top {rank}"
                elif rank <= 10:
                    color, bg, label = "#3b82f6", "#dbeafe", f"Top {rank}"
                elif rank <= 20:
                    color, bg, label = "#f59e0b", "#fef3c7", f"Top {rank}"
                else:
                    color, bg, label = "#9ca3af", "#f3f4f6", f"Top {rank}"
                st.markdown(f"""
                <div class="kw-item">
                    <span class="kw-badge" style="background:{bg};color:{color}">{label}</span>
                    <span class="kw-label">{row['Từ khóa']}</span>
                </div>""", unsafe_allow_html=True)

    # ── Alerts ────────────────────────────────────────────────────────────────
    if comparison_data is not None:
        st.markdown('<p class="section-header">🔔 Thông báo quan trọng</p>', unsafe_allow_html=True)

        critical_drop = comparison_data[comparison_data["Thay đổi"] < -10].nlargest(5, "Thay đổi", keep='all')
        big_jump      = comparison_data[comparison_data["Thay đổi"] > 5].nlargest(5, "Thay đổi", keep='all')
        new_top3      = comparison_data[(comparison_data["Rank_New"] <= 3) & (comparison_data["Rank_Old"] > 3)]
        dropped_top10 = comparison_data[(comparison_data["Rank_Old"] <= 10) & (comparison_data["Rank_New"] > 10)]

        col1, col2 = st.columns(2)
        with col1:
            if not critical_drop.empty:
                st.markdown('<div class="alert-box alert-critical">⚠️ <strong>Từ khóa giảm mạnh (>10 bậc)</strong></div>', unsafe_allow_html=True)
                with st.expander(f"📋 Xem {len(critical_drop)} từ khóa", expanded=False):
                    for _, row in critical_drop.iterrows():
                        st.write(f"• **{row['Từ khóa']}**: {row['Rank_Old']:.0f} → {row['Rank_New']:.0f} ({row['Thay đổi']:.0f})")
            if not dropped_top10.empty:
                st.markdown('<div class="alert-box alert-warning">📉 <strong>Rơi khỏi Top 10</strong></div>', unsafe_allow_html=True)
                with st.expander(f"📋 Xem {len(dropped_top10)} từ khóa", expanded=False):
                    for _, row in dropped_top10.iterrows():
                        st.write(f"• **{row['Từ khóa']}**: {row['Rank_Old']:.0f} → {row['Rank_New']:.0f}")
        with col2:
            if not big_jump.empty:
                st.markdown('<div class="alert-box alert-success">🎉 <strong>Tăng hạng mạnh (>5 bậc)</strong></div>', unsafe_allow_html=True)
                with st.expander(f"📋 Xem {len(big_jump)} từ khóa", expanded=False):
                    for _, row in big_jump.iterrows():
                        st.write(f"• **{row['Từ khóa']}**: {row['Rank_Old']:.0f} → {row['Rank_New']:.0f} (+{row['Thay đổi']:.0f})")
            if not new_top3.empty:
                st.markdown('<div class="alert-box alert-info">🏆 <strong>Mới vào Top 3</strong></div>', unsafe_allow_html=True)
                with st.expander(f"📋 Xem {len(new_top3)} từ khóa", expanded=False):
                    for _, row in new_top3.iterrows():
                        st.write(f"• **{row['Từ khóa']}**: {row['Rank_Old']:.0f} → {row['Rank_New']:.0f}")

    # ── Keyword Lists by Group ────────────────────────────────────────────────
    st.markdown('<p class="section-header">📋 Danh sách từ khóa theo nhóm hạng</p>', unsafe_allow_html=True)

    top3_kws          = filtered[(filtered["Thứ hạng"] <= 3)  & filtered["Thứ hạng"].notna()].sort_values("Thứ hạng")
    top10_kws         = filtered[(filtered["Thứ hạng"] > 3)   & (filtered["Thứ hạng"] <= 10) & filtered["Thứ hạng"].notna()].sort_values("Thứ hạng")
    top20_kws         = filtered[(filtered["Thứ hạng"] > 10)  & (filtered["Thứ hạng"] <= 20) & filtered["Thứ hạng"].notna()].sort_values("Thứ hạng")
    outside_top20_kws = filtered[(filtered["Thứ hạng"] > 20)  & filtered["Thứ hạng"].notna()].sort_values("Thứ hạng")
    no_rank_kws       = filtered[filtered["Thứ hạng"].isna()]

    col1, col2 = st.columns(2)
    with col1:
        with st.expander(f"🥇 Top 3 ({len(top3_kws)})", expanded=False):
            [st.markdown(f"• **{r['Từ khóa']}** — Hạng {r['Thứ hạng']:.0f}") for _, r in top3_kws.iterrows()] if not top3_kws.empty else st.info("Không có từ khóa nào")
        with st.expander(f"🏆 Top 10 ({len(top10_kws)})", expanded=False):
            [st.markdown(f"• **{r['Từ khóa']}** — Hạng {r['Thứ hạng']:.0f}") for _, r in top10_kws.iterrows()] if not top10_kws.empty else st.info("Không có từ khóa nào")
        with st.expander(f"🎯 Top 20 ({len(top20_kws)})", expanded=False):
            [st.markdown(f"• **{r['Từ khóa']}** — Hạng {r['Thứ hạng']:.0f}") for _, r in top20_kws.iterrows()] if not top20_kws.empty else st.info("Không có từ khóa nào")
    with col2:
        with st.expander(f"📈 Ngoài Top 20 ({len(outside_top20_kws)})", expanded=False):
            display = outside_top20_kws.head(50)
            [st.markdown(f"• **{r['Từ khóa']}** — Hạng {r['Thứ hạng']:.0f}") for _, r in display.iterrows()] if not display.empty else st.info("Không có từ khóa nào")
            if len(outside_top20_kws) > 50:
                st.info(f"Chỉ hiển thị 50/{len(outside_top20_kws)} từ khóa.")
        with st.expander(f"❌ Chưa có rank ({len(no_rank_kws)})", expanded=False):
            display = no_rank_kws.head(50)
            [st.markdown(f"• **{r['Từ khóa']}**") for _, r in display.iterrows()] if not display.empty else st.info("Tất cả từ khóa đều có rank")
            if len(no_rank_kws) > 50:
                st.info(f"Chỉ hiển thị 50/{len(no_rank_kws)} từ khóa.")