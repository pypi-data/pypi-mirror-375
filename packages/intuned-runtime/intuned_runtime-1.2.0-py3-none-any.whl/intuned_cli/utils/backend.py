import os


def get_base_url():
    return os.environ.get("INTUNED_API_BASE_URL") or os.environ.get("INTUNED_API_DOMAIN") or "https://app.intuned.io"
