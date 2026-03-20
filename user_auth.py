import streamlit as st
import json
import os
import bcrypt

USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file."""
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
    """Save users to JSON file."""
    data = {'users': users}
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify password against hash."""
    try:
        import base64
        return bcrypt.checkpw(password.encode('utf-8'), base64.b64decode(hashed))
    except:
        # Legacy direct str hash
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, password, domains):
    """Register new user. Returns True if successful."""
    users = load_users()
    if any(u['username'] == username for u in users):
        return False, "Username already exists"
    hashed_pw = hash_password(password)
    import base64
    user = {
        'username': username,
        'hashed_password': base64.b64encode(hashed_pw).decode('ascii'),
        'domains': domains  # list of domain names
    }
    users.append(user)
    save_users(users)
    return True, "Registered successfully"

def login_user(username, password):
    """Login user. Returns (success, domains) or (False, error)."""
    users = load_users()
    for user in users:
        if user['username'] == username and verify_password(password, user['hashed_password']):
            return True, user['domains']
    return False, "Invalid username or password"

def logout():
    """Logout current user."""
    if 'user_id' in st.session_state:
        del st.session_state['user_id']
    if 'user_domains' in st.session_state:
        del st.session_state['user_domains']

def get_user_domains():
    """Get current user's domains from session."""
    return st.session_state.get('user_domains', [])

def is_authenticated():
    """Check if user is logged in."""
    return 'user_id' in st.session_state


def validate_session():
    """Validate if session user/domains match users.json"""
    if 'user_id' not in st.session_state or not st.session_state.get('user_domains'):
        return False
    
    users = load_users()
    for user in users:
        if (user['username'] == st.session_state.user_id and 
            user['domains'] == st.session_state.user_domains):
            return True
    return False
