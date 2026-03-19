"""
UI: Nhóm từ khóa - Keyword grouping analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from helpers import extract_keyword_groups


def render_nhomkeyword(filtered):
    """Render trang Nhóm từ khóa"""

    st.markdown("""
    <style>
    .nhom-section-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 4px;
    }
    .nhom-divider {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 0 0 20px 0;
    }
    .nhom-metric-card {
        background: #f0f4ff;
        border: 0.5px solid #e0e7ff;
        border-radius: 12px;
        padding: 18px 20px 20px 20px;
        min-height: 110px;
    }
    .nhom-metric-top {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 13px;
        color: #4b5563;
        margin-bottom: 14px;
    }
    .nhom-metric-bottom {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nhom-metric-number {
        font-size: 30px;
        font-weight: 700;
        color: #111827;
    }
    .nhom-metric-text {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
    }
    .nhom-badge-up {
        background: #dcfce7;
        color: #166534;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Tiêu đề ────────────────────────────────────────────────────────────────
    st.markdown('<p class="nhom-section-title">Phân tích theo nhóm từ khoá</p>', unsafe_allow_html=True)
    st.markdown('<hr class="nhom-divider">', unsafe_allow_html=True)

    keyword_groups = extract_keyword_groups(filtered["Từ khóa"].unique())

    if not keyword_groups:
        st.warning("⚠️ Không tìm thấy nhóm từ khoá nào.")
        return

    # ── Tính group stats ───────────────────────────────────────────────────────
    group_stats = []
    for group_name, keywords in keyword_groups.items():
        group_data = filtered[filtered["Từ khóa"].isin(keywords)]
        group_stats.append({
            "Nhóm": group_name,
            "Số từ khóa": len(keywords),
            "Top 3": (group_data["Thứ hạng"] <= 3).sum(),
            "Top 10": (group_data["Thứ hạng"] <= 10).sum(),
            "Rank TB": group_data["Thứ hạng"].mean() if group_data["Thứ hạng"].notna().any() else None,
            "Chưa rank": group_data["Thứ hạng"].isna().sum(),
        })

    df_groups = pd.DataFrame(group_stats).sort_values("Số từ khóa", ascending=False)

    total_groups  = len(keyword_groups)
    largest_count = int(df_groups.iloc[0]["Số từ khóa"]) if not df_groups.empty else 0
    best_row      = df_groups.dropna(subset=["Rank TB"]).nsmallest(1, "Rank TB")
    best_name     = best_row.iloc[0]["Nhóm"] if not best_row.empty else "N/A"

    # ── 3 Metric cards ─────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="nhom-metric-card">
            <div class="nhom-metric-top">
                <span style="font-size:18px">🔗</span> Số nhóm từ khoá
            </div>
            <div class="nhom-metric-bottom">
                <span class="nhom-metric-number">{total_groups}</span>
                <span class="nhom-badge-up">↗ 2.0%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="nhom-metric-card">
            <div class="nhom-metric-top">
                <span style="font-size:18px">📦</span> Nhóm lớn nhất
            </div>
            <div class="nhom-metric-bottom">
                <span class="nhom-metric-number">{largest_count}</span>
                <span class="nhom-badge-up">↗ 2.0%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="nhom-metric-card">
            <div class="nhom-metric-top">
                <span style="font-size:18px">👍</span> Nhóm tốt nhất
            </div>
            <div class="nhom-metric-bottom">
                <span class="nhom-metric-text">{best_name}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 2 cột: chart + bảng ────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

    col_chart, col_table = st.columns([1, 1.2], gap="medium")

    with col_chart:
        with st.container(border=True):
            # Header: tiêu đề + dropdown
            hdr_l, hdr_r = st.columns([1.6, 1])
            with hdr_l:
                st.markdown(
                    '<p style="font-size:16px;font-weight:600;color:#2563eb;margin-bottom:4px">'
                    'Hiệu xuất theo nhóm chi tiết</p>',
                    unsafe_allow_html=True,
                )
            with hdr_r:
                selected_group = st.selectbox(
                    "",
                    list(keyword_groups.keys()),
                    key="nhom_select",
                    label_visibility="collapsed",
                )

            # Chart đường rank TB theo ngày của nhóm đã chọn
            if selected_group:
                group_kws   = keyword_groups[selected_group]
                group_data  = filtered[filtered["Từ khóa"].isin(group_kws)].copy()

                if not group_data.empty and "Ngày_Sort" in group_data.columns:
                    daily_avg = (
                        group_data.groupby("Ngày_Sort")["Thứ hạng"]
                        .mean()
                        .reset_index()
                        .sort_values("Ngày_Sort")
                    )
                    daily_avg["Ngày_label"] = daily_avg["Ngày_Sort"].dt.strftime("%d/%m/%Y")

                    y_max  = daily_avg["Thứ hạng"].max()
                    y_ceil = max(y_max * 1.2, y_max + 20) if pd.notna(y_max) else 200

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_avg["Ngày_label"],
                        y=[y_ceil] * len(daily_avg),
                        mode="lines",
                        line=dict(width=0, shape="spline"),
                        showlegend=False,
                        hoverinfo="skip",
                    ))
                    fig.add_trace(go.Scatter(
                        x=daily_avg["Ngày_label"],
                        y=daily_avg["Thứ hạng"],
                        mode="lines+markers",
                        name=selected_group,
                        line=dict(color="#f87171", width=2.5, shape="spline", smoothing=1.3),
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
                        height=340,
                        hovermode="x unified",
                        margin=dict(l=8, r=8, t=8, b=8),
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Không có dữ liệu cho nhóm này.")

    with col_table:
        with st.container(border=True):
            if selected_group:
                group_kws    = keyword_groups[selected_group]
                group_detail = filtered[filtered["Từ khóa"].isin(group_kws)].copy()

                # Lấy bản ghi mới nhất mỗi từ khoá
                if "Ngày_Sort" in group_detail.columns:
                    group_detail = (
                        group_detail.sort_values("Ngày_Sort", ascending=False)
                        .drop_duplicates(subset=["Từ khóa"])
                        .sort_values("Từ khóa")
                        .reset_index(drop=True)
                    )

                group_detail.index = (group_detail.index + 1).map(lambda x: f"{x:02d}")

                cols_show = [c for c in ["Từ khóa", "Thứ hạng", "URL", "Ngày"] if c in group_detail.columns]
                display_df = group_detail[cols_show].copy()

                display_df["Thứ hạng"] = display_df["Thứ hạng"].apply(
                    lambda x: f"{x:.0f}" if pd.notna(x) else "None"
                )
                if "URL" in display_df.columns:
                    display_df["URL"] = display_df["URL"].apply(
                        lambda x: x if pd.notna(x) and x != "" else "None"
                    )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400,
                    hide_index=False,
                    column_config={
                        "Từ khóa": st.column_config.TextColumn("Từ khoá", width="medium"),
                        "Thứ hạng": st.column_config.TextColumn("Thứ hạng", width="small"),
                        "URL": st.column_config.TextColumn("URL", width="medium"),
                        "Ngày": st.column_config.TextColumn("Ngày", width="small"),
                    }
                )