"""
Metadata loading for video events.
Supports CSV files (read fully) and DuckDB databases (only the rows for the
requested event IDs are queried from the 'events' table).
"""
import pandas as pd


def load_metadata(metadata_path, event_ids):
    """
    Load metadata for the given event IDs.

    Args:
        metadata_path: Path to a .csv or .duckdb file
        event_ids: List of event IDs (video filenames without .mp4)

    Returns:
        DataFrame with metadata (empty if loading fails)
    """
    try:
        if not metadata_path:
            print("[WARNING] No metadata path available, skipping metadata load")
            return pd.DataFrame()

        if metadata_path.endswith('.csv'):
            df_metadata = pd.read_csv(metadata_path)
            print(f"[INFO] Loaded {len(df_metadata)} metadata rows from CSV")
            return df_metadata

        if metadata_path.endswith('.duckdb'):
            # Lazy import so CSV-only setups don't need duckdb
            import duckdb
            conn = duckdb.connect(metadata_path, read_only=True)
            try:
                df_metadata = conn.execute(
                    "SELECT * FROM events WHERE id IN (SELECT unnest(?))",
                    [list(event_ids)]
                ).fetchdf()
            finally:
                conn.close()
            print(f"[INFO] Loaded {len(df_metadata)} metadata rows from DuckDB")
            return df_metadata

        print(f"[WARNING] Unsupported metadata file type: {metadata_path}")
    except Exception as e:
        print(f"[WARNING] Failed to load metadata: {e}")
    return pd.DataFrame()
