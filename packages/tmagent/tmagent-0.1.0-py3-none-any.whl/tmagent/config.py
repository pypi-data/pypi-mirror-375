
import os
import json
from typing import Dict, Any

# --- CONFIGURATION ---
CONFIG_DIR = os.path.expanduser("~/.config/tmate_interactive_cli")
SESSIONS_FILE = os.path.join(CONFIG_DIR, "sessions.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "cli_settings.json")

def ensure_config_dir() -> None:
    """Ensures the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_settings() -> Dict[str, Any]:
    """
    Loads CLI settings from the JSON file.
    Defaults to Russian if the file doesn't exist or is invalid.
    """
    ensure_config_dir()
    if not os.path.exists(SETTINGS_FILE):
        return {"language": "ru"}  # Default to Russian
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            # Handle empty file case
            if os.path.getsize(SETTINGS_FILE) == 0:
                return {"language": "ru"}
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"language": "ru"}

def save_settings(data: Dict[str, Any]) -> None:
    """Saves CLI settings to the JSON file."""
    ensure_config_dir()
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_session_data() -> Dict[str, Any]:
    """
    Loads session data from the JSON file.
    Returns an empty dictionary if the file doesn't exist or is invalid.
    """
    ensure_config_dir()
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            if os.path.getsize(SESSIONS_FILE) == 0:
                return {}
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_session_data(data: Dict[str, Any]) -> None:
    """Saves session data to the JSON file."""
    ensure_config_dir()
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Load settings once at startup
APP_SETTINGS = load_settings()
