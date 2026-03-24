import streamlit as st
import sys, os
import base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, logout, is_authenticated, update_user
from config import setup_page_config
from persistence import save_session_state, init_session_state

# Hide sidebar on profile page
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Restore session FIRST - F5 SAFE
from user_auth import validate_session
init_session_state(restore_auth=True)

# ✅ F5-safe: validate user + restore if valid
if 'user_id' in st.session_state:
    if not validate_session():
        st.session_state.avatar = None
        st.switch_page("pages/auth.py")
else:
    st.switch_page("pages/auth.py")

setup_page_config()

st.title("👤 Trang Cá nhân")
avatar_path = st.session_state.get('avatar_path')
# 🛡️ Defensive image load - prevents PIL crash
try:
    if avatar_path and os.path.exists(avatar_path):
        st.image(avatar_path, width=120)
    else:
        raise ValueError("No valid avatar")
except Exception:
    initials = st.session_state.get('display_name', st.session_state.user_id or '')[0].upper()
    st.markdown(f"""
        <div style='width:120px;height:120px;border-radius:50%;background:#3b82f6;display:flex;align-items:center;justify-content:center;color:white;font-weight:600;font-size:36px;'>
            {initials}
        </div>
    """, unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("⬅️ Quay lại"):
        st.switch_page("dashboard.py")
with col2:
    st.empty()

display_name = st.session_state.get('display_name', st.session_state.user_id)
user_id = st.session_state.user_id

tab1, tab2 = st.tabs(["📝 Thông tin cá nhân", "🌐 Quản lý Domain"])

with tab1:
    st.subheader("Họ và tên")
    new_display_name = st.text_input(
        "Họ và tên mới",
        value=display_name,
        help="Nhập họ và tên mới (tối thiểu 2 ký tự)"
    )

    st.divider()

    # ================= AVATAR =================
    st.subheader("Ảnh đại diện")

    avatar_file = st.file_uploader(
        "Tải lên avatar",
        type=["png", "jpg", "jpeg"],
        key="avatar_upload"
    )

    # if avatar_file is not None:
    #     st.image(avatar_file, width=120, caption="Preview avatar mới")
    if avatar_file is not None:
        os.makedirs("avatars", exist_ok=True)

        avatar_path = f"avatars/{user_id}.png"

        with open(avatar_path, "wb") as f:
            f.write(avatar_file.read())

    st.divider()

    # ================= PASSWORD =================
    st.subheader("🔑 Đổi mật khẩu")

    old_password = st.text_input("Mật khẩu cũ", type="password")
    new_password = st.text_input("Mật khẩu mới", type="password")
    confirm_password = st.text_input("Xác nhận mật khẩu mới", type="password")

with tab2:
    st.subheader("Quản lý Google Sheets Domain")
    user_sheets_config = st.session_state.get('user_sheets_config', [])

    # Dynamic domain management
    num_domains = st.number_input("Số domain", min_value=1, max_value=10, value=max(1, len(user_sheets_config)))

    new_sheets_config = []
    for i in range(int(num_domains)):
        with st.expander(f"Domain {i+1}"):
            domain = st.text_input(f"Tên domain", value=user_sheets_config[i]['domain'] if i < len(user_sheets_config) else '', key=f"prof_domain_{i}")
            sheet_id = st.text_input(f"Google Sheet ID", value=user_sheets_config[i].get('sheet_id', '') if i < len(user_sheets_config) else '', key=f"prof_sheet_{i}")
            worksheet = st.text_input(f"Tên worksheet", value=user_sheets_config[i].get('worksheet', 'Ngày_22_01_2026') if i < len(user_sheets_config) else 'Ngày_22_01_2026', key=f"prof_ws_{i}")
            if domain.strip() and sheet_id:
                new_sheets_config.append({
                    "domain": domain.strip(),
                    "sheet_id": sheet_id.strip(),
                    "worksheet": worksheet.strip()
                })


# Save buttons
col1, col2 = st.columns([3,1])
with col1:
    if st.button("💾 Cập nhật thông tin", width='stretch', type="primary"):

        success, msg = update_user(
            user_id,
            new_display_name,
            new_sheets_config,
            avatar=avatar_path   # 👈 truyền path, KHÔNG phải file
        )
        if success and avatar_file:
            st.session_state.avatar_path = f"avatars/{user_id}.png"

        if success:
            st.session_state.display_name = new_display_name
            st.session_state.user_sheets_config = new_sheets_config
            # Avatar auto-handled by user_auth.update_user()
            save_session_state()
            st.success(f"✅ {msg}!")
            st.switch_page("dashboard.py")
        else:
            st.error(f"❌ {msg}")

with col2:
    if st.button("🔑 Chỉ đổi mật khẩu", width='stretch'):
        if new_password != confirm_password:
            st.error("❌ Mật khẩu xác nhận không khớp")
        elif len(new_password) < 6:
            st.error("❌ Mật khẩu quá ngắn (tối thiểu 6 ký tự)")
        else:
            success, msg = update_user(user_id, display_name, user_sheets_config, old_password, new_password)
            if success:
                st.success(f"✅ {msg}!")
            else:
                st.error(f"❌ {msg}")

# Logout
if st.button("🚪 Đăng xuất", width='stretch'):
    logout()
    st.rerun()

