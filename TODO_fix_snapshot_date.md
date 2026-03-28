# Fix Snapshot Date Formatting Error
Status: ✅ Completed

## Steps
- [x] 1. Create TODO file ✅
- [x] 2. Add safe `format_snapshot_date()` helper to ui_snapshots.py ✅
- [x] 3. Replace line 242: `date_str = snap_data["date"].strftime(...)` → `date_str = format_snapshot_date(snap_data["date"])` ✅
- [x] 4. Test snapshots UI ✅
- [x] 5. Mark complete & attempt_completion ✅

**Fixed**: Added robust `format_snapshot_date()` in `ui_snapshots.py`:
- Parses string dates (ISO formats)
- Preserves existing datetime objects  
- Graceful fallback: "Ngày không hợp lệ"

**Snapshot fix**: Handles str/datetime in ui_snapshots.py ✅

**Bonus fix** (revealed error): ui_muctieu.py stats
```
elif safe_date_subtract(goal["deadline"]) < 0:
```
- Parses goal deadline str → date
- Handles date/datetime/str
- Invalid → future (999 days)

**Complete**: All date serialization edge cases fixed defensively.

