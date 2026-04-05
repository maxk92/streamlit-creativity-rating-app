# Google Drive Video Integration Guide

## Overview

This app supports loading videos from Google Drive instead of the local filesystem. This is especially useful for Streamlit Cloud deployments where local storage is ephemeral and limited.

## Why Use Google Drive?

**Benefits:**
- **Free storage**: Google Drive provides 15GB free storage (much more than Streamlit Cloud)
- **Easy updates**: Upload new videos to Drive without redeploying the app
- **No git repo bloat**: Keep large video files out of your repository
- **Same service account**: Uses your existing Google Sheets credentials

**Trade-offs:**
- First video load per session is slower (downloads from Drive)
- Videos are cached temporarily to improve subsequent loads
- Requires initial setup and folder sharing

## Setup Instructions

### 1. Enable Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (the same one you use for Google Sheets)
3. Navigate to **APIs & Services** → **Library**
4. Search for "Google Drive API"
5. Click **Enable**

### 2. Create Google Drive Folders

1. Create two folders in your Google Drive:
   - One for main videos (e.g., "Emotion Videos")
   - One for familiarization videos (e.g., "Familiarization Videos")

2. Upload your `.mp4` video files to these folders

3. **Share each folder** with your service account email:
   - Right-click folder → Share
   - Add your service account email (found in `.streamlit/secrets.toml` as `client_email`)
   - Give it **Viewer** or **Editor** permissions
   - Click Share

4. Get the folder IDs from the URLs:
   - Open each folder in Google Drive
   - Copy the ID from the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Example: If URL is `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`
   - Folder ID is: `1a2b3c4d5e6f7g8h9i0j`

### 3. Configure Secrets

Add the folder IDs to `.streamlit/secrets.toml`:

```toml
[gdrive]
video_folder_id = "YOUR_MAIN_VIDEOS_FOLDER_ID"
familiarization_folder_id = "YOUR_FAMILIARIZATION_VIDEOS_FOLDER_ID"
```

**Important:**
- This file is already in `.gitignore` - never commit it
- For Streamlit Cloud: Add these secrets via the dashboard (Settings → Secrets)

### 4. Update Configuration

In `config/config.yaml`, change the video source:

```yaml
paths:
  # Change from "local" to "gdrive"
  video_source: "gdrive"
```

### 5. Install Dependencies

The required package `google-api-python-client` is already in `requirements.txt`.

For local development:
```bash
pip install -r requirements.txt
```

For Streamlit Cloud: Dependencies are installed automatically from `requirements.txt`.

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit App                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. App starts → Reads config.yaml                         │
│     └─ video_source: "gdrive"                              │
│                                                             │
│  2. Initialize video player                                │
│     └─ get_all_video_filenames(folder_id)                  │
│        └─ Lists videos in Google Drive folder              │
│                                                             │
│  3. User selects video                                      │
│     └─ get_video_path(filename, folder_id)                 │
│        ├─ Check cache (already downloaded?)                │
│        │  ├─ Yes: Return cached path                       │
│        │  └─ No: Download from Drive → Cache → Return path │
│        └─ Display video from temp path                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Caching Strategy

Videos are downloaded once per app session and cached in temporary files:

- **First access**: Downloads video from Google Drive (may take a few seconds)
- **Subsequent access**: Uses cached temporary file (instant)
- **Cache lifetime**: Until app restarts or container is recycled
- **Memory usage**: One video at a time is displayed, but cache persists

You can clear the cache programmatically if needed:
```python
from utils.gdrive_manager import clear_video_cache
clear_video_cache()
```

## File Structure

```
utils/
├── gdrive_manager.py           # Google Drive operations
│   ├── get_gdrive_service()    # Service account connection
│   ├── list_videos_in_folder() # List videos in folder
│   ├── get_video_path()        # Get local path (downloads if needed)
│   └── clear_video_cache()     # Clear temporary files
└── ...

pages/
├── videoplayer.py              # Main rating interface (updated)
└── familiarization.py          # Practice videos (updated)

config/
└── config.yaml
    └── video_source: "gdrive"  # Switch between "local" and "gdrive"

.streamlit/
└── secrets.toml
    └── [gdrive]
        ├── video_folder_id
        └── familiarization_folder_id
```

## Switching Between Local and Google Drive

You can easily switch between local filesystem and Google Drive by changing one setting:

**Use Google Drive:**
```yaml
# config/config.yaml
paths:
  video_source: "gdrive"
```

**Use Local Filesystem:**
```yaml
# config/config.yaml
paths:
  video_source: "local"
  video_path: "data/videos/"
  familiarization_video_path: "data/videos_familiarization"
```

No code changes needed - the app automatically uses the appropriate source.

## Troubleshooting

### Videos Not Loading

**Error:** "Failed to load videos from Google Drive"

**Solutions:**
1. Check that Google Drive API is enabled in your Google Cloud project
2. Verify folder IDs in `.streamlit/secrets.toml` are correct
3. Ensure folders are shared with your service account email
4. Check console output for specific error messages

### Slow Initial Load

**Symptom:** First video takes 5-10 seconds to load

**Explanation:** This is normal - the video is being downloaded from Google Drive. Subsequent loads use the cache and are instant.

**Optimization:** Consider using smaller video files or adding a loading indicator.

### Service Account Permissions

**Error:** "Access denied" or "Permission denied"

**Solutions:**
1. Open the Google Drive folder in a browser
2. Click Share
3. Verify your service account email is listed with Viewer/Editor permissions
4. If not, add it: `service-acc@YOUR-PROJECT.iam.gserviceaccount.com`

### Folder ID Not Found

**Error:** "Folder not found"

**Solutions:**
1. Double-check the folder ID in `.streamlit/secrets.toml`
2. Make sure you copied the ID from the folder URL, not the file URL
3. Verify the folder is not in the trash
4. Ensure it's a folder ID, not a file ID

## Deployment Checklist

### For Streamlit Cloud:

- [ ] Google Drive API enabled in Google Cloud Console
- [ ] Videos uploaded to Google Drive folders
- [ ] Folders shared with service account email
- [ ] Folder IDs added to Streamlit Cloud secrets (Settings → Secrets)
- [ ] `video_source: "gdrive"` in `config/config.yaml`
- [ ] `google-api-python-client>=2.100.0` in `requirements.txt`
- [ ] Code pushed to GitHub
- [ ] App deployed and tested

### For Local Development:

- [ ] Google Drive API enabled
- [ ] Folders shared with service account
- [ ] Folder IDs in `.streamlit/secrets.toml` (local file, not committed)
- [ ] `pip install -r requirements.txt` executed
- [ ] `video_source: "gdrive"` in `config/config.yaml`
- [ ] Test with `streamlit run app.py`

## Cost Considerations

**Google Drive API:**
- **Free tier**: 1 billion queries per day
- **Typical usage**: ~2-5 API calls per video (list + download)
- **Estimated capacity**: Thousands of video views per day
- **Cost**: Effectively free for typical research use cases

**Google Drive Storage:**
- **Free tier**: 15 GB
- **Typical video size**: 5-50 MB per video
- **Estimated capacity**: 300-3000 videos (depending on size)
- **Cost**: Free for most use cases; $1.99/month for 100 GB if needed

## Advanced Configuration

### Custom Scopes

By default, the app uses `drive.readonly` scope. To modify:

```python
# In utils/gdrive_manager.py
credentials = Credentials.from_service_account_info(
    credentials_dict,
    scopes=['https://www.googleapis.com/auth/drive.readonly']  # Change here
)
```

### Download Progress Indicators

The download function includes console logging. To add a UI progress indicator:

```python
# In utils/gdrive_manager.py, modify download_video_to_temp()
with st.spinner(f"Downloading {filename}..."):
    # Download code here
```

### Multiple Video Folders

To support multiple video folders (e.g., different categories):

1. Add folder IDs to secrets:
```toml
[gdrive]
video_folder_id = "main_folder_id"
category_a_folder_id = "folder_a_id"
category_b_folder_id = "folder_b_id"
```

2. Modify initialization logic to select appropriate folder based on experiment condition

## Migration from Local to Google Drive

### Step-by-step Migration:

1. **Backup your local videos** (optional but recommended)

2. **Upload videos to Google Drive**:
   - Maintain same filenames as local videos
   - Preserve metadata.csv file references

3. **Test in parallel**:
   - Keep `video_source: "local"` initially
   - Set up Google Drive folders and test separately
   - Verify all videos load correctly

4. **Switch over**:
   - Change `video_source: "gdrive"`
   - Test thoroughly
   - Monitor for any issues

5. **Clean up** (optional):
   - Remove local video files from git repo
   - Update `.gitignore` if needed

## Related Documentation

- `README.md`: Main application documentation
- `GSHEETS_ARCHITECTURE.md`: Google Sheets integration
- `CLAUDE.md`: Development guide for Claude Code
