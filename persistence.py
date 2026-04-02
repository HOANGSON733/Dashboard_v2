"""
persistence.py - Lớp quản lý lưu và tải trạng thái phiên làm việc của người dùng từ MongoDB.
Lưu và tải trạng thái phiên làm việc
"""

import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
from db import SessionsManager


# ===================== SAVE SESSION STATE =====================
def serialize_session_data():
    """Serialize session data to dict (JSON compatible)"""
    session_data = {
        'user_id': st.session_state.get('user_id'),
        'user_sheets_config': st.session_state.get('user_sheets_config', []),
        'selected_domain': st.session_state.get('selected_domain', ''),
        'goals': {},
        'snapshots': {},
        'saved_filters': st.session_state.get('saved_filters', {}),
        'theme': st.session_state.get('theme', 'dark'),
        'notes': st.session_state.get('notes', {}),
        'display_name': st.session_state.get('display_name', ''),
        'avatar_path': st.session_state.get('avatar_path', None),
    }
    
    # Serialize goals
    for goal_id, goal in st.session_state.get('goals', {}).items():
        goal_serial = goal.copy()
        if 'deadline' in goal_serial and isinstance(goal_serial['deadline'], date):
            goal_serial['deadline'] = goal_serial['deadline'].isoformat()
        if 'created' in goal_serial and isinstance(goal_serial['created'], datetime):
            goal_serial['created'] = goal_serial['created'].isoformat()
        session_data['goals'][goal_id] = goal_serial
    
    # Serialize snapshots
    for name, snap in st.session_state.get('snapshots', {}).items():
        snap_serial = {}
        date_val = snap.get('date')
        if isinstance(date_val, datetime):
            snap_serial['date'] = date_val.isoformat()
        elif isinstance(date_val, date):
            snap_serial['date'] = date_val.isoformat()
        else:
            snap_serial['date'] = str(date_val)
        snap_serial['score'] = snap.get('score')
        snap_serial['note'] = snap.get('note', '')
        data_val = snap.get('data')
        if isinstance(data_val, pd.DataFrame):
            try:
                data_copy = data_val.copy()
                for col in data_copy.columns:
                    if pd.api.types.is_datetime64_any_dtype(data_copy[col]):
                        data_copy[col] = data_copy[col].astype(str)
                snap_serial['data'] = data_copy.to_dict(orient='records')
            except Exception:
                snap_serial['data'] = []
        elif isinstance(data_val, list):
            snap_serial['data'] = data_val
        else:
            snap_serial['data'] = str(data_val)
        session_data['snapshots'][name] = snap_serial
    
    # Serialize marked_keywords
    session_data['marked_keywords'] = [[str(kw), str(day)] for kw, day in st.session_state.get('marked_keywords', set())]
    
    return session_data

def save_session_state():
    """Save session state to MongoDB"""
    user_id = st.session_state.get('user_id', 'default')
    if user_id != 'default':
        session_data = serialize_session_data()
        SessionsManager().save_session(user_id, session_data)

def save_marked_keywords():
    """Save marked keywords to MongoDB immediately"""
    user_id = st.session_state.get('user_id', 'default')
    if user_id != 'default' and 'marked_keywords' in st.session_state:
        keywords_list = [[str(kw), str(day)] for kw, day in st.session_state.marked_keywords]
        db = SessionsManager()
        # Keep session_data in sync and support both root-level and nested storage
        existing = db.load_session(user_id) or {}
        existing['marked_keywords'] = keywords_list
        db.save_session(user_id, existing)
        # Keep deprecated root field for backward compatibility
        db.sessions.update_one(
            {'user_id': user_id},
            {'$set': {'marked_keywords': keywords_list, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

def load_marked_keywords():
    """Load marked keywords from MongoDB"""
    user_id = st.session_state.get('user_id', 'default')
    if user_id == 'default':
        return set()
    db = SessionsManager()
    # check direct root field first (legacy path)
    keywords_list = db.load_marked_keywords(user_id)
    if not keywords_list:
        session_data = db.load_session(user_id) or {}
        if isinstance(session_data, dict) and 'marked_keywords' in session_data:
            keywords_list = session_data.get('marked_keywords', [])
        elif isinstance(session_data, dict) and 'session_data' in session_data:
            keywords_list = session_data['session_data'].get('marked_keywords', [])
        else:
            keywords_list = []
    return set(tuple(k) for k in keywords_list)


# ===================== LOAD SESSION STATE =====================
def deserialize_session_data(raw_data):
    """Deserialize raw session data back to live objects"""
    data = raw_data.copy()
    
    # Deserialize goals
    if 'goals' in data:
        for goal_id, goal in data['goals'].items():
            if 'deadline' in goal and isinstance(goal['deadline'], str):
                try:
                    data['goals'][goal_id]['deadline'] = datetime.fromisoformat(goal['deadline']).date()
                except:
                    pass
            if 'created' in goal and isinstance(goal['created'], str):
                try:
                    data['goals'][goal_id]['created'] = datetime.fromisoformat(goal['created'])
                except:
                    pass
    
    # Deserialize snapshots
    if 'snapshots' in data:
        for snap_name, snap in data['snapshots'].items():
            if 'date' in snap and isinstance(snap['date'], str):
                try:
                    snap['date'] = datetime.fromisoformat(snap['date'])
                except:
                    snap['date'] = datetime.now()
            if 'data' in snap and isinstance(snap['data'], list):
                try:
                    snap['data'] = pd.DataFrame(snap['data'])
                except:
                    pass
    
    return data

def load_session_state(restore_auth=True):
    """Load session data from MongoDB"""
    user_id = st.session_state.get('user_id', 'default')
    if user_id == 'default' or not user_id:
        return {}

    try:
        session_data = SessionsManager().load_session(user_id) or {}
        # Root legacy marked_keywords may exist in collection alongside session_data
        legacy_marked = SessionsManager().load_marked_keywords(user_id)
        if legacy_marked:
            session_data.setdefault('marked_keywords', legacy_marked)

        deserialized = deserialize_session_data(session_data)
        if restore_auth and 'user_id' not in deserialized:
            deserialized['user_id'] = user_id
        return deserialized
    except Exception:
        return {}


# ===================== INITIALIZE SESSION STATE =====================
def clear_all_session_files():
    """Deprecated - use SessionsManager.clear_user_sessions per user"""
    print("clear_all_session_files deprecated - use Mongo clear")

def save_auth_state(user_id):
    """Save auth state to MongoDB (24h TTL)"""
    SessionsManager().save_auth_state(user_id)

def load_auth_state(user_id):
    """Load auth state from MongoDB"""
    return SessionsManager().load_auth_state(user_id)

def save_auth_state_file(user_id):
    """NO-OP: file-based auth persistence is deprecated for security reasons."""
    # Previously this wrote a shared server file session_auth.json.
    # This is insecure in multi-user/multi-machine environments because it leaks
    # the last logged-in user to all other sessions on the same server.
    return None

def load_auth_state_file():
    """Load auth state from file"""
    # File-based auth state is deprecated and disabled to prevent a shared
    # auth state across different clients. Authentication is now session-only
    # in Streamlit + server-side auth TTL in MongoDB.
    return None

def init_session_state():
    """Initialize APP data from MongoDB"""
    saved_session = load_session_state()
    
    if 'avatar_path' not in st.session_state:
        st.session_state.avatar_path = saved_session.get('avatar_path')

    # Keep user_sheets_config if existing in saved session
    if 'user_sheets_config' not in st.session_state:
        st.session_state.user_sheets_config = saved_session.get('user_sheets_config', [])
    
    # App data
    for key in ['goals', 'snapshots', 'saved_filters', 'selected_domain', 'theme', 'notes', 'display_name']:
        if key not in st.session_state:
            st.session_state[key] = saved_session.get(key, {} if key in ['goals', 'snapshots', 'saved_filters', 'notes'] else '' if key == 'selected_domain' else 'dark')
    
    # Load marked_keywords from session state or legacy storage.
    if 'marked_keywords' not in st.session_state:
        st.session_state.marked_keywords = load_marked_keywords()
    elif isinstance(st.session_state.marked_keywords, set):
        # ensure consistent tuple shape
        st.session_state.marked_keywords = set(_ for _ in st.session_state.marked_keywords)
    elif 'marked_keywords' in saved_session:
        st.session_state.marked_keywords = set(tuple(k) for k in saved_session['marked_keywords'])

