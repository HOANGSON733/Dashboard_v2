"""
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
    
    return session_data

def save_session_state():
    """Save session state to MongoDB"""
    user_id = st.session_state.get('user_id', 'default')
    if user_id != 'default':
        session_data = serialize_session_data()
        SessionsManager().save_session(user_id, session_data)


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

def load_session_state(restore_auth=False):
    """Load session from MongoDB. restore_auth=False (secure)."""
    user_id = st.session_state.get('user_id', 'default')
    if user_id == 'default':
        return {}
    
    raw_data = SessionsManager().load_session(user_id)
    return deserialize_session_data(raw_data)

    
    # Convert string dates back to datetime objects for other data (always)
    if 'goals' in data:
        for goal_id, goal in data['goals'].items():
            if 'deadline' in goal and isinstance(goal['deadline'], str):
                try:
                    goal['deadline'] = datetime.fromisoformat(goal['deadline']).date()
                except Exception:
                    pass
            if 'created' in goal and isinstance(goal['created'], str):
                try:
                    goal['created'] = datetime.fromisoformat(goal['created'])
                except Exception:
                    pass
    
    if 'snapshots' in session_data:
        for snap_name, snap_data in session_data['snapshots'].items():
            # Convert date string back to datetime
            if 'date' in snap_data and isinstance(snap_data['date'], str):
                try:
                    snap_data['date'] = datetime.fromisoformat(snap_data['date'])
                except Exception:
                    try:
                        snap_data['date'] = datetime.fromisoformat(snap_data['date'].replace(' ', 'T'))
                    except Exception:
                        try:
                            snap_data['date'] = datetime.fromisoformat(snap_data['date']).replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                        except Exception:
                            snap_data['date'] = datetime.now()
            
            # Convert stored data (list of records) back to DataFrame
            if 'data' in snap_data and isinstance(snap_data['data'], list):
                try:
                    snap_data['data'] = pd.DataFrame(snap_data['data'])
                except Exception:
                    pass
    
    return session_data

def load_session_state(restore_auth=True):
    """Load session data from MongoDB"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        return {}
    
    try:
        session_data = SessionsManager().load_session(user_id)
        if restore_auth and 'user_id' not in session_data:
            session_data['user_id'] = user_id
        return session_data
    except:
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
    """Save auth state to file for F5 persistence"""
    import json
    auth_data = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    with open('session_auth.json', 'w') as f:
        json.dump(auth_data, f)

def load_auth_state_file():
    """Load auth state from file"""
    import json, os
    if os.path.exists('session_auth.json'):
        try:
            with open('session_auth.json', 'r') as f:
                data = json.load(f)
            user_id = data.get('user_id')
            timestamp_str = data.get('timestamp')
            if user_id and timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                # Check if within 24 hours
                if (datetime.utcnow() - timestamp) < timedelta(hours=24):
                    return user_id
        except:
            pass
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

