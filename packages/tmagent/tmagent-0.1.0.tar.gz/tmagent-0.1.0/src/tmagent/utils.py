import subprocess  # nosec B404
from subprocess import CalledProcessError, TimeoutExpired
import shutil
import secrets
import string
from io import StringIO
from typing import Dict, List, Optional

import qrcode
from rich.console import Console
from rich.panel import Panel

from .i18n import t

CONSOLE = Console()

def generate_random_suffix(length: int = 4) -> str:
    """
    Generates a random alphanumeric suffix of a given length.

    Args:
        length: The desired length of the suffix.

    Returns:
        A random alphanumeric string.
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def detect_ai_clients() -> Dict[str, List[str]]:
    """
    Automatically detects available AI client executables in the system's PATH.

    Returns:
        A dictionary mapping descriptive client names to their command arguments.
        If no clients are found, it returns a placeholder entry.
    """
    detected_clients: Dict[str, List[str]] = {}
    known_executables = {
        "gemini": {
            "Gemini (Pro)": ["gemini", "--model", "gemini-pro"],
            "Gemini (Flash)": ["gemini", "--model", "gemini-flash"],
        },
        "claude": {"Claude": ["claude"]},
        "qwen": {"Qwen": ["qwen"]},
        "opencode": {"Opencode": ["opencode"]},
    }

    for exe, client_configs in known_executables.items():
        if shutil.which(exe):
            detected_clients.update(client_configs)

    if not detected_clients:
        CONSOLE.print(
            Panel(
                t("ai_client_detect_error_message"),
                title=f"[red]{t('ai_client_detect_error_title')}[/red]",
                border_style="red",
            )
        )
        detected_clients[t("no_clients_available")] = ["echo", t("no_clients_available")]

    return detected_clients

def get_session_links(socket: str) -> Dict[str, str]:
    """
    Retrieves read-write and read-only SSH links for a given tmate session socket.

    Args:
        socket: The path to the tmate session socket.

    Returns:
        A dictionary with 'read_write' and 'read_only' SSH links.
        Returns placeholders if links cannot be retrieved.
    """
    tmate_path = shutil.which("tmate")
    if not tmate_path:
        return {"read_write": "ssh", "read_only": t("qr_unavailable")}
    try:
        rw_result = subprocess.run(  # nosec B603
            [tmate_path, "-S", socket, "display", "-p", "#{tmate_ssh}"],
            capture_output=True, text=True, check=True, timeout=25
        )
        ro_result = subprocess.run(  # nosec B603
            [tmate_path, "-S", socket, "display", "-p", "#{tmate_ssh_ro}"],
            capture_output=True, text=True, check=True, timeout=25
        )
        
        rw_link = rw_result.stdout.strip()
        ro_link = ro_result.stdout.strip()

        return {
            "read_write": rw_link if rw_link else "ssh",
            "read_only": ro_link if ro_link else t("qr_unavailable")
        }
    except (CalledProcessError, TimeoutExpired, FileNotFoundError):
        return {"read_write": "ssh", "read_only": t("qr_unavailable")}

def generate_qr_code_ascii(data: str) -> Optional[str]:
    """
    Generates a QR code and returns it as an ASCII string.

    Args:
        data: The string data to encode in the QR code.

    Returns:
        An ASCII string representing the QR code, or None if generation fails.
    """
    try:
        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make(fit=True)
        
        buffer = StringIO()
        qr.print_ascii(out=buffer, invert=True)
        return buffer.getvalue()
    except Exception as e:
        CONSOLE.print(
            Panel(
                f"[bold red]{t('qr_error_message', e=e)}[/bold red]",
                title=f"[red]{t('qr_error_title')}[/red]",
                border_style="red"
            )
        )
        return None

def send_telegram_notification(message: str, use_markdown: bool = False) -> None:
    """
    Sends a notification to Telegram using HTTP API requests.
    Telegram notification is sent only if both TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID 
    environment variables are set and not empty.

    Args:
        message: The message content to send.
        use_markdown: Whether to format the message as Markdown.
    """
    import os
    import requests
    
    # Get Telegram credentials from environment variables
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    # Check if both environment variables are set and not empty
    if not telegram_bot_token or not telegram_chat_id:
        # If either token or chat ID is not set, silently skip sending notification
        return
    
    # Telegram API endpoint for sending messages
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    
    # Prepare the message data
    data = {
        "chat_id": telegram_chat_id,
        "text": message,
        "disable_web_page_preview": True
    }
    
    # Set parse mode if markdown is requested
    if use_markdown:
        data["parse_mode"] = "Markdown"
    
    try:
        # Send the HTTP request
        response = requests.post(url, data=data, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        CONSOLE.print(
            Panel(
                f"[bold green]{t('telegram_sent')}[/bold green]",
                title=f"[green]{t('telegram_panel_title')}[/green]",
                border_style="green"
            )
        )
    except requests.exceptions.RequestException as e:
        error_output = str(e)
        CONSOLE.print(
            Panel(
                t('telegram_error_message', error_output=error_output),
                title=f"[red]{t('telegram_error_title')}[/red]",
                border_style="red"
            )
        )
    except Exception as e:
        error_output = str(e)
        CONSOLE.print(
            Panel(
                t('telegram_error_message', error_output=error_output),
                title=f"[red]{t('telegram_error_title')}[/red]",
                border_style="red"
            )
        )