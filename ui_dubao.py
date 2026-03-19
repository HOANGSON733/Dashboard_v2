"""
UI: Dự báo xu hướng - Forecasting
Clone UI theo ảnh: 2 cột (panel trái + metric + chart phải)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_loader import get_keyword_data
from helpers import forecast_rank


# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
DUBAO_CSS = """
<style>
/* ══ PAGE TITLE ══ */
.db-page-title {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
}
.db-page-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 24px 0;
}

/* ══ LEFT PANEL — border giả lập qua CSS column ══ */
.db-panel-label {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
}
.db-panel-hint {
    font-size: 12px;
    color: #6b7280;
    margin: 0 0 14px 0;
}

/* ── Selectbox antd style ── */
div[data-testid="stSelectbox"] > div > div {
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    background: #fff !important;
    font-size: 13.5px !important;
    color: #111827 !important;
    min-height: 40px !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* ── Slider antd style ── */
div[data-testid="stSlider"] > div > div > div > div {
    background: #3b82f6 !important;
}
.db-slider-label {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    margin: 20px 0 4px 0;
}

/* ── Primary button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #3b82f6 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    height: 42px !important;
    color: #fff !important;
    transition: background 0.2s !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #2563eb !important;
}

/* ══ METRIC CARDS ══ */
.db-metric-card {
    margin-bottom: 8px;
    background: #eef2ff;
    border-radius: 10px;
    padding: 14px 18px 16px 18px;
}
.db-metric-top {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: #4b5563;
    margin-bottom: 10px;
    font-weight: 500;
}
.db-metric-top svg, .db-metric-top .icon {
    font-size: 16px;
    color: #6366f1;
}
.db-metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    line-height: 1;
}
.db-metric-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #dcfce7;
    color: #16a34a;
    font-size: 11.5px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    margin-top: 6px;
}
.db-metric-badge.down {
    background: #fee2e2;
    color: #dc2626;
}
.db-metric-badge.neutral {
    background: #f3f4f6;
    color: #6b7280;
}
</style>
"""


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def _badge_html(delta: float, invert: bool = True) -> str:
    """Tạo badge % thay đổi, invert=True thì rank giảm = tốt."""
    if delta == 0:
        return '<span class="db-metric-badge neutral">→ 0%</span>'
    pct = abs(delta)
    if invert:
        good = delta < 0   # rank giảm = tăng hạng = tốt
    else:
        good = delta > 0
    arrow = "↑" if good else "↓"
    cls = "" if good else "down"
    return f'<span class="db-metric-badge {cls}">{arrow} {pct:.1f}%</span>'


def _trend_label(trend: str) -> str:
    mapping = {"up": "Tăng", "down": "Giảm", "stable": "Ổn định"}
    return mapping.get(trend, "N/A")


def _trend_badge(trend: str) -> str:
    if trend == "up":
        return '<span class="db-metric-badge">↑ Tích cực</span>'
    elif trend == "down":
        return '<span class="db-metric-badge down">↓ Suy giảm</span>'
    return '<span class="db-metric-badge neutral">→ Ổn định</span>'


# ─────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────
def render_dubao(df):
    """Render trang Dự báo xu hướng"""

    st.markdown(DUBAO_CSS, unsafe_allow_html=True)

    # ── Page title ──────────────────────────────────────────────────────
    st.markdown('<p class="db-page-title">Dự báo xu hướng</p>', unsafe_allow_html=True)
    st.markdown('<hr class="db-page-divider">', unsafe_allow_html=True)

    all_keywords = df["Từ khóa"].unique().tolist()

    # ── Layout: cột trái (panel) | cột phải (metrics + chart) ───────────
    col_left, col_right = st.columns([1, 1.8], gap="large")

    # ════════════════════════════════════════
    # PANEL TRÁI
    # ════════════════════════════════════════
    with col_left:
        # Label + hint
        st.markdown('<p class="db-panel-label">Chọn từ khoá để dự báo</p>', unsafe_allow_html=True)
        st.markdown('<p class="db-panel-hint">(Chọn tối thiểu 3 từ khoá để dự báo)</p>', unsafe_allow_html=True)

        forecast_keyword = st.selectbox(
            "Từ khoá", all_keywords,
            key="db_keyword",
            label_visibility="collapsed",
        )

        st.markdown('<p class="db-slider-label">Số ngày dự đoán</p>', unsafe_allow_html=True)
        forecast_days = st.slider(
            "Số ngày", min_value=1, max_value=99, value=7,
            key="db_days",
            label_visibility="collapsed",
        )

        # st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        # save_clicked = st.button("💾  Lưu mục tiêu", use_container_width=True, type="primary")

        # if save_clicked:
        #     st.success("✅ Đã lưu mục tiêu!")

    # ════════════════════════════════════════
    # CỘT PHẢI: metrics + chart
    # ════════════════════════════════════════
    with col_right:

        # ── Lấy dữ liệu ──────────────────────────────────────────────
        kw_data = get_keyword_data(df, forecast_keyword)
        has_data = len(kw_data) >= 3

        if not has_data:
            st.warning("⚠️ Cần ít nhất 3 điểm dữ liệu để dự báo.")
            return

        predictions, trend = forecast_rank(kw_data, forecast_days)

        if predictions is None:
            st.warning("⚠️ Không thể tính dự báo cho từ khoá này.")
            return

        current_rank = kw_data.iloc[-1]["Thứ hạng"]
        predicted_rank = predictions[-1]

        # ── Delta ─────────────────────────────────────────────────────
        delta_val = None
        delta_pct = None
        if pd.notna(current_rank) and pd.notna(predicted_rank):
            delta_val = predicted_rank - current_rank          # + = rank tụt, - = rank tăng
            if current_rank != 0:
                delta_pct = (delta_val / current_rank) * 100

        # ── 3 Metric cards ────────────────────────────────────────────
        current_str   = f"{int(current_rank)}" if pd.notna(current_rank) else "N/A"
        predicted_str = f"{int(predicted_rank)}" if pd.notna(predicted_rank) else "N/A"
        badge_forecast = _badge_html(delta_pct, invert=True) if delta_pct is not None else ""
        badge_trend    = _trend_badge(trend)
        trend_text     = _trend_label(trend)

        mc1, mc2, mc3 = st.columns(3)

        with mc1:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-top"><span class="icon">🏆</span> Hạng hiện tại</div>
                <div class="db-metric-value">{current_str}</div>
            </div>
            """, unsafe_allow_html=True)

        with mc2:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-top"><span class="icon">🔮</span> Dự báo ({forecast_days} ngày)</div>
                <div class="db-metric-value">{predicted_str}</div>
                {badge_forecast}
            </div>
            """, unsafe_allow_html=True)

        with mc3:
            st.markdown(f"""
            <div class="db-metric-card">
                <div class="db-metric-top"><span class="icon">📈</span> Xu hướng</div>
                <div class="db-metric-value" style="font-size:22px">{trend_text}</div>
                {badge_trend}
            </div>
            """, unsafe_allow_html=True)

        # ── Chart ─────────────────────────────────────────────────────
        historical_dates = kw_data["Ngày"].tolist()
        historical_ranks = kw_data["Thứ hạng"].tolist()

        last_date = kw_data["Ngày_Sort"].max()
        future_dates = [
            (last_date + timedelta(days=i + 1)).strftime("%d/%m")
            for i in range(forecast_days)
        ]

        # Nối điểm cuối lịch sử với điểm đầu dự báo để đường liên tục
        join_date  = [historical_dates[-1]] + future_dates
        join_ranks = [historical_ranks[-1]] + list(predictions)

        fig = go.Figure()

        # Vùng fill lịch sử
        fig.add_trace(go.Scatter(
            x=historical_dates,
            y=historical_ranks,
            mode="lines+markers",
            name="Lịch sử",
            line=dict(color="#6366f1", width=2.5, shape="spline", smoothing=0.8),
            marker=dict(
                size=6,
                color="#fff",
                line=dict(color="#6366f1", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
            hovertemplate="Ngày %{x}<br>Hạng: %{y}<extra></extra>",
        ))

        # Vùng fill dự báo
        fig.add_trace(go.Scatter(
            x=join_date,
            y=join_ranks,
            mode="lines+markers",
            name="Dự báo",
            line=dict(color="#a5b4fc", width=2, dash="dot", shape="spline", smoothing=0.8),
            marker=dict(
                size=6,
                color="#fff",
                line=dict(color="#a5b4fc", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(165,180,252,0.06)",
            hovertemplate="Dự báo %{x}<br>Hạng: %{y:.0f}<extra></extra>",
        ))

        # Đường phân cách lịch sử / dự báo
        fig.add_vline(
            x=historical_dates[-1],
            line_width=1,
            line_dash="dash",
            line_color="#d1d5db",
        )

        fig.update_yaxes(
            autorange="reversed",
            showgrid=True,
            gridcolor="#f3f4f6",
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=12, color="#6b7280"),
        )
        fig.update_xaxes(
            showgrid=False,
            tickfont=dict(size=10, color="#9ca3af"),
            tickangle=-40,
            nticks=12,
            automargin=True,
        )
        fig.update_layout(
            height=340,
            margin=dict(l=0, r=0, t=8, b=50),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12),
            ),
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════
    # PHÂN TÍCH CHI TIẾT — nằm bên col_left
    # ════════════════════════════════════════
    with col_left:
        if not has_data or predictions is None:
            return

        rank_series = kw_data["Thứ hạng"].dropna()
        rank_min    = int(rank_series.min())
        rank_max    = int(rank_series.max())
        rank_avg    = rank_series.mean()
        volatility  = rank_series.std()

        if len(rank_series) >= 7:
            velocity = (rank_series.iloc[-1] - rank_series.iloc[-7]) / 7
        elif len(rank_series) >= 2:
            velocity = (rank_series.iloc[-1] - rank_series.iloc[0]) / (len(rank_series) - 1)
        else:
            velocity = 0

        velocity_text = (
            f"↑ +{abs(velocity):.1f} hạng/ngày (tụt hạng)"
            if velocity > 0
            else f"↓ {abs(velocity):.1f} hạng/ngày (tăng hạng)"
            if velocity < 0
            else "Không đổi"
        )
        velocity_color = "#dc2626" if velocity > 0 else "#16a34a" if velocity < 0 else "#6b7280"

        best_day  = kw_data.loc[rank_series.idxmin(), "Ngày"]
        worst_day = kw_data.loc[rank_series.idxmax(), "Ngày"]

        if velocity < 0 and pd.notna(current_rank) and current_rank > 10:
            days_to_top10 = int((current_rank - 10) / abs(velocity))
            top10_est = f"~{days_to_top10} ngày"
        elif pd.notna(current_rank) and current_rank <= 10:
            top10_est = "Đã đạt Top 10 🎉"
        else:
            top10_est = "Chưa xác định"

        st.markdown("""
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0 12px 0">
        <p style="font-size:14px;font-weight:600;color:#111827;margin-bottom:12px">📊 Phân tích chi tiết</p>
        """, unsafe_allow_html=True)

        da1, da2 = st.columns(2)

        with da1:
            st.markdown(f"""
            <div style="background:#fafafa;border:1px solid #f0f0f0;border-radius:8px;padding:14px 16px;margin-bottom:10px">
                <div style="font-size:11px;color:#9ca3af;font-weight:500;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Biên độ dao động</div>
                <div style="font-size:20px;font-weight:700;color:#111827">Top {rank_min} – {rank_max}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">Trung bình: Top {rank_avg:.1f}</div>
            </div>
            <div style="background:#fafafa;border:1px solid #f0f0f0;border-radius:8px;padding:14px 16px">
                <div style="font-size:11px;color:#9ca3af;font-weight:500;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Ngày tốt nhất / tệ nhất</div>
                <div style="font-size:13px;color:#111827;line-height:1.8">
                    🟢 <b>Top {rank_min}</b> — {best_day}<br>
                    🔴 <b>Top {rank_max}</b> — {worst_day}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with da2:
            st.markdown(f"""
            <div style="background:#fafafa;border:1px solid #f0f0f0;border-radius:8px;padding:14px 16px;margin-bottom:10px">
                <div style="font-size:11px;color:#9ca3af;font-weight:500;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Tốc độ thay đổi</div>
                <div style="font-size:15px;font-weight:600;color:{velocity_color}">{velocity_text}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">Độ biến động: ±{volatility:.1f}</div>
            </div>
            <div style="background:#fafafa;border:1px solid #f0f0f0;border-radius:8px;padding:14px 16px">
                <div style="font-size:11px;color:#9ca3af;font-weight:500;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">Ước tính đạt Top 10</div>
                <div style="font-size:18px;font-weight:700;color:#111827">{top10_est}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:4px">Dựa trên tốc độ hiện tại</div>
            </div>
            """, unsafe_allow_html=True)