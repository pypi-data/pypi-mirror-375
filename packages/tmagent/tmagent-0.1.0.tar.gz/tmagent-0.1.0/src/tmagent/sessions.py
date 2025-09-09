import os
import glob
import subprocess  # nosec B404
from subprocess import PIPE, CalledProcessError, TimeoutExpired, DEVNULL
import shutil
import tempfile
from typing import List, Dict, Any, Optional

import questionary
from rich.status import Status
from rich.panel import Panel

from . import config
from . import display
from . import utils
from .i18n import t


def get_existing_sessions() -> List[Dict[str, Any]]:
    """
    Retrieves a list of active tmate sessions and their metadata.

    It checks for socket files in the temporary directory, verifies if the session is live,
    and cleans up stale session data from the configuration file.

    Returns:
        A list of dictionaries, where each dictionary represents an active session.
    """
    sessions_info: List[Dict[str, Any]] = []
    socket_files = glob.glob(os.path.join(tempfile.gettempdir(), "tmate-*.sock"))
    live_session_names: List[str] = []
    session_data = config.load_session_data()
    tmate_path = shutil.which("tmate")
    if not tmate_path:
        display.CONSOLE.print(Panel(t('tmate_not_found_error'), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
        return []

    for socket_path in socket_files:
        try:
            # Check if the session associated with the socket is actually running
            subprocess.run(  # nosec B603
                [tmate_path, "-S", socket_path, "has-session"],
                check=True, stdout=DEVNULL, stderr=DEVNULL
            )
            session_name = os.path.basename(socket_path).replace(".sock", "")
            live_session_names.append(session_name)
            
            # Get the working directory from our session data file
            session_path = session_data.get(session_name, t("external_session"))
            
            sessions_info.append({"name": session_name, "socket": socket_path, "path": session_path})
        except CalledProcessError:
            # If the tmate session is not running, remove the orphaned socket file
            if os.path.exists(socket_path):
                os.remove(socket_path)
        except FileNotFoundError:
            # If the tmate session is not running, remove the orphaned socket file
            if os.path.exists(socket_path):
                os.remove(socket_path)
    
    # Clean up session data for sessions that are no longer live
    stale_sessions = [name for name in session_data if name not in live_session_names]
    if stale_sessions:
        for name in stale_sessions:
            if name in session_data:
                del session_data[name]
        config.save_session_data(session_data)

    return sessions_info

def create_new_session(
    existing_sessions_info: List[Dict[str, Any]],
    available_ai_clients: Dict[str, List[str]],
    answers: Optional[Dict[str, Any]] = None
) -> None:
    """
    Interactively guides the user through creating a new tmate session.

    Args:
        existing_sessions_info: A list of currently active sessions to prevent name conflicts.
        available_ai_clients: A dictionary of detected AI clients the user can choose from.
        answers: A dictionary of pre-defined answers for non-interactive testing.
    """
    display.CONSOLE.rule(f"[bold green]{t('create_session_title')}[/bold green]")

    def ask(name: str, func, *args, **kwargs):
        if answers and name in answers:
            return answers[name]
        return func(*args, **kwargs).ask()

    color = ask("color", questionary.select, t('select_color_prompt'), choices=display.COLORS, use_shortcuts=True)
    if not color:
        return

    client_name = ask("client_name", questionary.select, t('select_ai_client_prompt'), choices=list(available_ai_clients.keys()), use_shortcuts=True)
    if not client_name:
        return

    send_notification = False
    if shutil.which("telegram-send"):
        send_notification = ask("send_notification", questionary.confirm, t('telegram_prompt'), default=False)

    session_name = f"tmate-{color}"
    socket = os.path.join(tempfile.gettempdir(), f"{session_name}.sock")
    
    existing_session_names = [s["name"] for s in existing_sessions_info]
    if session_name in existing_session_names:
        display.CONSOLE.print(Panel(t('session_exists_error', session_name=session_name), title=f"[red]{t('conflict_title')}[/red]", border_style="red"))
        return

    command_to_run = available_ai_clients[client_name]
    
    default_dir = os.getcwd()
    working_dir = ask("working_dir", questionary.text, t('specify_work_dir_prompt', default_dir=default_dir), default=default_dir)
    if not working_dir:
        working_dir = default_dir

    if not os.path.isdir(working_dir):
        display.CONSOLE.print(Panel(t('invalid_directory_error', working_dir=working_dir), title=f"[red]{t('invalid_dir_title')}[/red]", border_style="red"))
        return

    display.CONSOLE.print(t('starting_session_message', session_name=session_name, client_name=client_name, working_dir=working_dir))
    
    tmate_path = shutil.which("tmate")
    if not tmate_path:
        display.CONSOLE.print(Panel(t('tmate_not_found_error'), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
        return

    try:
        if os.path.exists(socket):
            os.remove(socket)

        tmate_command = [tmate_path, "-S", socket, "new-session", "-d", "-s", session_name, "-c", working_dir] + command_to_run
        
        with Status(f"[bold green]{t('status_creating_session')}[/bold green]", spinner="dots", console=display.CONSOLE) as status:
            subprocess.run(tmate_command, check=True, capture_output=True, text=True)  # nosec B603
            
            status.update(f"[bold green]{t('status_waiting_for_ready')}[/bold green]")
            subprocess.run([tmate_path, "-S", socket, "wait", "tmate-ready"], check=True, timeout=30)  # nosec B603
            
            status.update(f"[bold green]{t('status_getting_links')}[/bold green]")
            links = utils.get_session_links(socket)

            if links and links['read_write'] != "ssh":
                session_data = config.load_session_data()
                session_data[session_name] = working_dir
                config.save_session_data(session_data)
            else:
                display.CONSOLE.print(Panel(t("link_problem_message"), title=f"[red]{t('link_problem_title')}[/red]", border_style="red"))
            
            display.display_links_and_qrs(links)

            if links['read_write'] != "ssh" and send_notification:
                message = t(
                    "telegram_notification_message", 
                    session_name=session_name, 
                    working_dir=working_dir, 
                    read_write_link=links['read_write'], 
                    read_only_link=links['read_only']
                )
                utils.send_telegram_notification(message, use_markdown=True)

        connect_result = ask("connect", questionary.confirm, t('connect_to_new_session_prompt'), default=False)
        if connect_result:
            subprocess.run([tmate_path, "-S", socket, "attach"])  # nosec B603
        else:
            display.CONSOLE.print(f"[bold green]{t('session_running_in_bg', session_name=session_name)}[/bold green]")

    except FileNotFoundError as e:
        display.CONSOLE.print(Panel(t('command_not_found_error', filename=e.filename), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
    except CalledProcessError as e:
        display.CONSOLE.print(Panel(t('tmate_create_error', cmd=e.cmd, stdout=e.stdout, stderr=e.stderr), title=f"[red]{t('tmate_error_title')}[/red]", border_style="red"))
    except TimeoutExpired as e:
        display.CONSOLE.print(Panel(t('tmate_timeout_error', e=e), title=f"[red]{t('timeout_error_title')}[/red]", border_style="red"))

def manage_sessions(
    sessions_info: List[Dict[str, Any]],
    answers: Optional[Dict[str, Any]] = None
) -> None:
    """
    Provides a menu for managing an existing tmate session (connect, view links, destroy).

    Args:
        sessions_info: A list of currently active sessions.
        answers: A dictionary of pre-defined answers for non-interactive testing.
    """
    display.CONSOLE.rule(f"[bold blue]{t('manage_sessions_title')}[/bold blue]")
    if not sessions_info: 
        display.CONSOLE.print(Panel(f"[yellow]{t('no_sessions_to_manage')}[/yellow]", title=f"[yellow]{t('no_sessions_title')}[/yellow]", border_style="yellow"))
        return

    def ask(name: str, func, *args, **kwargs):
        if answers and name in answers:
            return answers[name]
        return func(*args, **kwargs).ask()

    session_names = [s["name"] for s in sessions_info]
    session_to_manage_name = ask("session_name", questionary.select, t('select_session_to_manage'), choices=session_names)
    if not session_to_manage_name:
        return

    selected_session = next((s for s in sessions_info if s["name"] == session_to_manage_name), None)
    if not selected_session:
        return 

    socket = selected_session["socket"]
    session_path = selected_session["path"]
    
    tmate_path = shutil.which("tmate")
    if not tmate_path:
        display.CONSOLE.print(Panel(t('tmate_not_found_error'), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
        return

    action = ask(
        "action",
        questionary.select,
        t('action_for_session', session_to_manage_name=session_to_manage_name, session_path=session_path),
        choices=[t('action_connect'), t('action_show_links'), t('action_destroy'), t('action_back')]
    )

    if action == t('action_connect'):
        try:
            subprocess.run([tmate_path, "-S", socket, "attach"], check=True)  # nosec B603
        except CalledProcessError as e:
            display.CONSOLE.print(Panel(t('connect_error_message', cmd=e.cmd, stdout=e.stdout, stderr=e.stderr), title=f"[red]{t('connect_error_title')}[/red]", border_style="red"))
    
    elif action == t('action_show_links'):
        links = utils.get_session_links(socket)
        if links and links['read_write'] != 'ssh':
            display.display_links_and_qrs(links)
        else:
            display.CONSOLE.print(Panel(t('get_links_error_message'), title=f"[red]{t('get_links_error_title')}[/red]", border_style="red"))
    
    elif action == t('action_destroy'):
        confirm_destroy = ask("confirm_destroy", questionary.confirm, t('destroy_confirm', session_to_manage_name=session_to_manage_name), default=False)
        if confirm_destroy:
            try:
                subprocess.run([tmate_path, "-S", socket, "kill-session"], check=True, capture_output=True, text=True)  # nosec B603
                display.CONSOLE.print(Panel(t('session_destroyed_message', session_to_manage_name=session_to_manage_name), title=f"[green]{t('session_destroyed_title')}[/green]", border_style="green"))
                
                session_data = config.load_session_data()
                if session_to_manage_name in session_data:
                    del session_data[session_to_manage_name]
                    config.save_session_data(session_data)

            except CalledProcessError as e:
                display.CONSOLE.print(Panel(t('destroy_error_message', cmd=e.cmd, stdout=e.stdout, stderr=e.stderr), title=f"[red]{t('destroy_error_title')}[/red]", border_style="red"))

def kill_all_sessions(
    sessions_info: List[Dict[str, Any]], 
    answers: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Destroys all active tmate sessions.

    Args:
        sessions_info: A list of currently active sessions.
        answers: A dictionary of pre-defined answers for non-interactive testing.
        
    Returns:
        True if sessions were successfully killed, False otherwise.
    """
    display.CONSOLE.rule(f"[bold red]{t('kill_all_title')}[/bold red]")
    if not sessions_info: 
        display.CONSOLE.print(Panel(f"[yellow]{t('no_sessions_to_kill')}[/yellow]", title=f"[yellow]{t('no_sessions_title')}[/yellow]", border_style="yellow"))
        return False

    def ask(name: str, func, *args, **kwargs):
        if answers and name in answers:
            return answers[name]
        return func(*args, **kwargs).ask()

    confirm_kill_all = ask("confirm_kill", questionary.confirm, t('kill_all_confirm'), default=False)
    if confirm_kill_all:
        killall_path = shutil.which("killall")
        if not killall_path:
            display.CONSOLE.print(Panel(t('killall_not_found_error'), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
            return False
        try:
            with Status(f"[bold red]{t('status_killing_all')}[/bold red]", spinner="dots", console=display.CONSOLE):
                subprocess.run([killall_path, "tmate"], check=True, stdout=PIPE, stderr=PIPE, text=True)  # nosec B603
            display.CONSOLE.print(Panel(f"[bold green]{t('all_sessions_killed')}[/bold green]", title=f"[green]{t('success')}[/green]", border_style="green"))
            config.save_session_data({})
            return True

        except CalledProcessError as e:
            display.CONSOLE.print(Panel(t('kill_all_error_message', cmd=e.cmd, stdout=e.stdout, stderr=e.stderr), title=f"[red]{t('kill_all_error_title')}[/red]", border_style="red"))
        except FileNotFoundError:
             display.CONSOLE.print(Panel(t('killall_not_found_error'), title=f"[red]{t('command_not_found_title')}[/red]", border_style="red"))
    return False