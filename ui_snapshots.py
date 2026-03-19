"""
UI: Snapshots - Quản lý snapshot dữ liệu
Clone UI theo ảnh: card grid 3 cột, bảng xem, so sánh 2 cột
"""

import streamlit as st
import pandas as pd
from persistence import save_session_state


# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
SNAP_CSS = """
<style>
/* ══ PAGE TITLE ══ */
.sp-page-title {
    font-size: 16px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
}
.sp-page-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 20px 0;
}

/* ══ SECTION LABEL ══ */
.sp-section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 16px;
}

/* ══ SNAPSHOT CARD ══ */
.sp-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px 18px 14px 18px;
    background: #fff;
    margin-bottom: 4px;
}
.sp-card-title {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    margin: 0 0 4px 0;
}
.sp-card-date {
    font-size: 12px;
    color: #6b7280;
    margin: 0 0 14px 0;
}
.sp-card-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.sp-card-score {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}
.sp-card-note {
    font-size: 12px;
    color: #9ca3af;
}

/* ══ CARD BUTTONS ══ */
/* Xem — blue filled (active) / outline (inactive) */
div[data-testid="stButton"] button.sp-btn-view-active {
    background: #2563eb !important;
    color: #fff !important;
    border: 1px solid #2563eb !important;
}
/* Generic outline button reset */
div[data-testid="stButton"] > button[kind="secondary"] {
    border-radius: 6px !important;
    font-size: 13px !important;
    height: 32px !important;
    min-height: unset !important;
    padding: 0 10px !important;
    transition: all 0.15s !important;
}

/* ══ VIEWING BANNER ══ */
.sp-viewing-banner {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #374151;
    font-weight: 500;
    margin: 20px 0 10px 0;
}

/* ══ TABLE ══ */
.sp-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
}
.sp-table thead tr {
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
}
.sp-table thead th {
    padding: 10px 16px;
    text-align: left;
    font-weight: 500;
    color: #6b7280;
    font-size: 12.5px;
    white-space: nowrap;
}
.sp-table tbody tr {
    border-bottom: 1px solid #f3f4f6;
    transition: background 0.12s;
}
.sp-table tbody tr:last-child { border-bottom: none; }
.sp-table tbody tr:hover { background: #fafafa; }
.sp-table td {
    padding: 10px 16px;
    color: #374151;
    vertical-align: middle;
}
.sp-table td.link a {
    color: #2563eb;
    text-decoration: none;
    font-size: 12.5px;
}
.sp-table td.kw { color: #2563eb; }
.sp-table td.stt { color: #9ca3af; }
.sp-table td.none-val { color: #9ca3af; }

/* ══ SO SÁNH SECTION ══ */
.sp-compare-title {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
    margin: 32px 0 4px 0;
}
.sp-compare-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0 0 20px 0;
}

/* ── Compare left panel ── */
.sp-compare-panel {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px 18px;
    background: #fff;
}
.sp-compare-field-label {
    font-size: 12.5px;
    color: #374151;
    font-weight: 500;
    margin: 0 0 6px 0;
}
.sp-compare-add-btn {
    width: 100%;
    border: 1px dashed #d1d5db !important;
    background: transparent !important;
    color: #9ca3af !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    height: 36px !important;
    min-height: unset !important;
    margin: 10px 0 !important;
    transition: all 0.15s !important;
}
.sp-compare-add-btn:hover {
    border-color: #2563eb !important;
    color: #2563eb !important;
}

/* ── Metric cards kết quả so sánh ── */
.sp-result-panel {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px 18px;
    background: #fff;
}
.sp-result-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #2563eb;
    margin-bottom: 16px;
}
.sp-result-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
.sp-result-card {
    background: #eff6ff;
    border-radius: 8px;
    padding: 14px 16px;
}
.sp-result-card-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #374151;
    font-weight: 500;
    margin-bottom: 8px;
}
.sp-result-card-value {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
    line-height: 1;
}

/* ── Fix: gap between result title div and cards below ── */
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] + div[data-testid="stHorizontalBlock"] {
    margin-top: 12px !important;
}
</style>
"""


# ─────────────────────────────────────────
# HELPER: render 1 snapshot card
# ─────────────────────────────────────────
def _snap_card(snap_name, snap_data, is_viewing):
    date_str = snap_data["date"].strftime("%d/%m/%Y %H:%M")
    score    = snap_data["score"]
    note     = snap_data.get("note", "") or "Chưa có ghi chú"

    st.markdown(f"""
    <div class="sp-card">
        <p class="sp-card-title">{snap_name}</p>
        <p class="sp-card-date">{date_str}</p>
        <div class="sp-card-row">
            <span class="sp-card-score">Score: {score}/100</span>
            <span class="sp-card-note">{note}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3 = st.columns(3)

    with b1:
        label = "Xem" if not is_viewing else "Xem"
        btn_type = "primary" if is_viewing else "secondary"
        if st.button(label, key=f"view_{snap_name}", use_container_width=True, type=btn_type):
            if is_viewing:
                del st.session_state.selected_snapshot
            else:
                st.session_state.selected_snapshot = snap_name
            st.rerun()

    with b2:
        if st.button("Nhập ghi chú", key=f"save_{snap_name}", use_container_width=True):
            # Mở input ghi chú qua session state
            st.session_state[f"editing_note_{snap_name}"] = True
            st.rerun()

    with b3:
        if st.button("Xoá", key=f"del_{snap_name}", use_container_width=True):
            del st.session_state.snapshots[snap_name]
            if st.session_state.get("selected_snapshot") == snap_name:
                del st.session_state.selected_snapshot
            save_session_state()
            st.rerun()

    # Inline note editor
    if st.session_state.get(f"editing_note_{snap_name}"):
        new_note = st.text_input(
            "Ghi chú", value=snap_data.get("note", ""),
            key=f"note_input_{snap_name}",
        )
        if st.button("✅ Lưu ghi chú", key=f"confirm_note_{snap_name}"):
            st.session_state.snapshots[snap_name]["note"] = new_note
            del st.session_state[f"editing_note_{snap_name}"]
            save_session_state()
            st.rerun()


# ─────────────────────────────────────────
# MAIN RENDER
# ─────────────────────────────────────────
def render_snapshots():
    st.markdown(SNAP_CSS, unsafe_allow_html=True)

    # ── Page title ──
    st.markdown('<p class="sp-page-title">Quản lý Snapshots</p>', unsafe_allow_html=True)
    st.markdown('<hr class="sp-page-divider">', unsafe_allow_html=True)

    snapshots = st.session_state.get("snapshots", {})

    # ══════════════════════════════════════
    # PHẦN 1: DANH SÁCH SNAPSHOTS
    # ══════════════════════════════════════
    st.markdown('<div class="sp-section-label">🗂️ Danh sách Snapshots</div>', unsafe_allow_html=True)

    if not snapshots:
        st.info("📝 Chưa có snapshot nào. Tạo snapshot ở trang Tổng quan!")
    else:
        snap_names = list(snapshots.keys())
        selected   = st.session_state.get("selected_snapshot")

        # Grid 3 cột
        for i in range(0, len(snap_names), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(snap_names):
                    name = snap_names[i + j]
                    with col:
                        _snap_card(name, snapshots[name], is_viewing=(selected == name))

        # ── VIEWING TABLE ──
        # if selected and selected in snapshots:
        #     snap_data = snapshots[selected]

        #     st.markdown(
        #         f'<div class="sp-viewing-banner">👁️ Đang xem {selected}</div>',
        #         unsafe_allow_html=True,
        #     )

        #     df = snap_data["data"].drop(columns=["Ngày_Sort"], errors="ignore").copy()

        #     # Render bảng HTML để style đúng
        #     cols_show = ["Từ khóa", "Trang", "Thứ hạng", "Vị trí", "URL"]
        #     cols_show = [c for c in cols_show if c in df.columns]

        #     rows_html = ""
        #     for idx, row in df[cols_show].head(50).iterrows():
        #         cells = ""
        #         for c in cols_show:
        #             val = row[c]
        #             val_str = str(val) if pd.notna(val) else "None"
        #             if c == "Từ khóa":
        #                 cells += f'<td class="kw">{val_str}</td>'
        #             elif c == "URL" and val_str.startswith("http"):
        #                 short = val_str[:40] + "…" if len(val_str) > 40 else val_str
        #                 cells += f'<td class="link"><a href="{val_str}" target="_blank">{short}</a></td>'
        #             elif val_str == "None":
        #                 cells += f'<td class="none-val">None</td>'
        #             else:
        #                 cells += f'<td>{val_str}</td>'

        #         rows_html += f"<tr><td class='stt'>{idx+1:02d}</td>{cells}</tr>"

        #     header_html = "<th>STT</th>" + "".join(f"<th>{c}</th>" for c in cols_show)

        #     st.markdown(f"""
        #     <table class="sp-table">
        #         <thead><tr>{header_html}</tr></thead>
        #         <tbody>{rows_html}</tbody>
        #     </table>
        #     """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # PHẦN 2: SO SÁNH SNAPSHOTS
    # ══════════════════════════════════════
    st.markdown('<p class="sp-compare-title">So sánh Snapshots</p>', unsafe_allow_html=True)
    st.markdown('<hr class="sp-compare-divider">', unsafe_allow_html=True)

    if len(snapshots) < 2:
        st.info("Cần ít nhất 2 snapshots để so sánh.")
        return

    snap_names = list(snapshots.keys())

    col_left, col_right = st.columns([1, 1.4], gap="large")

    with col_left:
        st.markdown('<p class="sp-compare-field-label">Chọn Snapshot 1</p>', unsafe_allow_html=True)
        snap1 = st.selectbox("", snap_names, key="cmp_snap1", label_visibility="collapsed")

        st.markdown('<p class="sp-compare-field-label" style="margin-top:12px">Chọn Snapshot 2</p>', unsafe_allow_html=True)
        snap2 = st.selectbox("", snap_names, index=min(1, len(snap_names)-1), key="cmp_snap2", label_visibility="collapsed")

        st.button("➕ Thêm Snapshot", use_container_width=True, disabled=True)

        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
        compare_clicked = st.button("🔄 So sánh", use_container_width=True, type="primary")

    with col_right:
        if compare_clicked or st.session_state.get("cmp_result"):
            if compare_clicked:
                d1 = snapshots[snap1]["data"]
                d2 = snapshots[snap2]["data"]

                score_diff = round(snapshots[snap1]["score"] - snapshots[snap2]["score"], 1)

                kw1 = set(d1["Từ khóa"].tolist()) if "Từ khóa" in d1.columns else set()
                kw2 = set(d2["Từ khóa"].tolist()) if "Từ khóa" in d2.columns else set()

                lost_kw  = len(kw1 - kw2)
                new_kw   = len(kw2 - kw1)
                total_kw = len(kw2)

                st.session_state.cmp_result = {
                    "score_diff": score_diff,
                    "lost_kw":    lost_kw,
                    "new_kw":     new_kw,
                    "total_kw":   total_kw,
                }

            r = st.session_state.cmp_result

            st.markdown("""
            <div style="border:1px solid #e5e7eb;border-radius:10px;padding:20px 18px;background:#fff">
                <div style="display:flex;align-items:center;gap:8px;font-size:14px;font-weight:600;
                            color:#2563eb;margin-bottom:20px;padding-bottom:14px;
                            border-bottom:1px solid #f0f0f0">
                    🗂️ Phân tích so sánh Snapshots
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 4 metric cards 2x2
            m1, m2 = st.columns(2, gap="small")
            m3, m4 = st.columns(2, gap="small")

            for col, icon, label, val in [
                (m1, "↕️", "Score",        r["score_diff"]),
                (m2, "🔍", "Từ khoá mất",  r["lost_kw"]),
                (m3, "🔍", "Từ khoá mới",  r["new_kw"]),
                (m4, "🔍", "Số từ khoá",   r["total_kw"]),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="sp-result-card" style="margin-bottom:10px">
                        <div class="sp-result-card-label">{icon} {label}</div>
                        <div class="sp-result-card-value">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:100%;display:flex;align-items:center;justify-content:center;
                        border:1px dashed #e5e7eb;border-radius:10px;padding:40px;
                        color:#9ca3af;font-size:13px;text-align:center">
                Chọn 2 snapshots và nhấn <b>So sánh</b> để xem kết quả
            </div>
            """, unsafe_allow_html=True)
            # ── VIEWING TABLE (đặt cuối, sau So sánh) ──
    if snapshots and st.session_state.get("selected_snapshot"):
        selected  = st.session_state.selected_snapshot
        if selected in snapshots:
            snap_data = snapshots[selected]

            st.markdown(
                f'<div class="sp-viewing-banner">👁️ Đang xem {selected}</div>',
                unsafe_allow_html=True,
            )

            df = snap_data["data"].drop(columns=["Ngày_Sort"], errors="ignore").copy()

            cols_show = ["Từ khóa", "Trang", "Thứ hạng", "Vị trí", "URL"]
            cols_show = [c for c in cols_show if c in df.columns]

            rows_html = ""
            for idx, row in df[cols_show].head(50).iterrows():
                cells = ""
                for c in cols_show:
                    val = row[c]
                    val_str = str(val) if pd.notna(val) else "None"
                    if c == "Từ khóa":
                        cells += f'<td class="kw">{val_str}</td>'
                    elif c == "URL" and val_str.startswith("http"):
                        short = val_str[:40] + "…" if len(val_str) > 40 else val_str
                        cells += f'<td class="link"><a href="{val_str}" target="_blank">{short}</a></td>'
                    elif val_str == "None":
                        cells += f'<td class="none-val">None</td>'
                    else:
                        cells += f'<td>{val_str}</td>'
                rows_html += f"<tr><td class='stt'>{idx+1:02d}</td>{cells}</tr>"

            header_html = "<th>STT</th>" + "".join(f"<th>{c}</th>" for c in cols_show)

            st.markdown(f"""
            <table class="sp-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)