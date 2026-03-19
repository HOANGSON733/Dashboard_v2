"""
Lưu và tải trạng thái phiên làm việc
"""

import streamlit as st
import json
import os
from datetime import datetime, date


# ===================== SAVE SESSION STATE =====================
def save_session_state():
    """Lưu session state vào file JSON"""
    session_data = {
        'goals': {},
        'snapshots': {},
        'saved_filters': st.session_state.saved_filters,
        'theme': st.session_state.theme,
        'notes': st.session_state.notes
    }
    
    # Convert goals (which may contain date objects) into serializable form
    for goal_id, goal in st.session_state.goals.items():
        goal_serial = goal.copy()
        if 'deadline' in goal_serial and isinstance(goal_serial['deadline'], date):
            goal_serial['deadline'] = goal_serial['deadline'].isoformat()
        if 'created' in goal_serial and isinstance(goal_serial['created'], datetime):
            goal_serial['created'] = goal_serial['created'].isoformat()
        session_data['goals'][goal_id] = goal_serial
    
    # Convert snapshots (which may contain DataFrames) into serializable form
    import pandas as pd
    for name, snap in st.session_state.snapshots.items():
        snap_serial = {}
        
        # Date -> ISO string
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
        # If data is a DataFrame, convert to list of records
        if isinstance(data_val, pd.DataFrame):
            try:
                # Convert datetime columns to strings to make JSON serializable
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
            # Fallback: stringify
            snap_serial['data'] = str(data_val)
        
        session_data['snapshots'][name] = snap_serial
    
    try:
        with open('dashboard_session.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"❌ Lỗi khi lưu session: {e}")


# ===================== LOAD SESSION STATE =====================
def load_session_state():
    """Tải session state từ file JSON"""
    import pandas as pd
    
    if os.path.exists('dashboard_session.json'):
        try:
            with open('dashboard_session.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Convert string dates back to datetime objects
            if 'goals' in session_data:
                for goal_id, goal in session_data['goals'].items():
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
                            snap_data['data'] = pd.DataFrame()
            
            return session_data
        except Exception as e:
            st.warning(f"⚠️ Không thể tải session đã lưu: {e}")
            return {}
    return {}


# ===================== INITIALIZE SESSION STATE =====================
def init_session_state():
    """Khởi tạo session state"""
    # Load saved session
    saved_session = load_session_state()
    
    # Initialize session state with saved data
    if 'goals' not in st.session_state:
        st.session_state.goals = saved_session.get('goals', {})
    if 'snapshots' not in st.session_state:
        st.session_state.snapshots = saved_session.get('snapshots', {})
    if 'saved_filters' not in st.session_state:
        st.session_state.saved_filters = saved_session.get('saved_filters', {})
    if 'theme' not in st.session_state:
        st.session_state.theme = saved_session.get('theme', 'dark').lower()
    if 'notes' not in st.session_state:
        st.session_state.notes = saved_session.get('notes', {})

