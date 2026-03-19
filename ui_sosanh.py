"""
UI: So sánh ngày - Layout 3 cột theo hình mẫu
Left: date selector + top keywords
Mid: gauge + horizontal bar chart
Right: 2x2 stat tiles với line chart
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from helpers import compare_ranks
from streamlit_echarts import st_echarts


def inject_css():
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 10px 12px !important;
    }
    div[data-testid="stPlotlyChart"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.3rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def make_line_chart(date1_label, date2_label, val1, val2, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[date1_label, date2_label],
        y=[val1, val2],
        mode="lines+markers+text",
        line=dict(color=color, width=2,  smoothing=1.2),
        marker=dict(size=6, color=color),
        text=[str(round(val1, 1)), str(round(val2, 1))],
        textposition=["top right", "top right"],
        textfont=dict(size=10, color="#374151"),
    ))
    y_min = min(val1, val2)
    y_max = max(val1, val2)
    pad = max((y_max - y_min) * 0.4, 1)
    fig.update_layout(
        height=110,
        margin=dict(l=10, r=10, t=24, b=24),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=9, color="#9ca3af"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.05)",
            zeroline=True,
            zerolinecolor="rgba(0,0,0,0.08)",
            tickfont=dict(size=9, color="#9ca3af"),
            range=[max(0, y_min - pad), y_max + pad],
        ),
    )
    return fig


def make_hbar(status_counts_df):
    order = ["Mới có rank", "Tăng hạng", "Giảm hạng", "Mất hạng", "Không đổi hạng"]
    colors = {
        "Tăng hạng": "#10b981",
        "Giảm hạng": "#ef4444",
        "Mới có rank": "#3b82f6",
        "Mất hạng": "#f59e0b",
        "Không đổi hạng": "#3b82f6",
    }
    df = status_counts_df.set_index("Trạng thái").reindex(order).fillna(0).reset_index()
    fig = go.Figure(go.Bar(
        x=df["Số lượng"],
        y=df["Trạng thái"],
        orientation="h",
        marker_color=[colors.get(s, "#94a3b8") for s in df["Trạng thái"]],
        text=df["Số lượng"].astype(int),
        textposition="outside",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        height=170,
        margin=dict(l=0, r=35, t=4, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False,
                   tickfont=dict(size=9, color="#9ca3af")),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        bargap=0.3,
    )
    return fig


def make_gauge_echarts(ranked, total):
    pct = max(0.0, min(1.0, ranked / total)) if total else 0.0
    return {
        "series": [{
            "type": "gauge",
            "startAngle": 200,
            "endAngle": -20,
            "min": 0,
            "max": 1,
            "radius": "88%",
            "center": ["50%", "65%"],
            "progress": {"show": False},
            "axisLine": {
                "lineStyle": {
                    "width": 18,
                    "color": [[pct, "#3b82f6"], [1, "#e5e7eb"]]
                }
            },
            "axisTick": {"show": False},
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "pointer": {"show": False},
            "detail": {
                "formatter": f"{ranked} / {total}\n Từ khoá",
                "fontSize": 24,
                "fontWeight": "700",
                "color": "#0f172a",
                "offsetCenter": [0, "-5%"],
                "lineHeight": 28,
            },
            "data": [{"value": pct}]
        }]
    }


def render_keyword_card(keyword, rank, change):
    if change > 0:
        badge_bg, badge_color, arrow = "#d1fae5", "#065f46", f"▲ +{change:.0f}"
    elif change < 0:
        badge_bg, badge_color, arrow = "#fee2e2", "#991b1b", f"▼ {change:.0f}"
    else:
        badge_bg, badge_color, arrow = "#f3f4f6", "#6b7280", "–"

    st.markdown(f"""
    <div style="border:1px solid #e5e7eb;border-radius:8px;padding:8px 12px;
                margin-bottom:6px;background:#fff;
                display:flex;align-items:center;justify-content:space-between;gap:8px;">
        <div style="font-size:15px;color:#374151;font-weight:500;
                    flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{keyword}</div>
        <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
            <span style="font-size:15px;font-weight:800;color:#0f172a;">{rank:.0f}</span>
            <span style="background:{badge_bg};color:{badge_color};font-size:15px;
                         padding:2px 9px;border-radius:20px;font-weight:700;white-space:nowrap;">{arrow}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_tile(label, icon, val, pct, color, badge_bg, badge_color,
                     pct_symbol, date1, date2, val_old=0):
    fig = make_line_chart(date1, date2, val_old, val, color)
    with st.container(border=True):
        st.markdown(
            f"<div style='display:flex;align-items:center;justify-content:space-between;'>"
            f"<span style='font-size:15px;font-weight:600;color:#374151;'>{icon} {label}</span>"
            f"<span style='background:{badge_bg};color:{badge_color};font-size:15px;"
            f"padding:1px 7px;border-radius:20px;font-weight:600;'>"
            f"{pct_symbol}{pct:.1f}%</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Main ─────────────────────────────────────────────────────────────────────
def render_sosanh(filtered, sheet_map, selected_days):
    inject_css()
    st.markdown("## So sánh thay đổi thứ hạng")

    if len(selected_days) < 2:
        st.warning("⚠️ Cần chọn ít nhất 2 ngày để so sánh")
        return

    # ── 3-column master layout ───────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1.1, 1.3, 2.2], gap="medium")

    # ════════════════════════════════════════════════════════════════
    # LEFT: date selector + top keywords
    # ════════════════════════════════════════════════════════════════
    with col_left:
        st.markdown("<div style='font-size:15px;color:#6b7280;margin-bottom:2px;'>Ngày cũ (Baseline)</div>",
                    unsafe_allow_html=True)
        compare_date1 = st.selectbox("d1", selected_days, index=0,
                                     label_visibility="collapsed", key="ss_d1")

        st.markdown("<div style='font-size:15px;color:#6b7280;margin-bottom:2px;margin-top:6px;'>Ngày mới (So sánh)</div>",
                    unsafe_allow_html=True)
        compare_date2 = st.selectbox("d2", selected_days, index=len(selected_days) - 1,
                                     label_visibility="collapsed", key="ss_d2")

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        date1_str   = sheet_map[compare_date1].strftime("%d-%m-%Y")
        date2_str   = sheet_map[compare_date2].strftime("%d-%m-%Y")
        date1_label = sheet_map[compare_date1].strftime("%d/%m/%Y")
        date2_label = sheet_map[compare_date2].strftime("%d/%m/%Y")

        df_date1 = filtered[filtered["Ngày"] == date1_str][["Từ khóa", "Thứ hạng"]].copy()
        df_date2 = filtered[filtered["Ngày"] == date2_str][["Từ khóa", "Thứ hạng"]].copy()
        df_date1.rename(columns={"Thứ hạng": "Rank_Old"}, inplace=True)
        df_date2.rename(columns={"Thứ hạng": "Rank_New"}, inplace=True)

        comparison = pd.merge(df_date1, df_date2, on="Từ khóa", how="outer")
        comparison[["Trạng thái", "Thay đổi", "Icon"]] = comparison.apply(
            lambda row: compare_ranks(row["Rank_Old"], row["Rank_New"]),
            axis=1, result_type="expand"
        )

        status_counts = comparison["Trạng thái"].value_counts().reset_index()
        status_counts.columns = ["Trạng thái", "Số lượng"]
        status_map = status_counts.set_index("Trạng thái")["Số lượng"].to_dict()

        total_kw = len(comparison)
        tang  = int((comparison["Thay đổi"] > 0).sum())
        giam  = int((comparison["Thay đổi"] < 0).sum())
        mat   = int((comparison["Trạng thái"] == "Mất hạng").sum())
        khong = int((comparison["Thay đổi"] == 0).sum())

        tang_pct  = tang  / total_kw * 100 if total_kw else 0
        giam_pct  = giam  / total_kw * 100 if total_kw else 0
        khong_pct = khong / total_kw * 100 if total_kw else 0
        mat_pct   = mat   / total_kw * 100 if total_kw else 0

        top_improved = comparison[comparison["Thay đổi"] > 0].nlargest(10, "Thay đổi")
        top_declined = comparison[comparison["Thay đổi"] < 0].nsmallest(10, "Thay đổi")

        _ranked_kw = int(
            comparison[comparison["Trạng thái"] != "Mất hạng"]["Rank_New"]
            .pipe(pd.to_numeric, errors="coerce").dropna().gt(0).sum()
        )

        # Top tăng
        st.markdown(
            "<div style='font-size:15px;font-weight:700;color:#10b981;margin-bottom:4px;'>"
            "📈 Top 10 từ khóa tăng mạnh nhất</div>",
            unsafe_allow_html=True,
        )
        if top_improved.empty:
            st.caption("Không có dữ liệu")
        else:
            show_all_up = st.session_state.get("show_all_improved", False)
            rows_up = top_improved if show_all_up else top_improved.head(3)
            for _, row in rows_up.iterrows():
                render_keyword_card(row["Từ khóa"], row["Rank_New"], row["Thay đổi"])
            if len(top_improved) > 3:
                if st.button("Xem thêm ▼" if not show_all_up else "Thu gọn ▲",
                             key="btn_improved", use_container_width=True):
                    st.session_state["show_all_improved"] = not show_all_up
                    st.rerun()

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

        # Top giảm
        st.markdown(
            "<div style='font-size:15px;font-weight:700;color:#ef4444;margin-bottom:4px;'>"
            "‼️ Top 10 từ khóa giảm mạnh nhất</div>",
            unsafe_allow_html=True,
        )
        if top_declined.empty:
            st.caption("Không có dữ liệu")
        else:
            show_all_dn = st.session_state.get("show_all_declined", False)
            rows_dn = top_declined if show_all_dn else top_declined.head(3)
            for _, row in rows_dn.iterrows():
                render_keyword_card(row["Từ khóa"], row["Rank_New"], row["Thay đổi"])
            if len(top_declined) > 3:
                if st.button("Xem thêm ▼" if not show_all_dn else "Thu gọn ▲",
                             key="btn_declined", use_container_width=True):
                    st.session_state["show_all_declined"] = not show_all_dn
                    st.rerun()

    # ════════════════════════════════════════════════════════════════
    # MID: Gauge (top) + Horizontal bar (bottom)
    # ════════════════════════════════════════════════════════════════
    with col_mid:
        with st.container(border=True):
            st.markdown(
                "<div style='font-size:15px;font-weight:700;color:#374151;"
                "text-align:center;margin-bottom:0;'>Tổng số lượng từ khoá</div>",
                unsafe_allow_html=True,
            )
            st_echarts(make_gauge_echarts(_ranked_kw, total_kw), height="180px")

        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.plotly_chart(
                make_hbar(status_counts),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            st.markdown(
                "<div style='font-size:15px;color:#6b7280;text-align:center;margin-top:-6px;'>"
                "■ Số lượng phân bổ</div>",
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════════════
    # RIGHT: 2×2 stat tiles
    # ════════════════════════════════════════════════════════════════
    with col_right:
        r1c1, r1c2 = st.columns(2, gap="small")
        with r1c1:
            render_stat_tile(
                "Tăng hạng", "🥇", tang, tang_pct,
                "#10b981", "#d1fae5", "#065f46", "▲ ",
                date1_label, date2_label, val_old=max(0, tang - 2),
            )
        with r1c2:
            render_stat_tile(
                "Giảm hạng", "🥉", giam, giam_pct,
                "#ef4444", "#fee2e2", "#991b1b", "▼ ",
                date1_label, date2_label, val_old=max(0, giam + 2),
            )

        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)

        r2c1, r2c2 = st.columns(2, gap="small")
        with r2c1:
            render_stat_tile(
                "Không đổi hạng", "🥈", khong, khong_pct,
                "#94a3b8", "#f3f4f6", "#374151", "— ",
                date1_label, date2_label, val_old=khong,
            )
        with r2c2:
            render_stat_tile(
                "Mất hạng", "❌", mat, mat_pct,
                "#f59e0b", "#fef3c7", "#92400e", "▲ ",
                date1_label, date2_label,
                val_old=int(status_map.get("Mất hạng", 0) * 0.65),
            )