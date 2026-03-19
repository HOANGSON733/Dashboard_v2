"""
UI: Phân tích từ khóa
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import (
    get_keyword_data,
    get_keyword_data_by_month,
    get_keyword_stats,
    get_available_months,
)


def render_keyword(filtered, df):
    """Render trang Phân tích từ khóa"""

    st.markdown("""
    <style>
    .kw-section-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
    }
    .kw-divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 0 0 20px 0;
    }
    .stat-label {
        font-size: 13px;
        font-weight: 600;
        margin: 0 0 3px 0;
    }
    .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #111827;
        margin: 0 0 14px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    all_keywords = filtered["Từ khóa"].unique().tolist()

    # ══════════════════════════════════════════════════════════════════════════
    # PHẦN 1: Phân tích từ khoá cụ thể
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('<p class="kw-section-title">Phân tích từ khoá cụ thể</p>', unsafe_allow_html=True)
    st.markdown('<hr class="kw-divider">', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2.8], gap="medium")

    with col_left:
        with st.container(border=True):
            selected_keyword = st.selectbox(
                "Chọn từ khoá để phân tích",
                all_keywords,
                key="specific_kw",
            )

            if selected_keyword:
                kw_data = get_keyword_data(df, selected_keyword)
                stats = get_keyword_stats(kw_data) if not kw_data.empty else {}

                st.markdown("<hr style='border-color:#f3f4f6;margin:12px 0'>", unsafe_allow_html=True)

                # ── Hạng hiện tại ──────────────────────────────────────────
                current = stats.get("latest_rank") if stats else None
                change  = stats.get("trend_change") if stats else None
                current_str = f"{current:.0f}" if pd.notna(current) else "N/A"

                if pd.notna(change) and change != 0:
                    sign        = "+" if change > 0 else ""
                    badge_bg    = "#dcfce7" if change > 0 else "#fee2e2"
                    badge_color = "#166534" if change > 0 else "#991b1b"
                    arrow       = "↑" if change > 0 else "↓"
                    badge_html  = (
                        f'<span style="background:{badge_bg};color:{badge_color};'
                        f'font-size:12px;font-weight:600;padding:2px 9px;'
                        f'border-radius:12px;margin-left:6px">'
                        f'{arrow} {sign}{change:.0f}</span>'
                    )
                else:
                    badge_html = ""

                st.markdown(
                    f'<p class="stat-label">📍 <span style="color:#2563eb">Hạng hiện tại</span></p>'
                    f'<p class="stat-value">{current_str}{badge_html}</p>',
                    unsafe_allow_html=True,
                )

                # ── Hạng tốt nhất ──────────────────────────────────────────
                best = stats.get("best_rank") if stats else None
                best_str = f"{best:.0f}" if pd.notna(best) else "N/A"
                st.markdown(
                    f'<p class="stat-label">🏆 <span style="color:#d97706">Hạng tốt nhất</span></p>'
                    f'<p class="stat-value">{best_str}</p>',
                    unsafe_allow_html=True,
                )

                # ── Hạng trung bình ────────────────────────────────────────
                avg = stats.get("avg_rank") if stats else None
                avg_str = f"{avg:.1f}" if pd.notna(avg) else "N/A"
                st.markdown(
                    f'<p class="stat-label">🥈 <span style="color:#6b7280">Hạng trung bình</span></p>'
                    f'<p class="stat-value">{avg_str}</p>',
                    unsafe_allow_html=True,
                )

                # ── Hạng thay đổi ──────────────────────────────────────────
                trend_str = f"{change:+.0f}" if pd.notna(change) else "N/A"
                st.markdown(
                    f'<p class="stat-label">📊 <span style="color:#2563eb">Hạng thay đổi</span></p>'
                    f'<p class="stat-value">{trend_str}</p>',
                    unsafe_allow_html=True,
                )

    with col_right:
        with st.container(border=True):
            if selected_keyword:
                kw_data = get_keyword_data(df, selected_keyword)

                st.markdown(
                    '<p style="font-size:16px;font-weight:600;color:#2563eb;margin-bottom:8px">'
                    'Lịch sử thứ hạng theo ngày</p>',
                    unsafe_allow_html=True,
                )

                if not kw_data.empty:
                    y_max = kw_data["Thứ hạng"].max()
                    y_ceil = max(y_max * 1.2, y_max + 10)

                    fig = go.Figure()
                    # trace nền để fill hướng lên (do trục Y đảo ngược)
                    fig.add_trace(go.Scatter(
                        x=kw_data["Ngày"],
                        y=[y_ceil] * len(kw_data),
                        mode="lines",
                        line=dict(width=0, shape="spline"),
                        showlegend=False,
                        hoverinfo="skip",
                    ))
                    fig.add_trace(go.Scatter(
                        x=kw_data["Ngày"],
                        y=kw_data["Thứ hạng"],
                        mode="lines+markers",
                        name=selected_keyword,
                        line=dict(color="#f87171", width=2.5, shape="spline", smoothing=1.2),
                        marker=dict(size=6, color="#f87171"),
                        fill="tonexty",
                        fillcolor="rgba(248,113,113,0.08)",
                    ))
                    fig.update_yaxes(
                        autorange="reversed",
                        title=None,
                        gridcolor="#f3f4f6",
                        tickfont=dict(size=11),
                    )
                    fig.update_xaxes(
                        title=None,
                        showgrid=False,
                        tickfont=dict(size=11),
                    )
                    fig.update_layout(
                        height=280,
                        hovermode="x unified",
                        margin=dict(l=8, r=8, t=8, b=8),
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # ── Bảng Chi tiết theo ngày ────────────────────────────
                    st.markdown(
                        '<p style="font-size:14px;font-weight:600;margin:4px 0 6px">📄 Chi tiết theo ngày</p>',
                        unsafe_allow_html=True,
                    )
                    cols_show = [c for c in ["Ngày", "Thứ hạng", "URL", "Tiêu đề"] if c in kw_data.columns]
                    st.dataframe(kw_data[cols_show], use_container_width=True, hide_index=True)
                else:
                    st.info("Không có dữ liệu cho từ khoá này.")

    # ══════════════════════════════════════════════════════════════════════════
    # PHẦN 2: So sánh nhiều từ khoá
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='margin-top:36px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="kw-section-title">So sánh nhiều từ khoá</p>', unsafe_allow_html=True)
    st.markdown('<hr class="kw-divider">', unsafe_allow_html=True)

    col_left2, col_right2 = st.columns([1, 2.8], gap="medium")

    with col_left2:
        with st.container(border=True):
            st.markdown(
                '<p style="font-size:13px;color:#374151;margin-bottom:2px">Chọn từ khoá để phân tích</p>'
                '<p style="font-size:12px;color:#9ca3af;margin-bottom:8px">(Chọn tối đa 5 từ khoá)</p>',
                unsafe_allow_html=True,
            )
            compare_keywords = st.multiselect(
                label="",
                options=all_keywords,
                max_selections=5,
                key="compare_kws",
                label_visibility="collapsed",
            )

    with col_right2:
        with st.container(border=True):
            # ── Header: tiêu đề + dropdown tháng ──────────────────────────
            available_months = get_available_months(df)
            month_labels = [m["label"] for m in available_months]

            hdr_left, hdr_right = st.columns([3, 1])
            with hdr_left:
                st.markdown(
                    '<p style="font-size:16px;font-weight:600;color:#2563eb;margin-bottom:4px">'
                    'Lịch sử thứ hạng theo tháng</p>',
                    unsafe_allow_html=True,
                )
            with hdr_right:
                if month_labels:
                    selected_month_label = st.selectbox(
                        "",
                        month_labels,
                        key="month_select",
                        label_visibility="collapsed",
                    )
                    selected_month_info = next(
                        m for m in available_months if m["label"] == selected_month_label
                    )
                else:
                    selected_month_info = None

            # ── Biểu đồ ───────────────────────────────────────────────────
            if compare_keywords and selected_month_info:
                COLORS = ["#667eea", "#f87171", "#10b981", "#f59e0b", "#3b82f6"]

                fig_multi = go.Figure()
                for idx, kw in enumerate(compare_keywords):
                    kw_month = get_keyword_data_by_month(
                        df, kw,
                        month=selected_month_info["month"],
                        year=selected_month_info["year"],
                    )
                    if kw_month.empty:
                        continue
                    fig_multi.add_trace(go.Scatter(
                        x=kw_month["Ngày"],
                        y=kw_month["Thứ hạng"],
                        mode="lines+markers",
                        name=kw,
                        line=dict(color=COLORS[idx % len(COLORS)], width=2, shape="spline", smoothing=1.2),
                        marker=dict(size=7),
                    ))

                fig_multi.update_yaxes(
                    autorange="reversed",
                    title=None,
                    gridcolor="#f3f4f6",
                    tickfont=dict(size=11),
                )
                fig_multi.update_xaxes(
                    title=None,
                    showgrid=False,
                    tickfont=dict(size=11),
                )
                fig_multi.update_layout(
                    height=340,
                    hovermode="x unified",
                    margin=dict(l=8, r=8, t=8, b=8),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12),
                    ),
                )
                st.plotly_chart(fig_multi, use_container_width=True)

            elif not compare_keywords:
                st.info("Chọn ít nhất một từ khoá để xem biểu đồ so sánh.")
            else:
                st.info("Không có dữ liệu trong tháng đã chọn.")