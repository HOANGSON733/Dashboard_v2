import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, register_user, logout, is_authenticated
from sheets_config import SHEETS
from config import setup_page_config
from persistence import save_session_state

# Hide sidebar on auth page
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

setup_page_config()

st.title("🔐 Đăng nhập / Đăng ký")

tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

with tab1:
    st.subheader("📝 Thông tin đăng nhập")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập", use_container_width=True):
        success, domains = login_user(username, password)
        if success:
            st.session_state.user_id = username  # Simple user_id as username
            st.session_state.user_domains = domains
            save_session_state()  # Persist auth session
            st.success("✅ Đăng nhập thành công!")
            st.switch_page("dashboard.py")
        else:
            st.error(f"❌ {domains}")  # Error msg

with tab2:
    st.subheader("👤 Tạo tài khoản mới")
    new_username = st.text_input("Tên đăng nhập", key="register_username")
    new_password = st.text_input("Mật khẩu", type="password", key="register_password")
    confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="register_confirm")
    
    domains_list = list(SHEETS.keys())
    selected_domains = st.multiselect(
        "Chọn domain được phép truy cập", 
        options=domains_list, 
        default=[], 
        help="Người dùng có thể chọn nhiều domain"
    )
    
    if st.button("Đăng ký", use_container_width=True):
        if new_password != confirm_password:
            st.error("❌ Mật khẩu không khớp")
        elif not selected_domains:
            st.error("❌ Phải chọn ít nhất 1 domain")
        elif len(new_username) < 3:
            st.error("❌ Tên đăng nhập quá ngắn")
        else:
            success, msg = register_user(new_username, new_password, selected_domains)
            if success:
                succ, domains = login_user(new_username, new_password)
                if succ:
                    st.session_state.user_id = new_username
                    st.session_state.user_domains = domains
                    save_session_state()  # Persist auth session
                    st.success("✅ Đăng ký và đăng nhập thành công!")
                    st.switch_page("dashboard.py")
                else:
                    st.success(f"✅ {msg}")
                    st.info("👆 Bây giờ bạn có thể đăng nhập")
            else:
                st.error(f"❌ {msg}")

if is_authenticated():
    st.success(f"Đã đăng nhập: {st.session_state.user_id}")
    if st.button("🚪 Đăng xuất", use_container_width=True):
        logout()
        # Clear session file on logout
        try:
            user_id = st.session_state.get('user_id', 'default')
            session_file = f"dashboard_session_{user_id}.json"
            if os.path.exists(session_file):
                os.remove(session_file)
            default_file = "dashboard_session_default.json"
            if os.path.exists(default_file):
                os.remove(default_file)
        except:
            pass
        st.rerun()

