# TODO: Fix F5 Domain Access Error - Approved Plan

## ✅ Step 1: Create TODO.md [COMPLETED]

## ✅ Step 2: Update persistence.py
- Soften validation logic 
- Add users.json fallback recovery
- Simplify force_clear_session() [COMPLETED]

## ✅ Step 3: Update dashboard.py  
- Add robust auth validation BEFORE domain check
- Auto-restore user_sheets_config if missing
- Fix init_session_state timing [COMPLETED]

## ✅ Step 4: Enhance user_auth.py
- Improve validate_session() with auto-recovery [COMPLETED]

## ✅ Step 5: Test & Verify
```
✅ Login → F5 → Domain still accessible
✅ Multi-tab F5 safe  
✅ Logout clears correctly
✅ Snapshots/goals persist
```

## ✅ Step 6: Update TODO.md [COMPLETED]

