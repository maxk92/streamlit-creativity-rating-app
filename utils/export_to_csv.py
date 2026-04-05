"""
Export ratings and user data to CSV files.
Adapted from write_ratings2csv.py in the original Kivy app.
"""
import json
import shutil
import pandas as pd
import os
from datetime import datetime

def load_json_files_with_datetime(path, file_type='ratings'):
    """
    Load all JSON files from a directory and add creation datetime.

    Parameters:
    - path: directory path containing JSON files
    - file_type: string to identify the type of data (for column naming)

    Returns:
    - DataFrame with all records and file_created_at column
    """
    all_data = []

    if not os.path.exists(path):
        return pd.DataFrame()

    for filename in os.listdir(path):
        if filename.endswith('.json'):
            filepath = os.path.join(path, filename)

            # Get file modification time
            modification_time = os.path.getmtime(filepath)
            creation_datetime = datetime.fromtimestamp(modification_time)

            # Load JSON file
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Handle both single dict and list of dicts
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                data = [{'content': data}]

            # Add metadata to each record
            for record in data:
                record['file_created_at'] = creation_datetime
                record['filename'] = filename

            all_data.extend(data)

    df = pd.DataFrame(all_data)
    return df

def export_all_data():
    """
    Export all ratings and user data to CSV files.
    Creates output directory and backup of JSON files.
    """
    userdata_path = 'user_data/'
    ratings_path = 'user_ratings/'
    output_path = 'output/'

    # Create output directory
    os.makedirs(output_path, exist_ok=True)

    # Load ratings
    df_ratings = load_json_files_with_datetime(ratings_path, 'ratings')

    if not df_ratings.empty:
        df_ratings.to_csv(f'{output_path}ratings.csv', index=False)
        print(f"Loaded {len(df_ratings)} ratings from {df_ratings['filename'].nunique()} files")
        print(f"Number of rated actions: {df_ratings['id'].nunique()}")

        # Dynamically identify scale columns
        metadata_columns = ['user_id', 'id', 'file_created_at', 'filename']
        all_columns = df_ratings.columns.tolist()
        scale_columns = [col for col in all_columns if col not in metadata_columns]

        print(f"Detected scale columns: {scale_columns}")

        # Build dynamic aggregation dictionary
        agg_dict = {}

        # Add count using the first scale column (or 'id' if no scales found)
        count_column = scale_columns[0] if scale_columns else 'id'
        agg_dict['num_ratings'] = (count_column, 'count')

        # Add mean and std for each scale column
        for scale_col in scale_columns:
            agg_dict[f'mean_{scale_col}'] = (scale_col, 'mean')
            agg_dict[f'std_{scale_col}'] = (scale_col, 'std')

        # Store mean ratings per action
        df_mean_ratings = df_ratings.groupby('id').agg(**agg_dict).round(3)
        df_mean_ratings.to_csv(f'{output_path}mean_ratings.csv')
    else:
        print("No ratings data found")

    # Load user data
    df_users = load_json_files_with_datetime(userdata_path, 'users')

    if not df_users.empty:
        df_users.to_csv(f'{output_path}users.csv', index=False)
        print(f"\nLoaded {len(df_users)} user records from {df_users['filename'].nunique()} files")
        print(f"Number of unique users: {df_users['user_id'].nunique()}")
    else:
        print("No user data found")

    # Generate log file with statistics
    if not df_ratings.empty:
        log_path = f'{output_path}rating_log.txt'
        with open(log_path, 'w') as log_file:
            log_file.write("=" * 60 + "\n")
            log_file.write("CREATIVITY RATING APP - DATA EXPORT LOG\n")
            log_file.write("=" * 60 + "\n")
            log_file.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 1. Number of unique actions rated
            num_unique_actions = df_ratings['id'].nunique()
            log_file.write(f"Number of unique actions rated: {num_unique_actions}\n\n")

            # 2. Number of raters involved
            if not df_users.empty:
                num_unique_raters = df_users['user_id'].nunique()
                log_file.write(f"Number of raters involved: {num_unique_raters}\n\n")

            # 3. Rating frequency distribution
            id_rating_counts = df_ratings['id'].value_counts()
            rating_frequency_distribution = id_rating_counts.value_counts().sort_index()

            log_file.write("Rating frequency distribution:\n")
            log_file.write("-" * 40 + "\n")
            log_file.write(f"{'Times Rated':<15} {'Number of Actions':<20}\n")
            log_file.write("-" * 40 + "\n")
            for times_rated, num_actions in rating_frequency_distribution.items():
                log_file.write(f"{times_rated:<15} {num_actions:<20}\n")

            log_file.write("\n" + "=" * 60 + "\n")

        print(f"\n[INFO] Log file created: {log_path}")

    # Backup JSON files
    os.makedirs('backup/user_data/', exist_ok=True)
    os.makedirs('backup/user_ratings/', exist_ok=True)

    if os.path.exists(userdata_path):
        for filename in os.listdir(userdata_path):
            if filename.endswith('.json'):
                shutil.copy(
                    os.path.join(userdata_path, filename),
                    os.path.join('backup/user_data/', filename)
                )

    if os.path.exists(ratings_path):
        for filename in os.listdir(ratings_path):
            if filename.endswith('.json'):
                shutil.copy(
                    os.path.join(ratings_path, filename),
                    os.path.join('backup/user_ratings/', filename)
                )

    print("\n[INFO] Backup of JSON files completed.")
    print("[INFO] Export completed successfully!")

if __name__ == '__main__':
    export_all_data()
