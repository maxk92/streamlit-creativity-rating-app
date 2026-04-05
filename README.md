# Streamlit Rating App

A web application for collecting subjective ratings of video clips. Participants watch short video clips and rate them on configurable dimensions. Built with Streamlit; supports local and Google Sheets/Drive storage.

---

## Installation

Requires Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd 4_streamlit-rating-app
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
  metadata_path: "data/events.duckdb"   # DuckDB (.duckdb) or CSV (.csv)

  # Video source: "local" or "gdrive"
  video_source: "local"
  video_path: "data/videos/"            # used when video_source = "local"
  familiarization_video_path: "data/videos_familiarization/"

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
  # "online" — Google Sheets + Google Drive (requires secrets.toml)
  # "both"   — write to all locations
  storage_mode: "local"
```

**Google Drive / Sheets** (when `video_source: "gdrive"` or `storage_mode: "online"`): add credentials to `.streamlit/secrets.toml`. See [Streamlit secrets docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

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
