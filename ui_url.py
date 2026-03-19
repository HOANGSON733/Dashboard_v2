"""
UI: Phân tích URL
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import get_url_stats, get_url_declining


def render_url(filtered, df):
    """Render trang Phân tích URL"""

    st.markdown("""
    <style>
    .url-section-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
    }
    .url-divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 0 0 20px 0;
    }
    .metric-card {
        background: #f9fafb;
        border: 0.5px solid #e5e7eb;
        border-radius: 10px;
        padding: 18px 20px;
    }
    .metric-icon-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 10px;
    }
    .metric-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .metric-number {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }
    .metric-badge-up {
        background: #dcfce7;
        color: #166534;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
    }
    .url-sub-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        margin: 20px 0 12px 0;
    }
    .declining-card {
        border: 0.5px solid #e5e7eb;
        border-radius: 8px;
        padding: 12px 14px;
        background: #fff;
    }
    .declining-url {
        font-size: 12px;
        color: #2563eb;
        margin: 2px 0 6px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .declining-badge {
        background: #fee2e2;
        color: #991b1b;
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    url_stats = get_url_stats(filtered)

    # ── Tiêu đề ────────────────────────────────────────────────────────────────
    st.markdown('<p class="url-section-title">Tổng quan hiệu suất URL</p>', unsafe_allow_html=True)
    st.markdown('<hr class="url-divider">', unsafe_allow_html=True)

    if url_stats.empty:
        st.warning("⚠️ Không có dữ liệu URL")
        return

    # ── 3 Metric cards ─────────────────────────────────────────────────────────
    total_urls    = len(url_stats)
    best_url_kw   = int(url_stats.iloc[0]["Số từ khóa"]) if not url_stats.empty else 0
    avg_kw_per_url = url_stats["Số từ khóa"].mean()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-label">🔗 Tổng URL</div>
            <div class="metric-row">
                <span class="metric-number">{total_urls}</span>
                <span class="metric-badge-up">↗ 2.0%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-label">👍 URL tốt nhất</div>
            <div class="metric-row">
                <span class="metric-number">{best_url_kw}</span>
                <span class="metric-badge-up">↗ 2.0%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon-label">⭐ TB từ khoá/URL</div>
            <div class="metric-row">
                <span class="metric-number">{avg_kw_per_url:.1f} / 10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Phân tích hiệu suất URL ────────────────────────────────────────────────
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="url-section-title">Phân tích hiệu suất URL</p>', unsafe_allow_html=True)
    st.markdown('<hr class="url-divider">', unsafe_allow_html=True)

    top10 = url_stats.head(10).copy()
    top10["URL_short"] = top10["URL"].str.replace(r"https?://", "", regex=True).str[:40]

    col_chart, col_table = st.columns([1, 1.2], gap="medium")

    with col_chart:
        fig = go.Figure(go.Bar(
            x=top10["Rank TB"].round(2),
            y=top10["URL_short"],
            orientation="h",
            text=top10["Rank TB"].round(2),
            textposition="outside",
            marker=dict(
                color=top10["Rank TB"],
                colorscale="Blues",
                reversescale=True,
                showscale=False,
            ),
        ))
        fig.update_layout(
            height=380,
            margin=dict(l=8, r=40, t=8, b=8),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f3f4f6", tickfont=dict(size=11)),
            yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        table_data = url_stats.head(10).copy().reset_index(drop=True)
        table_data.index = table_data.index + 1
        table_data.index = table_data.index.map(lambda x: f"{x:02d}")
        table_data["URL"] = table_data["URL"].str[:50] + "..."
        table_data["Rank TB"] = table_data["Rank TB"].apply(
            lambda x: f"{x:.0f}" if pd.notna(x) else "None"
        )
        table_data["Rank tốt nhất"] = table_data["Rank tốt nhất"].apply(
            lambda x: f"{x:.0f}" if pd.notna(x) else "None"
        )
        table_data = table_data.rename(columns={"Số từ khóa": "Số từ khoá"})
        st.dataframe(
            table_data[["URL", "Số từ khoá", "Rank TB", "Rank tốt nhất"]],
            use_container_width=True,
            height=380,
            hide_index=False,
        )

    # ── URL cần tối ưu ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:15px;font-weight:600;color:#d97706">⚠️ URL cần tối ưu (nhiều từ khoá giảm hạng)</p>',
        unsafe_allow_html=True,
    )

    declining = get_url_declining(df)

    if declining.empty:
        st.info("Không có URL nào giảm hạng trong kỳ này.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(declining.iterrows()):
            with cols[i % 3]:
                url_display = row["URL"]
                url_short   = url_display.replace("https://", "").replace("http://", "")
                change_val  = int(row["Thay đổi"])
                st.markdown(f"""
                <div class="declining-card">
                    <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:4px;
                                overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                        {url_display[:45]}
                    </div>
                    <div class="declining-url">{url_short[:50]}</div>
                    <span class="declining-badge">↘ -{change_val}</span>
                </div>
                <div style="margin-bottom:10px"></div>
                """, unsafe_allow_html=True)

