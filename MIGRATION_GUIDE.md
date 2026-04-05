# Migration Guide: Kivy to Streamlit

This document explains the differences between the Kivy desktop app and the new Streamlit web app.

## Architecture Comparison

### Kivy App (Desktop)
- **UI Framework**: Kivy with `.kv` layout files
- **Navigation**: ScreenManager with Screen classes
- **State Management**: Class properties and instance variables
- **User Input**: Keyboard navigation, mouse/touch
- **Deployment**: Desktop application, requires installation

### Streamlit App (Web)
- **UI Framework**: Streamlit (web-based)
- **Navigation**: Session state with page routing
- **State Management**: `st.session_state` dictionary
- **User Input**: Web forms, buttons, sliders
- **Deployment**: Web app, accessible via browser

## File Structure Mapping

| Kivy App | Streamlit App | Notes |
|----------|---------------|-------|
| `CreativityRatingApp.py` | `app.py` + `pages/*.py` | Split into multiple modules |
| `rating.kv` | Built-in Streamlit components | No separate layout file needed |
| `utils/write_ratings2csv.py` | `utils/export_to_csv.py` | Same functionality |
| `config/*.yaml` | `config/*.yaml` | Identical configuration files |
| `User` class | `utils/user.py` | Identical user model |

## Feature Parity

### ✅ Fully Implemented

- **Welcome Screen**: Instructions and navigation
- **Login Screen**: Returning user validation
- **Questionnaire**: Dynamic form generation from YAML
- **User ID Generation**: Same algorithm as Kivy app
- **Video Playback**: HTML5 video player
- **Rating Scales**: Dynamic generation (discrete, slider, text)
- **Required vs Optional Scales**: Same validation logic
- **Action Not Recognized**: Checkbox to skip rating
- **Data Persistence**: JSON files (same format)
- **CSV Export**: Same export functionality
- **Database Integration**: DuckDB for metadata

### 🔄 Modified

- **Metadata Display**: Simplified layout (horizontal metrics)
- **Pitch Visualization**: Uses matplotlib (same as Kivy)
- **Navigation**: Web-based buttons instead of keyboard
- **Video Controls**: Browser's native video controls

### ❌ Not Implemented (Desktop-Specific)

- **Fullscreen Mode**: Web apps use browser fullscreen
- **Keyboard Navigation**: Not standard for web apps
- **Focus Indicators**: Uses Streamlit's default focus
- **Custom Widgets**: Uses Streamlit's built-in components

## Configuration

### No Changes Required

The same YAML configuration files work in both apps:
- `config/config.yaml`
- `config/questionnaire_fields.yaml`
- `config/rating_scales.yaml`

### Path Configuration

Update paths in `config/config.yaml`:

```yaml
paths:
  metadata_path: "/absolute/path/to/metadata.duckdb"  # or .csv file
  video_path: "/absolute/path/to/videos/"
```

**Note**: For web deployment, you may need to:
- Store videos in cloud storage (S3, Google Cloud Storage)
- Use remote database connection
- Configure paths via environment variables

## Data Compatibility

### JSON Files

The Streamlit app uses the **same JSON format** as the Kivy app:

**User Data** (`user_data/{user_id}.json`):
```json
{
  "user_id": "abcd1234",
  "gender": "Male",
  "age": 25,
  "saved_at": "2024-01-01T12:00:00",
  ...
}
```

**Ratings** (`user_ratings/{user_id}_{action_id}.json`):
```json
{
  "user_id": "abcd1234",
  "id": "action123",
  "action_not_recognized": false,
  "creativity": 5,
  "technical_correctness": 6,
  ...
}
```

### CSV Exports

The export script produces identical CSV files:
- `output/ratings.csv`
- `output/mean_ratings.csv`
- `output/users.csv`
- `output/rating_log.txt`

## Deployment Options

### Option 1: Local Development (Same as Kivy)

```bash
cd streamlit-creativity-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Access at: `http://localhost:8501`

### Option 2: Streamlit Cloud (Public Web App)

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Configure secrets for database/video paths
4. Deploy!

Users can access via URL (e.g., `yourapp.streamlit.app`)

### Option 3: Self-Hosted (Private Web App)

Deploy on your own server:
- Docker container
- Cloud VM (AWS, Google Cloud, Azure)
- Internal server

Requires:
- Web server (nginx/Apache)
- Python environment
- Process manager (supervisor/systemd)

## User Experience Changes

### For Researchers

| Aspect | Kivy App | Streamlit App |
|--------|----------|---------------|
| **Setup** | Users install app | Share URL |
| **Updates** | Redistribute app | Update server |
| **Data Collection** | Manual file transfer | Download from server |
| **Access Control** | Physical access | Web authentication (if added) |

### For Participants

| Aspect | Kivy App | Streamlit App |
|--------|----------|---------------|
| **Access** | Need installation | Click link |
| **Platform** | Desktop only | Any device with browser |
| **Controls** | Keyboard + mouse | Click/touch |
| **Session** | Can pause anytime | Browser session |

## Migration Checklist

- [ ] Install Streamlit app dependencies
- [ ] Copy configuration files (already done)
- [ ] Update paths in `config/config.yaml`
- [ ] Test questionnaire workflow
- [ ] Test video rating workflow
- [ ] Verify data persistence (check JSON files)
- [ ] Test CSV export
- [ ] (Optional) Deploy to web server

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Configuration file errors
- Ensure you're in the `streamlit-creativity-app` directory
- Check YAML syntax (use online validator)

### Video playback issues
- Use `.mp4` format (H.264 codec recommended)
- Check browser compatibility
- Test with a small sample video first

### Database connection issues
- Verify DuckDB file path
- Test connection: `python -c "import duckdb; duckdb.connect('path/to/db.duckdb')"`
- For remote databases, ensure network access

## Future Enhancements

Potential additions for the Streamlit version:

1. **User Authentication**: Add login with password
2. **Admin Dashboard**: View statistics in real-time
3. **Cloud Storage**: S3/GCS for videos
4. **Remote Database**: PostgreSQL instead of DuckDB
5. **Mobile Optimization**: Responsive design
6. **Progress Tracking**: Show percentage complete
7. **Multi-language**: Support for different languages

## Support

If you encounter issues during migration:

1. Check the README.md for detailed documentation
2. Review QUICKSTART.md for setup instructions
3. Compare JSON output with Kivy app to verify compatibility
4. Test with a small dataset first

## Summary

The Streamlit app is a **functionally equivalent** web-based version of the Kivy desktop app:

- ✅ Same data format and storage
- ✅ Same configuration system
- ✅ Same user ID generation
- ✅ Same rating workflow
- ✅ Simpler deployment for web access
- ✅ Easier to maintain and update

The main trade-off is moving from a desktop application to a web application, which changes how users access the app but maintains all core functionality.
