from typing import Dict, List, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from .i18n import t
from .utils import generate_qr_code_ascii

# --- UI CONSTANTS ---
COLORS = ['red', 'blue', 'green', 'yellow', 'magenta', 'cyan', 'white']
CONSOLE = Console()

def display_sessions_table(sessions_info: List[Dict[str, Any]]) -> None:
    """
    Displays active tmate sessions in a formatted table.

    Args:
        sessions_info: A list of dictionaries, each representing an active session.
    """
    table = Table(title=f"[bold blue]{t('active_sessions_table_title')}[/bold blue]")
    table.add_column(f"{t('session_name_column')}", style="magenta")
    table.add_column(f"{t('socket_column')}", style="green")
    table.add_column(f"{t('directory_column')}", style="cyan")

    for session in sessions_info:
        table.add_row(session["name"], session["socket"], session["path"])
    CONSOLE.print(table)

def display_links_and_qrs(links: Dict[str, str]) -> None:
    """
    Displays SSH connection links and their corresponding QR codes side-by-side.

    Args:
        links: A dictionary containing 'read_write' and 'read_only' SSH links.
    """
    CONSOLE.print(Panel(f"[bold green]{t('links_panel_title')}[/bold green]", border_style="green"))

    rw_qr_ascii = generate_qr_code_ascii(links['read_write'])
    ro_qr_ascii = generate_qr_code_ascii(links['read_only'])

    rw_link_text = Text(links['read_write'], style="red")
    ro_link_text = Text(links['read_only'], style="yellow")

    rw_content = Panel(
        Text("Read-Write:", style="bold") + Text.assemble(" ", rw_link_text) + Text("\n") + Text(rw_qr_ascii or f"[red]{t('qr_unavailable')}[/red]"),
        title=f"[bold red]{t('read_write_panel_title')}[/bold red]", border_style="red"
    )
    ro_content = Panel(
        Text("Read-Only:", style="bold") + Text.assemble(" ", ro_link_text) + Text("\n") + Text(ro_qr_ascii or f"[red]{t('qr_unavailable')}[/red]"),
        title=f"[bold yellow]{t('read_only_panel_title')}[/bold yellow]", border_style="yellow"
    )

    CONSOLE.print(Columns([rw_content, ro_content]))