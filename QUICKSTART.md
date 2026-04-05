# Quick Start Guide

## Getting Started in 3 Steps

### 1. Install Dependencies

```bash
cd streamlit-creativity-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Paths

Edit `config/config.yaml` and update these paths:

```yaml
paths:
  metadata_path: "/path/to/your/metadata.duckdb"  # or .csv file
  video_path: "/path/to/your/videos/"
```

**Important**:
- Video files must be `.mp4` format
- Video filenames (without extension) should match the `id` column in your metadata
- **For DuckDB**: Database should have an `events` table with columns: id, team, player, jersey_number, type, body_part, start_x, start_y, end_x, end_y
- **For CSV**: File should have columns including: id, team, player, jersey_number, type, body_part, start_x, start_y, end_x, end_y

### 3. Run the App

```bash
streamlit run app.py
```

Or use the provided script:

```bash
./run.sh
```

The app will open in your browser at `http://localhost:8501`

## Testing Without a Database

If you want to test the app without setting up the full database:

1. **Disable metadata display** in `config/config.yaml`:
   ```yaml
   settings:
     display_metadata: false
     display_pitch: false
   ```

2. **Create a minimal database** or comment out database loading in `pages/videoplayer.py`

3. **Place test videos** in your video directory

## Common Issues

### ImportError: No module named 'streamlit'
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### FileNotFoundError: config/config.yaml not found
- Make sure you're running the app from the `streamlit-creativity-app` directory
- Check that config files were copied correctly

### Videos not playing
- Ensure videos are in `.mp4` format
- Check that the path in `config.yaml` is correct
- Verify file permissions

### Database connection errors
- The app can run without a database if you disable metadata display
- Check that the database path is correct
- Ensure the database file is readable

## Next Steps

- Customize the questionnaire in `config/questionnaire_fields.yaml`
- Adjust rating scales in `config/rating_scales.yaml`
- Review the full README.md for detailed documentation
- Test the full workflow: Welcome → Login → Questionnaire → Video Rating

## Deployment

To deploy this app online:

1. **Streamlit Cloud** (easiest):
   - Push to GitHub
   - Connect at share.streamlit.io
   - Configure secrets for sensitive paths

2. **Docker**:
   - Create a Dockerfile
   - Build and deploy to your hosting service

3. **Heroku/Railway**:
   - Add a `Procfile`
   - Configure environment variables
   - Deploy via Git

See README.md for detailed deployment instructions.
