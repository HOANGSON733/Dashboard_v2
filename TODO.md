# Fix JSONDecodeError in users.json

## Information Gathered
- users.json is corrupted/truncated at line ~14: incomplete second user "Son@1234" after "hashed_password": 
- First user "Son@123" is valid with domains ["drtuananh.com", "huyenhocviet.com", "sdtc.vn"]
- user_auth.py load_users() lacks error handling, crashes on invalid JSON
- pages/auth.py calls register_user() -> load_users() -> error

## Plan
1. Repair users.json: Complete/validate JSON keeping only valid "Son@123" user (remove incomplete "Son@1234")
2. Add try/except in user_auth.py load_users(): return [] on JSON error, optionally auto-repair
3. Test auth.py after fixes

## Dependent Files
- users.json (repair)
- user_auth.py (add error handling)

## Followup steps
- Test streamlit run pages/auth.py
- Test register new user
- Test login with "Son@123"

Approve this plan to proceed?

