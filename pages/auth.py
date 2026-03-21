import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from user_auth import login_user, register_user, logout, is_authenticated
# from sheets_config import SHEETS  # Removed
from config import setup_page_config
from persistence import save_session_state, clear_all_session_files, init_session_state

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
    
    if st.button("Đăng nhập", width='stretch'):
        success, user_config = login_user(username, password)
        if success:
            st.session_state.user_id = username  # Simple user_id as username
            st.session_state.display_name = user_config.get('display_name', username)
            st.session_state.user_sheets_config = user_config['sheets_config']
            save_session_state()  # Persist auth session
            init_session_state(restore_auth=True)  # Load full app state
            st.success("✅ Đăng nhập thành công!")
            st.switch_page("dashboard.py")
            st.rerun()
        else:
            st.error(f"❌ {user_config}")  # Error msg

with tab2:
    st.subheader("👤 Tạo tài khoản mới")
    new_display_name = st.text_input("Họ và tên", key="register_display_name")
    new_username = st.text_input("Tên đăng nhập", key="register_username")
    new_password = st.text_input("Mật khẩu", type="password", key="register_password")
    confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="register_confirm")
    
    num_domains = st.number_input("Số domain", min_value=1, max_value=10, value=1)
    
    sheets_config = []
    for i in range(int(num_domains)):
        with st.expander(f"Domain {i+1}"):
            domain = st.text_input(f"Tên domain", key=f"domain_{i}", placeholder="vd: example.com")
            sheet_id = st.text_input(f"Google Sheet ID", key=f"sheet_{i}", placeholder="1abc...xyz")
            worksheet = st.text_input(f"Tên worksheet", key=f"ws_{i}", value="Ngày_22_01_2026", placeholder="Ngày_DD_MM_YYYY")
            if domain and sheet_id:
                sheets_config.append({"domain": domain.strip(), "sheet_id": sheet_id.strip(), "worksheet": worksheet.strip()})
    
    if st.button("Đăng ký", width='stretch'):
        if new_password != confirm_password:
            st.error("❌ Mật khẩu không khớp")
        elif len(new_username) < 3:
            st.error("❌ Tên đăng nhập quá ngắn")
        elif len(new_display_name.strip()) < 2:
            st.error("❌ Họ và tên quá ngắn")
        elif not sheets_config:
            st.error("❌ Phải nhập ít nhất 1 domain đầy đủ")
        else:
            success, msg = register_user(new_username, new_password, new_display_name, sheets_config)
            if success:
                succ, user_config = login_user(new_username, new_password)
                if succ:
                    st.session_state.user_id = new_username
                    st.session_state.display_name = user_config.get('display_name', new_username)
                    st.session_state.user_sheets_config = user_config['sheets_config']
                    save_session_state()  # Persist auth session
                    init_session_state(restore_auth=True)  # Full app state
                    st.success(f"✅ Đăng ký và đăng nhập thành công, chào {st.session_state.display_name}!")
                    st.switch_page("dashboard.py")
                    st.rerun()
                else:
                    st.success(f"✅ {msg}")
                    st.info("👆 Bây giờ bạn có thể đăng nhập")
            else:
                st.error(f"❌ {msg}")

if is_authenticated():
    display = st.session_state.get('display_name', st.session_state.user_id)
    st.success(f"Đã đăng nhập: {display}")
    if st.button("🚪 Đăng xuất", width='stretch'):
        logout()
        clear_all_session_files()  # FIXED: Clear ALL session files
        st.rerun()

