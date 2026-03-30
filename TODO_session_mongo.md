# TODO: Migrate Session JSON to MongoDB Always
Status: 🔄 In Progress (BLACKBOXAI)

## Plan Steps (Sequential)

### 1. ✅ Create TODO.md [DONE]
### 2. ✅ Update `db.py` 
   - Add `save_marked_keywords(user_id, keywords)` and `load_marked_keywords(user_id)` to SessionsManager [DONE]
### 3. ✅ Update `persistence.py`
   - Add `save_marked_keywords()`, `load_marked_keywords()`
   - Extend `serialize_session_data()` to include `'marked_keywords': list(st.session_state.marked_keywords)`
   - Update `init_session_state()` to load/convert marked_keywords [DONE]
### 4. ✅ Update `dashboard.py`
   - Import new persistence functions from persistence
   - Replace file load_marked/save_marked with Mongo calls
   - Call `save_marked_keywords()` on table changes and clear [DONE]
### 5. 🧪 Test
   - streamlit run dashboard.py
   - Login Son@1235, mark keywords in table, F5 → persists?
   - Check no more JSON writes
### 6. 🧹 Cleanup: Delete old JSON files?
### 7. ✅ attempt_completion()

