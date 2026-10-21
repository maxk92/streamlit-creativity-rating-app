"""
Upload videos (or a single file such as the metadata CSV) to the Cloudflare R2 bucket.
Reads the [r2] credentials from .streamlit/secrets.toml. Files that already
exist in the bucket with the same size are skipped, so re-running is cheap.

Usage:
    python utils/upload_to_r2.py data/video-set-2 video-set-2/
    python utils/upload_to_r2.py data/videos-famil videos-famil/
    python utils/upload_to_r2.py data/statsbomb_event_sample.csv metadata/
"""
import argparse
import mimetypes
import os
import sys
import tomllib

import boto3
from botocore.config import Config


def load_r2_secrets(secrets_path):
    with open(secrets_path, 'rb') as f:
        return tomllib.load(f)['r2']


def get_client(r2):
    return boto3.client(
        's3',
        endpoint_url=f"https://{r2['account_id']}.r2.cloudflarestorage.com",
        aws_access_key_id=r2['access_key_id'],
        aws_secret_access_key=r2['secret_access_key'],
        region_name='auto',
        config=Config(signature_version='s3v4'),
    )


def list_existing(client, bucket, prefix):
    """Return {key: size} for all objects under prefix."""
    existing = {}
    paginator = client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            existing[obj['Key']] = obj['Size']
    return existing


def main():
    parser = argparse.ArgumentParser(description='Upload files to Cloudflare R2.')
    parser.add_argument('source', help='Local directory (uploads all .mp4 files) or a single file')
    parser.add_argument('prefix', help='Key prefix in the bucket, e.g. "video-set-2/"')
    parser.add_argument('--secrets', default='.streamlit/secrets.toml', help='Path to secrets.toml')
    args = parser.parse_args()

    prefix = args.prefix if args.prefix.endswith('/') else args.prefix + '/'

    if os.path.isdir(args.source):
        files = sorted(
            os.path.join(args.source, f) for f in os.listdir(args.source)
            if f.lower().endswith('.mp4')
        )
    elif os.path.isfile(args.source):
        files = [args.source]
    else:
        sys.exit(f"[ERROR] Source not found: {args.source}")

    r2 = load_r2_secrets(args.secrets)
    client = get_client(r2)
    bucket = r2['bucket']
    existing = list_existing(client, bucket, prefix)

    uploaded = skipped = failed = 0
    for i, path in enumerate(files, 1):
        key = prefix + os.path.basename(path)
        if existing.get(key) == os.path.getsize(path):
            skipped += 1
            continue

        content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        try:
            client.upload_file(path, bucket, key, ExtraArgs={'ContentType': content_type})
            uploaded += 1
            print(f"[INFO] ({i}/{len(files)}) Uploaded {key}")
        except Exception as e:
            failed += 1
            print(f"[ERROR] ({i}/{len(files)}) Failed to upload {key}: {e}")

    print(f"\n[INFO] Done: {uploaded} uploaded, {skipped} skipped (already present), {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
