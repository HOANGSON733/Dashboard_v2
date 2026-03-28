import streamlit as st
import pandas as pd
from datetime import datetime, date
from persistence import save_session_state


# ───────────────── MODAL THÊM MỤC TIÊU ─────────────────
@st.dialog("Quản lý mục tiêu", width="large")
def _modal_them_muctieu(all_keywords):

    st.markdown("### Tạo mục tiêu mới")

    goal_keyword = st.selectbox("Tên mục tiêu", all_keywords)
    goal_target = st.number_input("Mục tiêu thứ hạng", min_value=1, max_value=200)
    goal_deadline = st.date_input("Thời hạn")

    if st.button("💾 Lưu mục tiêu", use_container_width=True):
        if goal_keyword and goal_target and goal_deadline:
            goal_id = f"{goal_keyword}_{datetime.now().timestamp()}"

            st.session_state.goals[goal_id] = {
                "keyword": goal_keyword,
                "target": int(goal_target),
                "deadline": goal_deadline,
                "created": datetime.now(),
            }

            save_session_state()
            st.success("✅ Đã thêm mục tiêu!")
            st.rerun()
        else:
            st.warning("Vui lòng nhập đầy đủ thông tin")


# ───────────────── MAIN UI ─────────────────
def render_muctieu(filtered):

    if "goals" not in st.session_state:
        st.session_state.goals = {}

    goals = st.session_state.goals

    # ── HEADER ──
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 🎯 Danh sách mục tiêu")

    with col2:
        if st.button("➕ Tạo mục tiêu", use_container_width=True):
            all_keywords = filtered["Từ khóa"].unique().tolist()
            _modal_them_muctieu(all_keywords)

    st.divider()

    # ── STATS ──
    total = len(goals)
    achieved = 0
    overdue = 0
    in_progress = 0

    def safe_date_subtract(deadline_obj):
        today = datetime.now().date()
        if isinstance(deadline_obj, str):
            try:
                dl_str = deadline_obj.replace(' ', 'T')
                dl_date = datetime.fromisoformat(dl_str).date()
            except Exception:
                return 999  # Treat invalid as future
        elif isinstance(deadline_obj, date):
            dl_date = deadline_obj
        elif hasattr(deadline_obj, 'date'):
            dl_date = deadline_obj.date()
        else:
            return 999
        return (dl_date - today).days

    for goal in goals.values():
        kw_data = filtered[filtered["Từ khóa"] == goal["keyword"]]

        if not kw_data.empty:
            latest_rank = kw_data.sort_values("Ngày_Sort").iloc[-1]["Thứ hạng"]

            if pd.notna(latest_rank) and latest_rank <= goal["target"]:
                achieved += 1
            elif safe_date_subtract(goal["deadline"]) < 0:
                overdue += 1
            else:
                in_progress += 1

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tổng", total)
    c2.metric("Đã đạt", achieved)
    c3.metric("Đang theo dõi", in_progress)
    c4.metric("Quá hạn", overdue)

    st.divider()

    # ── EMPTY ──
    if not goals:
        st.info("Chưa có mục tiêu nào")
        return

    # ── CSS ──
    st.markdown("""
    <style>
    .row {
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }
    .row:hover {
        background: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER TABLE ──
    h1, h2, h3, h4, h5, h6 = st.columns([1, 3, 2, 2, 4, 1])
    h1.markdown("**STT**")
    h2.markdown("**Tên mục tiêu**")
    h3.markdown("**Mục tiêu**")
    h4.markdown("**Thời hạn**")
    h5.markdown("**URL**")
    h6.markdown("")

    st.markdown("---")

    # ── ROWS ──
    goal_ids = list(goals.keys())

    for i, goal_id in enumerate(goal_ids):
        goal = goals[goal_id]

        kw_data = filtered[filtered["Từ khóa"] == goal["keyword"]]

        url = ""
        if not kw_data.empty:
            latest = kw_data.sort_values("Ngày_Sort").iloc[-1]
            url = latest.get("URL", "") if pd.notna(latest.get("URL", "")) else ""

        c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 4, 1])

        with c1:
            st.write(f"{i+1:02d}")

        with c2:
            st.write(goal["keyword"])

        with c3:
            st.write(goal["target"])

        with c4:
            deadline = goal["deadline"]
            if hasattr(deadline, "strftime"):
                deadline = deadline.strftime("%d/%m/%Y")
            st.write(deadline)

        with c5:
            if url:
                st.link_button("🔗 Link", url)

        # ── MENU 3 CHẤM ──
        with c6:
            with st.popover("⋯"):

                if st.button("✏️ Chỉnh sửa", key=f"edit_{goal_id}"):
                    st.info("Chưa làm edit")

                if st.button("🗑️ Xóa mục tiêu", key=f"del_{goal_id}"):
                    del st.session_state.goals[goal_id]
                    save_session_state()
                    st.rerun()