from typing import Dict, Any

# --- I18N LOCALIZATION ---
STRINGS: Dict[str, Dict[str, str]] = {
    "en": {
        # Main Menu & General
        "main_menu_title": "tmagent",
        "main_menu_prompt": "Choose an action:",
        "status_panel_title": "Status",
        "no_active_sessions": "No active tmate sessions found.",
        "create_session": "Create new session",
        "manage_session": "Manage existing session",
        "kill_all_sessions": "Kill all sessions",
        "settings": "Settings",
        "exit": "Exit",
        "goodbye": "Goodbye!",
        "user_exit_request": "\nExited by user request.",
        "external_session": "External session",
        "success": "Success",

        # Session Table
        "active_sessions_table_title": "Active tmate Sessions",
        "session_name_column": "Session Name",
        "socket_column": "Socket",
        "directory_column": "Directory",

        # Create Session
        "create_session_title": "Create New Session",
        "select_color_prompt": "Select a color for the session:",
        "select_ai_client_prompt": "Select an AI client:",
        "session_exists_error": "Error: Session with name '{session_name}' already exists.",
        "conflict_title": "Name Conflict",
        "specify_work_dir_prompt": "Specify the working directory for the agent (default: {default_dir}):",
        "invalid_directory_error": "Error: Directory '{working_dir}' does not exist.",
        "invalid_dir_title": "Invalid Directory",
        "starting_session_message": "\nStarting session [magenta]'{session_name}'[/magenta] with client [yellow]'{client_name}'[/yellow] in directory [cyan]'{working_dir}'[/cyan]...",
        "status_creating_session": "Creating tmate session...",
        "status_waiting_for_ready": "Waiting for session to be ready...",
        "status_getting_links": "Getting SSH links...",
        "link_problem_title": "Link Problem",
        "link_problem_message": "[red]Warning: Failed to get a valid Read-Write SSH link.[/red]\n[yellow]Check your network connection, firewall settings, and SSH keys.[/yellow]\n[cyan]To diagnose inside the tmate session, use the command: tmate show-messages[/cyan]",
        "connect_to_new_session_prompt": "Connect to the new session right away?",
        "session_running_in_bg": "Session '{session_name}' is running in the background.",
        "command_not_found_error": "Error: Command '{filename}' not found.\nMake sure it is installed and available in your PATH.",
        "command_not_found_title": "Command Not Found",
        "tmate_error_title": "tmate Error",
        "tmate_create_error": "Failed to create tmate session: {cmd}\nStdout: {stdout}\nStderr: {stderr}",
        "timeout_error_title": "Timeout",
        "tmate_timeout_error": "Error: Timed out waiting for tmate session to be ready.\n{e}",

        # Links & QR
        "links_panel_title": "SSH Connection Links",
        "read_write_panel_title": "Read-Write",
        "read_only_panel_title": "Read-Only",
        "qr_error_title": "QR Error",
        "qr_error_message": "Error generating QR code: {e}",
        "qr_unavailable": "QR code unavailable",

        # Manage Sessions
        "manage_sessions_title": "Manage Existing Sessions",
        "no_sessions_to_manage": "No active sessions to manage.",
        "no_sessions_title": "No Sessions",
        "select_session_to_manage": "Select a session to manage:",
        "action_for_session": "Action for [magenta]'{session_to_manage_name}'[/magenta] (Directory: [cyan]{session_path}[/cyan]):",
        "action_connect": "Connect",
        "action_show_links": "Show SSH links",
        "action_destroy": "Destroy session",
        "action_back": "Back",
        "connect_error_title": "Connection Error",
        "connect_error_message": "Failed to connect to session: {cmd}\nStdout: {stdout}\nStderr: {stderr}",
        "get_links_error_message": "Could not get links for this session. It might not be connected yet.",
        "get_links_error_title": "Link Error",
        "destroy_confirm": "Are you sure you want to destroy session [magenta]'{session_to_manage_name}'[/magenta]?",
        "session_destroyed_message": "Session '{session_to_manage_name}' destroyed.",
        "session_destroyed_title": "Session Destroyed",
        "destroy_error_title": "Destroy Error",
        "destroy_error_message": "Failed to destroy session: {cmd}\nStdout: {stdout}\nStderr: {stderr}",

        # Kill All
        "kill_all_title": "Destroy All Sessions",
        "no_sessions_to_kill": "No active sessions to destroy.",
        "kill_all_confirm": "Are you sure you want to destroy ALL active tmate sessions?",
        "status_killing_all": "Destroying all tmate sessions...",
        "all_sessions_killed": "All tmate sessions have been destroyed.",
        "kill_all_error_message": "Failed to execute 'killall tmate': {cmd}\nStdout: {stdout}\nStderr: {stderr}",
        "kill_all_error_title": "killall Error",
        "killall_not_found_error": "Command 'killall' not found. Make sure it is installed.",

        # AI Clients
        "ai_client_detect_error_title": "Client Detection Error",
        "ai_client_detect_error_message": "[bold red]Warning: No supported AI clients found in your system.[/bold red]\nMake sure 'gemini', 'claude', 'qwen', or 'opencode' are installed and available in your PATH.",
        "no_clients_available": "No clients available",
        "no_clients_warning_message": "[bold red]Warning: No supported AI clients found. The script will run, but without the ability to launch AI clients.[/bold red]",
        "no_clients_warning_title": "Warning",

        # Telegram
        "telegram_prompt": "Send session notification to Telegram?",
        "telegram_sent": "Telegram notification sent.",
        "telegram_panel_title": "Telegram",
        "telegram_send_not_found": "Command 'telegram-send' not found. Notification not sent.\n[cyan]To install, run: pip install telegram-send && telegram-send --configure[/cyan]",
        "telegram_error_title": "Telegram Error",
        "telegram_error_message": "Failed to send Telegram notification:\n{error_output}",
        "telegram_notification_message": "🚀 *New tmate session created!*\n\n🎨 *Session:* `{session_name}`\n📂 *Directory:* `{working_dir}`\n\n🔗 *Read-Write SSH:*\n`{read_write_link}`\n\n👁 *Read-Only SSH:*\n`{read_only_link}`",

        # Settings
        "settings_title": "Settings",
        "language_prompt": "Select interface language:",
        "language_changed": "Language changed successfully. Changes will take effect on restart.",
    }
}

CURRENT_LANG = "en"

def set_language(lang: str) -> None:
    """Sets the current language and updates the global variable."""
    global CURRENT_LANG
    CURRENT_LANG = lang

def t(key: str, **kwargs: Any) -> str:
    """
    Returns the translated string for the given key.
    Falls back to the key itself if the translation is not found.
    """
    lang_dict = STRINGS.get(CURRENT_LANG, STRINGS["en"])
    return lang_dict.get(key, key).format(**kwargs)
