import streamlit as st
import json
import os
import bcrypt

USERS_FILE = 'users.json'

def load_users():
    """
    Load users from JSON file.
    """
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('users', [])
        except json.JSONDecodeError:
            print("Warning: users.json corrupted, returning empty users list")
            return []
    return []

def save_users(users):
    """
    Save users to JSON file.
    """
    data = {'users': users}
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """
    Hash password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """
    Verify password against hash.
    """
    try:
        import base64
        return bcrypt.checkpw(password.encode('utf-8'), base64.b64decode(hashed))
    except:
        # Legacy direct str hash
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, password, display_name, sheets_config):
    """
    Register new user. sheets_config is list of {'domain':str, 'sheet_id':str, 'worksheet':str}. Returns True if successful.
    """
    users = load_users()
    if any(u['username'] == username for u in users):
        return False, "Username already exists"
    if len(display_name.strip()) < 2:
        return False, "Họ và tên quá ngắn"
    hashed_pw = hash_password(password)
    import base64
    user = {
        'username': username,
        'display_name': display_name.strip(),
        'hashed_password': base64.b64encode(hashed_pw).decode('ascii'),
        'sheets_config': sheets_config  # list of dicts
    }
    users.append(user)
    save_users(users)
    return True, "Registered successfully"

def login_user(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and verify_password(password, user['hashed_password']):
            user_data = {
                'sheets_config': user.get('sheets_config', []),
                'display_name': user.get('display_name', username),
                'avatar': user.get('avatar')
            }
            # ✅ Explicit avatar set - prevents stale
            st.session_state.avatar = user_data['avatar']
            return True, user_data
    return False, "Invalid username or password"

def update_user(username, new_display_name, new_sheets_config, avatar=None, old_password=None, new_password=None):
    """
    Update user profile. Returns (success, msg).
    """
    users = load_users()
    user_idx = None

    for i, u in enumerate(users):
        if u['username'] == username:
            user_idx = i
            break

    if user_idx is None:
        return False, "User not found"

    user = users[user_idx]

    # Validate display_name
    if len(new_display_name.strip()) < 2:
        return False, "Họ và tên quá ngắn"

    # Validate sheets_config
    for config in new_sheets_config:
        if not all(k in config for k in ['domain', 'sheet_id', 'worksheet']):
            return False, "Mỗi domain phải có domain, sheet_id, worksheet"
        if not config['domain'].strip():
            return False, "Tên domain không được rỗng"

    # ✅ Update info
    user['display_name'] = new_display_name.strip()
    user['sheets_config'] = new_sheets_config

    # ✅ NEW: lưu avatar
    if avatar is not None:
        user['avatar'] = avatar

    # Password change
    if new_password is not None:
        if not old_password:
            return False, "Phải nhập mật khẩu cũ để thay đổi"
        if not verify_password(old_password, user['hashed_password']):
            return False, "Mật khẩu cũ không đúng"

        hashed_new = hash_password(new_password)
        import base64
        user['hashed_password'] = base64.b64encode(hashed_new).decode('ascii')

    save_users(users)
    return True, "Cập nhật thành công"

def logout():
    """
    Logout current user - FIXED.
    """
    # Clear ALL persistent session files
    try:
        import persistence
        persistence.clear_all_session_files()
    except ImportError:
        pass
    # Clear session state
    if 'user_id' in st.session_state:
        del st.session_state['user_id']
    if 'user_sheets_config' in st.session_state:
        del st.session_state['user_sheets_config']
    if 'user_domains' in st.session_state:
        del st.session_state['user_domains']
    # ✅ Clear avatar explicitly
    if 'avatar' in st.session_state:
        del st.session_state['avatar']

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
    """
    Validate session w/ AUTO-RECOVERY (F5-safe enhancement)
    """
    if 'user_id' not in st.session_state:
        return False
    
    users = load_users()
    for user in users:
        if user['username'] == st.session_state.user_id:
            # ✅ AUTO-RESTORE missing config (F5 safe)
            if 'user_sheets_config' not in st.session_state:
                st.session_state.user_sheets_config = user.get('sheets_config', [])
            if 'display_name' not in st.session_state:
                st.session_state.display_name = user.get('display_name', st.session_state.user_id)
            if 'avatar' not in st.session_state:
                st.session_state.avatar = user.get('avatar')
            return True
    return False

