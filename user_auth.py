# user_auth.py - handles user registration, login, logout, and profile updates with MongoDB
import streamlit as st
from db import UserManager, SessionsManager

def load_users():
    """Load users from MongoDB"""
    return UserManager().list_users()



def register_user(username, password, display_name, sheets_config):
    """
    Register new user with full profile.
    """

    # Validate display_name
    if len(display_name.strip()) < 2:
        return False, "Họ và tên quá ngắn"

    # Validate sheets_config
    if not sheets_config or len(sheets_config) == 0:
        return False, "Phải có ít nhất 1 domain"

    for config in sheets_config:
        if not all(k in config for k in ['domain', 'sheet_id', 'worksheet']):
            return False, "Mỗi domain phải có domain, sheet_id, worksheet"
        if not config['domain'].strip():
            return False, "Tên domain không được rỗng"

    um = UserManager()

    # 👉 Tạo user trước
    success, msg = um.register(username, password)
    if not success:
        return False, msg

    # 👉 Sau đó update profile (QUAN TRỌNG)
    success, msg = um.update_profile(
        username,
        display_name.strip(),
        sheets_config,
        avatar_path=None
    )

    return success, msg

def login_user(username, password):
    success, _, profile = UserManager().login_flex(username, password)
    if success:
        st.session_state.avatar_path = profile.get('avatar_path')
        return True, profile
    return False, "Invalid username or password"

def validate_sheets_config(configs):
    """Validate sheets_config - return True if OK"""
    if not configs:
        return True  # Empty OK
    for config in configs:
        if not all(k in config for k in ['domain', 'sheet_id', 'worksheet']):
            return False
        if not config['domain'].strip():
            return False
    return True

def update_user(username, new_display_name=None, new_sheets_config=None, avatar=None, old_password=None, new_password=None):
    """
    Partial update user profile. Updates only provided valid fields.
    """
    errors = []
    
    # Validate each field independently
    if new_display_name and len(new_display_name.strip()) < 2:
        errors.append("Họ tên quá ngắn")
    
    if new_sheets_config is not None and not validate_sheets_config(new_sheets_config):
        errors.append("Sheets config invalid")
    
    if errors:
        return False, "; ".join(errors)
    
    # Prepare params - use None for unchanged fields
    display_name = new_display_name.strip() if new_display_name else None
    sheets_config = new_sheets_config if new_sheets_config is not None else None
    avatar_path = None
    
    if avatar is not None:
        import os
        os.makedirs('avatars', exist_ok=True)
        file_path = f'avatars/{username}.png'
        if hasattr(avatar, "getvalue"):
            with open(file_path, 'wb') as f:
                f.write(avatar.getvalue())
            avatar_path = file_path
        elif isinstance(avatar, str):
            avatar_path = avatar
    
    # Call DB with partial params
    result = UserManager().update_profile(username, display_name, sheets_config, avatar_path, old_password, new_password)
    return result

def logout():
    """Logout: xóa token DB + session state"""
    user_id = st.session_state.get('user_id')
    token = st.session_state.get('session_token')
    
    if token:
        SessionsManager().delete_session_token(token)
    if user_id:
        SessionsManager().clear_user_sessions(user_id)
    
    for key in ['user_id', 'user_sheets_config', 'user_domains', 
                'avatar_path', 'display_name', 'session_token']:
        if key in st.session_state:
            del st.session_state[key]
            
def get_user_domains():
    """
    Get current user's domains from session.
    """
    config = st.session_state.get('user_sheets_config', [])
    return [c['domain'] for c in config]

def is_authenticated():
    """
    Check if user is logged in.
    """
    return 'user_id' in st.session_state

def validate_session():
    """Check auth state from Mongo"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        return False
    return SessionsManager().load_auth_state(user_id) is not None

