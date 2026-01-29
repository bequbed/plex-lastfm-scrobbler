# Plex to Last.fm Scrobbler (Clean Metadata)

A lightweight Python/Flask server that listens for Plex Webhooks and scrobbles tracks to Last.fm. 

**The Problem:** Plex's built-in scrobbler often submits dirty tags (e.g., "Song (2011 Remaster)" or "Track [Live]").  
**The Solution:** This script intercepts the play, cleans the metadata using regex, and submits a pristine scrobble to Last.fm.

## Features
- 🧹 **Smart Metadata Cleaning:** Automatically removes "Remastered", "Deluxe Edition", "Stereo Mix", "feat. Artist", and other junk tags from song titles.
- 🎵 **Correct Hierarchy:** Properly parses `Grandparent` (Artist) and `Parent` (Album) from Plex payloads.
- 🚫 **Anti-Duplicate:** Only triggers a scrobble when the track hits 90% completion (`media.scrobble` event).
- 🤫 **Silent Mode:** Includes scripts to run silently in the background on Windows.

## Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/plex-lastfm-scrobbler.git](https://github.com/YOUR_USERNAME/plex-lastfm-scrobbler.git)
   cd plex-lastfm-scrobbler
Install dependencies:

Bash
pip install -r requirements.txt
Configuration:

Rename config.example.py to config.py.

Open config.py and paste your Last.fm API keys.

Don't have keys? Get them here: Last.fm API Account Creation

Usage
1. Start the Server
You can run the script manually to see the logs:

Bash
python scrobbler.py
Port 5000 must be open.

2. Configure Plex
Open your Plex Server settings.

Navigate to Webhooks (under Account).

Click Add Webhook and enter:

http://localhost:5000/plex_scrobble
(Note: If Plex is running on a different machine than this script, replace localhost with the script's IP address).

🪟 Windows Auto-Start (Background Service)
This repo includes helper scripts to run the scrobbler silently in the background on Windows.

Edit Paths:

Right-click run_scrobbler.bat and update the path to your folder.

Right-click start_silent.vbs and update the path to point to run_scrobbler.bat.

Test:

Double-click start_silent.vbs. It should run without opening a window.

Verify it is running by checking Task Manager for python.exe or running netstat -an | find "5000" in cmd.

Enable on Boot:

Press Win + R, type shell:startup, and hit Enter.

Create a shortcut to start_silent.vbs and drag it into this Startup folder.

Files
scrobbler.py: The main application logic.

config.example.py: Template for API keys (rename to config.py).

run_scrobbler.bat: Windows batch file launcher.

start_silent.vbs: Windows silent launcher (hides the console window).

License
MIT
