# Google Drive Integration - Setup Instructions

**Date:** 2025-11-23
**Status:** Implementation Complete - Awaiting Configuration

---

## What Was Implemented

### 1. **New Files Created**
- `utils/gdrive_manager.py` - Handles all Google Drive operations (listing videos, downloading, caching)
- `GDRIVE_INTEGRATION.md` - Comprehensive setup and troubleshooting guide

### 2. **Modified Files**
- `requirements.txt` - Added `google-api-python-client>=2.100.0`
- `config/config.yaml` - Added `video_source` setting to switch between local/gdrive
- `.streamlit/secrets.toml` - Added `[gdrive]` section for folder IDs (placeholders added)
- `pages/videoplayer.py` - Updated to fetch videos from Google Drive
- `pages/familiarization.py` - Updated to support Google Drive familiarization videos
- `CLAUDE.md` - Added documentation about Google Drive integration

### 3. **Key Features**
- **Automatic caching** - Videos download once per session, then use cached files
- **Seamless switching** - Change `video_source` in config to switch between local/gdrive
- **Same service account** - Uses your existing Google Sheets credentials
- **No code changes needed** - Just configuration

---

## What You Need to Do Next

### Step 1: Enable Google Drive API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `streamlit-app-478710`
3. Navigate to **APIs & Services** → **Library**
4. Search for "Google Drive API" and click **Enable**

### Step 2: Create & Share Folders
1. Create two folders in your Google Drive:
   - Main videos folder (e.g., "Emotion Videos")
   - Familiarization videos folder (e.g., "Familiarization Videos")

2. Upload your `.mp4` files to these folders

3. **Share both folders** with your service account:
   - Email: `service-acc@streamlit-app-478710.iam.gserviceaccount.com`
   - Permission: **Viewer** or **Editor**

4. Get folder IDs from URLs:
   - Open folder in browser
   - Copy ID from URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Example: If URL is `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`
   - Folder ID is: `1a2b3c4d5e6f7g8h9i0j`

### Step 3: Update Secrets
In `.streamlit/secrets.toml`, replace the placeholders:

```toml
[gdrive]
video_folder_id = "YOUR_ACTUAL_FOLDER_ID"  # Replace this
familiarization_folder_id = "YOUR_ACTUAL_FOLDER_ID"  # Replace this
```

### Step 4: Switch to Google Drive
In `config/config.yaml`, change:

```yaml
paths:
  video_source: "gdrive"  # Change from "local" to "gdrive"
```

### Step 5: Deploy to Streamlit Cloud
1. Push your code to GitHub (secrets.toml won't be pushed - it's gitignored)
2. In Streamlit Cloud dashboard, go to **Settings** → **Secrets**
3. Add the same `[gdrive]` section with your folder IDs
4. Redeploy

---

## Benefits

- **No more repo bloat** - Remove videos from GitHub
- **Easy updates** - Just upload new videos to Drive
- **Free storage** - 15GB free (vs limited Streamlit Cloud storage)
- **Same service account** - No additional credentials needed

---

## Testing

For local testing:
```bash
pip install -r requirements.txt
streamlit run app.py
```

The first video will take a few seconds to download, then subsequent loads will be instant (cached).

---

## Documentation

Full details in `GDRIVE_INTEGRATION.md` including:
- Complete setup instructions
- Troubleshooting guide
- Architecture diagrams
- Cost considerations (effectively free)
- Switching between local/gdrive modes

---

## Quick Reference: Service Account Email

```
service-acc@streamlit-app-478710.iam.gserviceaccount.com
```

Share your Google Drive folders with this email address!

---

## Current Configuration Status

- [ ] Google Drive API enabled
- [ ] Main videos folder created in Google Drive
- [ ] Familiarization videos folder created in Google Drive
- [ ] Folders shared with service account
- [ ] Folder IDs added to `.streamlit/secrets.toml`
- [ ] `video_source: "gdrive"` set in `config/config.yaml`
- [ ] Tested locally
- [ ] Secrets added to Streamlit Cloud dashboard
- [ ] Deployed to Streamlit Cloud

---

## Need Help?

Refer to:
- `GDRIVE_INTEGRATION.md` for detailed setup and troubleshooting
- `CLAUDE.md` for developer documentation
- Claude Code for implementation assistance
