"""
Cloudflare R2 manager for video file access.
R2 is S3-compatible, so boto3 is used. The bucket stays private; videos are
served to the browser via short-lived presigned URLs, so the Streamlit server
never downloads video files itself.
"""
import streamlit as st
import os
import time
import tempfile
import boto3
from botocore.config import Config

# Presigned URL lifetime and the age after which a cached URL is regenerated.
# URLs are cached per session so reruns (e.g. clicking a rating) keep the same
# URL and the video player does not reload.
_URL_EXPIRES_SECONDS = 7200
_URL_REFRESH_AFTER_SECONDS = 5400


@st.cache_resource
def get_r2_client():
    """
    Get or create a cached R2 (S3-compatible) client using st.secrets["r2"].

    Returns:
        boto3 S3 client
    """
    r2 = st.secrets["r2"]
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{r2['account_id']}.r2.cloudflarestorage.com",
        aws_access_key_id=r2["access_key_id"],
        aws_secret_access_key=r2["secret_access_key"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    print("[INFO] R2 client initialized")
    return client


def _bucket():
    return st.secrets["r2"]["bucket"]


def _key(prefix, filename):
    prefix = prefix or ""
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return f"{prefix}{filename}"


@st.cache_data(ttl=300, show_spinner=False)
def list_video_filenames(prefix):
    """
    List all .mp4 filenames under a prefix in the R2 bucket.

    Args:
        prefix: Key prefix ("folder") in the bucket, e.g. "video-set-2/"

    Returns:
        List of video filenames (basenames, without the prefix)
    """
    client = get_r2_client()
    paginator = client.get_paginator("list_objects_v2")
    filenames = []
    for page in paginator.paginate(Bucket=_bucket(), Prefix=_key(prefix, "")):
        for obj in page.get("Contents", []):
            name = os.path.basename(obj["Key"])
            if name.lower().endswith(".mp4"):
                filenames.append(name)
    print(f"[INFO] Found {len(filenames)} video files in R2 under '{prefix}'")
    return filenames


def get_video_url(prefix, filename):
    """
    Get a presigned URL for a video, cached in session state.

    Args:
        prefix: Key prefix in the bucket
        filename: Video filename

    Returns:
        Presigned HTTPS URL, or None if it could not be generated
    """
    key = _key(prefix, filename)
    cache = st.session_state.setdefault("r2_video_urls", {})
    cached = cache.get(key)
    if cached and time.time() - cached[1] < _URL_REFRESH_AFTER_SECONDS:
        return cached[0]

    try:
        url = get_r2_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": _bucket(), "Key": key},
            ExpiresIn=_URL_EXPIRES_SECONDS,
        )
    except Exception as e:
        print(f"[ERROR] Failed to create presigned URL for '{key}': {e}")
        return None

    cache[key] = (url, time.time())
    return url


@st.cache_data(show_spinner=False)
def _download_file_cached(key):
    # Cached until the app restarts (metadata files can be large).
    # Raises on failure so that failed downloads are not cached
    temp_dir = os.path.join(tempfile.gettempdir(), "r2_cache")
    os.makedirs(temp_dir, exist_ok=True)
    local_path = os.path.join(temp_dir, os.path.basename(key))
    get_r2_client().download_file(_bucket(), key, local_path)
    print(f"[INFO] Downloaded '{key}' from R2")
    return local_path


def download_file_to_temp(key):
    """
    Download a file (e.g. the metadata CSV) from R2 to a temporary location.

    Args:
        key: Object key in the bucket

    Returns:
        Local temp file path, or None if the download failed
    """
    try:
        return _download_file_cached(key)
    except Exception as e:
        print(f"[ERROR] Failed to download '{key}' from R2: {e}")
        return None
