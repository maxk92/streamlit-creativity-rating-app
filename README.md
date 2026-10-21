# Soccer Creativity Rating App

A web application for collecting subjective creativity ratings of soccer actions from video clips. Participants watch short clips of soccer actions and rate them on creativity, technical correctness, and aesthetic appeal. Built with Streamlit; supports local and Google Sheets/Drive storage.

---

## Installation

Requires Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd streamlit-creativity-app
uv sync                  # creates .venv and installs all dependencies
```

---

## Configuration

All behaviour is driven by YAML files in `config/`. No code changes are needed for typical study customisation.

### `config/config.yaml`

```yaml
app:
  title: "My Rating App"   # browser tab title
  icon: ""                 # emoji or leave empty

paths:
  metadata_source: "local"              # "local" or "r2"
  metadata_path: "data/events.csv"      # used when metadata_source = "local"
  r2_metadata_key: "metadata/events.csv" # used when metadata_source = "r2"

  # Video source: "local" or "r2" (Cloudflare R2 bucket)
  video_source: "local"
  video_path: "data/videos/"            # used when video_source = "local"
  familiarization_video_path: "data/videos_familiarization/"
  r2_video_prefix: "videos/"            # used when video_source = "r2"
  r2_familiarization_prefix: "videos_familiarization/"

settings:
  min_ratings_per_video: 2   # stop showing a video once it has this many ratings

  # --- Files ---
  questionnaire_fields_file: "config/questionnaire_fields.yaml"
  rating_scales_file:        "config/rating_scales.yaml"
  page_texts_file:           "config/page_texts.yaml"

  # --- Rating interface layout ---
  # "combined"  — video and rating scales on one screen (default)
  # "separate"  — first screen shows video only, second screen shows scales
  display_mode: "combined"

  # --- Video display ---
  display_metadata: true        # show metadata bar above video
  display_pitch: true           # show pitch visualisation next to video
  video_playback_mode: "loop"   # "loop" = repeats with controls; "once" = plays once, no controls
  video_player_height: 600      # iframe height in px (only used for "once" mode)
  video_pitch_column_ratio: [55, 45]

  # --- Metadata columns shown above video ---
  metadata_to_show:
    - { label: "Team",   column: "team" }
    - { label: "Player", column: "player" }
    - { label: "Type",   column: "type" }

  # --- Rating interface ---
  rating_section_heading: "Please rate the action on the following dimensions:"
  show_action_not_recognized: true   # "Action not recognized" button; clicking it
                                     # immediately saves the rating and advances

  # --- Pitch visualisation ---
  pitch_type: "statsbomb"
  pitch_color: "grass"
  pitch_arrow_color: "blue"

  # --- Familiarization (practice trials before the main task) ---
  enable_familiarization: false   # set true to show 3 practice videos first

  # --- Video selection ---
  number_of_videos: null   # max videos per session (null = all available)

  # Stratified sampling (optional; leave commented for simple random sampling)
  # variables_for_stratification:
  #   - variable: "outcome"
  #     levels: ["Win", "Loss"]
  #     proportions: [0.5, 0.5]   # must sum to 1.0

  # --- Skip pages (useful during development) ---
  skip_welcome:      false
  skip_login:        false
  skip_consent:      false
  skip_questionnaire: false

  # --- Storage ---
  # "local"  — JSON files in user_data/ and user_ratings/
  # "online" — Google Sheets (requires secrets.toml)
  # "both"   — Google Sheets + local JSON
  storage_mode: "local"
```

**Google Sheets** (when `storage_mode: "online"` or `"both"`): add credentials to `.streamlit/secrets.toml`. See [Streamlit secrets docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

#### Hosting videos on Cloudflare R2

For online deployments, keep videos out of the git repository and serve them from a [Cloudflare R2](https://developers.cloudflare.com/r2/) bucket (S3-compatible, 10 GB free, no egress fees). The bucket stays private: the app lists the videos and hands each participant's browser a short-lived presigned URL, so videos stream directly from R2 and never pass through the Streamlit server.

1. In the Cloudflare dashboard go to **R2 → Create bucket** (e.g. `creativity-videos`). Leave public access disabled.
2. Go to **R2 → Manage API tokens → Create API token** with *Object Read & Write* permission, limited to that bucket. Note the Access Key ID, Secret Access Key and your Account ID.
3. Add the credentials to `.streamlit/secrets.toml` (and to the app's secrets on Streamlit Community Cloud):

   ```toml
   [r2]
   account_id = "..."
   access_key_id = "..."
   secret_access_key = "..."
   bucket = "creativity-videos"
   ```

4. Upload the videos (already-uploaded files are skipped on re-runs):

   ```bash
   python utils/upload_to_r2.py data/videos videos/
   python utils/upload_to_r2.py data/videos_familiarization videos_familiarization/
   python utils/upload_to_r2.py data/events.csv metadata/   # optional, for metadata_source: "r2"
   ```

   Alternatively upload via the Cloudflare dashboard or `rclone`.

5. Set `video_source: "r2"` (and optionally `metadata_source: "r2"`) in `config/config.yaml`, with the prefixes matching the upload.

---

### `config/questionnaire_fields.yaml`

Each field shown to participants before the rating task:

```yaml
- active: true
  type: "multiple_choice"   # or "text" / "numeric"
  field_name: "experience"
  title: "How many years have you watched football?"
  options: ["< 1", "1–5", "5–10", "> 10"]
  required_to_proceed: true
  required_for_user_id: false   # set true to include in anonymous ID generation
```

Set `active: false` to hide a field without deleting it.

---

### `config/rating_scales.yaml`

Each scale shown per video. Three types:

```yaml
# Discrete (pill buttons)
- active: true
  type: "discrete"
  title: "Creativity"
  label_low: "not creative"
  label_high: "very creative"
  values: [1, 2, 3, 4, 5, 6, 7]
  required_to_proceed: true

# Slider
- active: true
  type: "slider"
  title: "Confidence"
  label_low: "0 %"
  label_high: "100 %"
  slider_min: 0
  slider_max: 100
  initial_state: "low"   # "low" | "center" | "high"
  required_to_proceed: false

# Free text
- active: false
  type: "text"
  title: "Comments"
  required_to_proceed: false
```

**Groups** — require a minimum number of ratings from a set of scales before proceeding:

```yaml
groups:
  - id: "emotions"
    title: "Emotion Ratings"
    number_of_ratings: 3
    error_msg: "Please rate at least 3 emotions before continuing."

# Then on each scale in the group:
- active: true
  type: "discrete"
  title: "Joy"
  group: "emotions"
  required_to_proceed: false
```

---

### `config/page_texts.yaml`

Optional — override the text shown on welcome, consent, pre/post-familiarization, and completion pages. If the file is absent, built-in defaults are used.

---

## Running the App

```bash
uv run streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## Data

Ratings are saved to `user_ratings/{user_id}_{action_id}.json`. Each file includes the scale values, an `action_not_recognized` flag, and device info (`device_type`, `os`, `browser`, `browser_version`, `user_agent`) captured automatically from the participant's browser.

Export all ratings to CSV:

```bash
uv run python utils/export_to_csv.py
```

Output is written to `output/`.
