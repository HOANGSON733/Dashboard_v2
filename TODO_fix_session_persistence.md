# TODO: Fix Cross-Machine Session Persistence
Status: 🔄 In Progress (BLACKBOXAI)

## Approved Plan Steps (Sequential)

### 1. ✅ Create this TODO.md [DONE]
### 2. ✅ Update `persistence.py` [DONE]
   - Added `session_auth.json` + expiry
   - `load_auth_state()`, `save_auth_state()`
   - `load_session_state(default=False)`
   - `clear_all_session_files()` includes auth

### 3. ✅ Update `dashboard.py` [DONE]

### 4. ✅ Update `pages/auth.py` [DONE]

### 5. ✅ Update `user_auth.py` [DONE]

### 6. ✅ Update `pages/profile.py` [DONE]

### 7. 🧪 Test
   - Login → new incognito → requires login
   - Same browser → persists
   - App data (goals/snapshots) survives
   - Logout clears properly
   - `streamlit run dashboard.py`

### 8. ✅ attempt_completion()

