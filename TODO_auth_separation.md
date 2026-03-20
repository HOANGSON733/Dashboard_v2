# TODO: Auth Separation Progress

✅ pages/auth.py updated (auto-redirects on login/register)

✅ dashboard.py cleaned:
 - Removed user_auth imports & initial check
 - Inline logout + switch to auth
 - session_state.user_domains
 - Fail-safe check added

Next:
1. Test: Run `streamlit run dashboard.py`
2. Complete
