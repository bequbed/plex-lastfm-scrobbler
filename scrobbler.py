import json
import logging
import os
import re
import time

import pylast
from flask import Flask, request, Response

# --- IMPORT CONFIG ---
def load_config():
    try:
        import config
        return {
            "api_key": config.LASTFM_API_KEY,
            "api_secret": config.LASTFM_API_SECRET,
            "username": config.LASTFM_USERNAME,
            "password": config.LASTFM_PASSWORD,
            "source": "config.py",
        }
    except ImportError:
        required = [
            "LASTFM_API_KEY",
            "LASTFM_API_SECRET",
            "LASTFM_USERNAME",
            "LASTFM_PASSWORD",
        ]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            missing_list = ", ".join(missing)
            print(
                "Error: config.py not found and missing environment variables: "
                f"{missing_list}"
            )
            exit(1)
        return {
            "api_key": os.getenv("LASTFM_API_KEY"),
            "api_secret": os.getenv("LASTFM_API_SECRET"),
            "username": os.getenv("LASTFM_USERNAME"),
            "password": os.getenv("LASTFM_PASSWORD"),
            "source": "environment",
        }


config_values = load_config()

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# --- INITIALIZE LAST.FM ---
try:
    # We hash the password here so it's not stored in plain text in memory longer than needed
    password_hash = pylast.md5(config_values["password"])

    network = pylast.LastFMNetwork(
        api_key=config_values["api_key"],
        api_secret=config_values["api_secret"],
        username=config_values["username"],
        password_hash=password_hash,
    )
    logger.info(
        "Connected to Last.fm successfully using %s.", config_values["source"]
    )
except Exception as e:
    logger.error(f"Failed to connect to Last.fm: {e}")
    exit(1)

app = Flask(__name__)

# --- CLEANING LOGIC ---
def clean_metadata(text):
    if not text: return ""
    
    # 1. Remove content within brackets/parentheses often containing junk
    # e.g., "Song (Remastered 2009)", "Title [Live at...]"
    junk_triggers = [
        "Remaster", "Live", "Mono", "Stereo", "Mix", "Version", 
        "Edit", "Deluxe", "Expanded", "Anniversary", "feat", "ft\\."
    ]
    
    pattern = r"\s*[\[\(].*?(" + "|".join(junk_triggers) + r").*?[\]\)]"
    cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Remove standard suffixes that aren't always in brackets
    # e.g. "Song - Remastered" or "Song feat. Jay-Z"
    suffix_patterns = [
        r"\s-\s.*Remaster.*",
        r"\s-\s.*Live.*",
        r"\s(feat\.|ft\.).*" 
    ]
    
    for pat in suffix_patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()

# --- FLASK ROUTE ---
@app.route('/plex_scrobble', methods=['POST'])
def plex_webhook():
    # Plex sends a multipart form with a 'payload' JSON field
    if 'payload' not in request.form:
        return Response("No payload found", status=400)

    try:
        data = json.loads(request.form['payload'])
    except json.JSONDecodeError:
        return Response("Invalid JSON", status=400)

    # Filter: Only act on 'media.scrobble' (90% played)
    event = data.get('event')
    if event != 'media.scrobble':
        # We ignore play/pause/resume events to save API calls
        return Response("Event ignored", status=200)

    metadata = data.get('Metadata', {})

    # Filter: Only act on music tracks
    if metadata.get('type') != 'track':
        return Response("Not a music track", status=200)

    # Extract Metadata (Plex structure: Grandparent=Artist, Parent=Album)
    raw_artist = metadata.get('grandparentTitle', 'Unknown Artist')
    raw_track = metadata.get('title', 'Unknown Track')
    raw_album = metadata.get('parentTitle', '')

    # Clean Metadata
    clean_artist = clean_metadata(raw_artist)
    clean_track = clean_metadata(raw_track)
    clean_album = clean_metadata(raw_album)

    logger.info(f"Scrobbling: {clean_artist} - {clean_track} (Album: {clean_album})")

    try:
        network.scrobble(
            artist=clean_artist,
            title=clean_track,
            album=clean_album,
            timestamp=int(time.time())
        )
        logger.info("-> Scrobble Success")
    except Exception as e:
        logger.error(f"-> Scrobble Failed: {e}")

    return Response("OK", status=200)

if __name__ == '__main__':
    print("Plex Scrobbler Listening on port 5000...")
    app.run(host='0.0.0.0', port=5000)
