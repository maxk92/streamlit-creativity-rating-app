# Google Sheets Integration Architecture

## Overview

This document explains the Google Sheets integration architecture, data flow, backup strategies, and best practices for deployment.

## Architecture Design

### File Structure

```
utils/
├── gsheets_manager.py       # Central Google Sheets connection & operations
├── data_persistence.py      # Dual-write strategy implementation
└── ...

.streamlit/
└── secrets.toml            # Google Sheets credentials (never commit!)

pages/
├── welcome.py              # Optional connection test
└── videoplayer.py          # Uses save_rating() automatically
```

### Design Principles

**1. Centralized Connection Management**
- **Location**: `utils/gsheets_manager.py`
- **Why**: Single point of connection management, easy to maintain and debug
- **Pattern**: Singleton-like cached connection (`get_gsheets_connection()`)

**2. Separation of Concerns**
- **Storage logic**: `utils/data_persistence.py` handles all save/load operations
- **Connection logic**: `utils/gsheets_manager.py` handles Google Sheets API
- **Business logic**: Pages call simple `save_rating()` without knowing implementation details

**3. Dual-Write Strategy**
- **Primary**: Google Sheets (persistent, cloud-based)
- **Backup**: Local JSON files (temporary, for redundancy)
- **Reason**: Ensures no data loss even if Google Sheets API fails temporarily

## Data Flow

### When a User Submits a Rating:

```
1. videoplayer.py: User clicks "Submit Rating"
   ↓
2. Calls: save_rating(user_id, action_id, scale_values, action_not_recognized)
   ↓
3. data_persistence.py: Builds rating_data dictionary
   ↓
4. WRITES TO TWO PLACES:
   ├─→ Google Sheets (via gsheets_manager.append_rating_to_gsheets())
   │   └─→ Appends new row to "ratings" worksheet
   │       └─→ Includes timestamp
   └─→ Local JSON file (user_ratings/userid_actionid.json)
       └─→ Backup for redundancy
   ↓
5. Returns True if at least ONE write succeeded
```

### When Loading User's Rated Videos:

```
1. videoplayer.py: initialize_video_player() needs to know what user already rated
   ↓
2. Calls: get_rated_videos_for_user(user_id)
   ↓
3. data_persistence.py: TRIES TWO SOURCES:
   ├─→ PRIMARY: Google Sheets (via gsheets_manager)
   │   └─→ If successful: Returns list of action IDs
   └─→ FALLBACK: Local JSON files
       └─→ If Google Sheets fails: Reads from local files
   ↓
4. Returns list of action_ids already rated by user
```

## Backup Strategies for Production (Streamlit Cloud)

### Current Implementation: Dual-Write

**What it does:**
- Every rating written to BOTH Google Sheets AND local JSON
- If Google Sheets fails → Local JSON still saves
- If local storage fails → Google Sheets still saves

**Limitations on Streamlit Cloud:**
- Local JSON files are EPHEMERAL (cleared on app restart)
- Only useful during a single session
- NOT persistent across deployments

### Recommended Backup Strategy for Production

#### Option 1: Google Sheets Only (Simplest - Already Implemented)

**Pros:**
- ✅ Free forever
- ✅ Automatic versioning (Google Sheets revision history)
- ✅ No additional setup needed
- ✅ Can manually download as CSV/Excel anytime

**Cons:**
- ⚠️ Single point of failure (if Google Sheets API goes down)
- ⚠️ API rate limits (300 requests/minute per user)

**Backup Process:**
1. Periodically download Google Sheet as CSV manually
2. Use Google Sheets built-in version history
3. Share sheet with multiple Google accounts for redundancy

#### Option 2: Multiple Google Sheets (Redundancy)

**Architecture:**
- Write to 2+ different Google Sheets simultaneously
- If one fails, others still capture data

**Implementation:**
```python
def save_rating_redundant(rating_data):
    success_count = 0
    for sheet_name in ["ratings", "ratings_backup"]:
        if append_rating_to_gsheets(rating_data, worksheet=sheet_name):
            success_count += 1
    return success_count > 0
```

**Pros:**
- ✅ Free
- ✅ Simple implementation
- ✅ High redundancy

**Cons:**
- ⚠️ Doubles API calls
- ⚠️ More complex to sync/reconcile

### What NOT to Do on Streamlit Community Cloud

❌ **Don't rely on local file storage for backups**
- Files are ephemeral and cleared on restart
- Only useful within a single session

❌ **Don't use paid database services** (you mentioned budget constraints)
- MongoDB Atlas, PostgreSQL hosting, etc. all cost money

❌ **Don't use large files in the repo**
- Git has size limits
- Performance issues

## Best Practices

### 1. Error Handling

Always assume API calls might fail:
```python
try:
    gsheets_success = append_rating_to_gsheets(rating_data)
except Exception as e:
    logger.error(f"Google Sheets failed: {e}")
    # Fallback to alternative storage
```

### 2. Monitoring

Add logging to track success rates:
```python
print(f"[INFO] ✓ Rating saved to Google Sheets")
print(f"[WARNING] Google Sheets write failed")
```

Check logs regularly to ensure writes are succeeding.

### 3. Rate Limiting

Google Sheets API limits:
- 300 read/write requests per minute per user
- 100 requests per 100 seconds per user

For high-volume apps:
- Batch writes (collect multiple ratings, write together)
- Implement exponential backoff on failures
- Use caching for reads

### 4. Data Validation

Before writing to Google Sheets:
```python
# Ensure all required fields present
required_fields = ['user_id', 'id', 'action_not_recognized']
if all(field in rating_data for field in required_fields):
    append_rating_to_gsheets(rating_data)
```

### 5. Testing

Test connection on app startup:
```python
# In app.py or welcome.py
conn = get_gsheets_connection()
if not conn:
    st.warning("⚠️ Google Sheets connection unavailable. Using local storage only.")
```

## Deployment Checklist

### Before Deploying to Streamlit Cloud:

- [x] Google Sheets API enabled in Google Cloud Console
- [x] Service account created with credentials
- [x] Google Sheet shared with service account email
- [x] `secrets.toml` configured locally
- [ ] **Add secrets to Streamlit Cloud dashboard** (Settings → Secrets)
- [ ] Test write operation locally
- [ ] Test read operation locally
- [ ] Verify timestamp is being added to each rating
- [ ] Download initial backup of empty/test sheet

### In Streamlit Cloud Dashboard:

Go to: App Settings → Secrets

Paste your `.streamlit/secrets.toml` content:
```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
# ... rest of credentials
```

**IMPORTANT**: Never commit `.streamlit/secrets.toml` to Git!

Add to `.gitignore`:
```
.streamlit/secrets.toml
```

## Maintenance & Recovery

### Regular Backups

**Manual** (recommended initially):
1. Open Google Sheet
2. File → Download → CSV
3. Save to Google Drive with date in filename
4. Do this weekly or after significant data collection

**Automated** (future improvement):
- Set up Google Apps Script to auto-export weekly
- Or implement periodic export in your Streamlit app

### Disaster Recovery

**If Google Sheets is deleted:**
1. Check Google Drive trash (30-day retention)
2. Restore from Google Sheets version history
3. Restore from manual CSV backups
4. Restore from local JSON files (if still available)

**If API quota exceeded:**
1. App will fall back to local JSON temporarily
2. Manually upload JSON files to Google Sheets later
3. Consider implementing batch writes

**If service account credentials compromised:**
1. Revoke access in Google Cloud Console
2. Generate new service account
3. Update secrets.toml
4. Redeploy app

## Future Enhancements

1. **Batch writes**: Collect N ratings, write as single DataFrame
2. **Periodic backup**: Automated CSV downloads with timestamps
3. **Data validation dashboard**: Monitor data quality in real-time
4. **Conflict resolution**: Handle duplicate ratings gracefully
5. **Multiple sheet redundancy**: Write to backup worksheet simultaneously

## Summary

**Current Architecture:**
- ✅ Centralized connection in `gsheets_manager.py`
- ✅ Dual-write strategy in `data_persistence.py`
- ✅ Automatic append to Google Sheets
- ✅ Local JSON backup (ephemeral on cloud)

**Recommended for Production:**
- Use Google Sheets as primary storage (already implemented)
- Enable local JSON backups with "both" storage mode for redundancy
- Manually download CSV backups weekly from Google Sheets
- Monitor logs for write failures

**Cost:** $0 (all free services)

**Data Safety:** High (Google Sheets revision history + local JSON backups + manual CSV exports)
