
import sys

import questionary
from rich.panel import Panel

from . import sessions
from . import utils
from .display import CONSOLE, display_sessions_table
from .i18n import t


def main() -> None:
    """The main entry point and loop for the tmate interactive CLI."""
    try:
        available_ai_clients = utils.detect_ai_clients()
        if not available_ai_clients or (len(available_ai_clients) == 1 and t("no_clients_available") in available_ai_clients):
            CONSOLE.print(Panel(t("no_clients_warning_message"), title=f"[red]{t('no_clients_warning_title')}[/red]", border_style="red"))

        while True:
            CONSOLE.rule(f"[bold cyan]{t('main_menu_title')}[/bold cyan]")
            sessions_info = sessions.get_existing_sessions()
            
            if sessions_info:
                display_sessions_table(sessions_info)
            else:
                CONSOLE.print(Panel(f"[yellow]{t('no_active_sessions')}[/yellow]", title=f"[yellow]{t('status_panel_title')}[/yellow]", border_style="yellow"))

            # Create menu choices for better visual distinction
            menu_choices = [
                questionary.Choice(f"{t('create_session')}", value="create_session")
            ]
            if sessions_info:
                menu_choices.append(
                    questionary.Choice(f"{t('manage_session')}", value="manage_session")
                )
                menu_choices.append(
                    questionary.Choice(f"{t('kill_all_sessions')}", value="kill_all_sessions")
                )
            menu_choices.extend([
                questionary.Choice(f"{t('exit')}", value="exit")
            ])

            action = questionary.select(
                f"{t('main_menu_prompt')}",
                choices=menu_choices,
                use_shortcuts=True
            ).ask()

            if not action or action == "exit":
                CONSOLE.print(f"[bold]{t('goodbye')}[/bold]")
                break
            
            elif action == "create_session":
                sessions.create_new_session(sessions_info, available_ai_clients)

            elif action == "manage_session":
                sessions.manage_sessions(sessions_info)

            elif action == "kill_all_sessions":
                sessions_killed = sessions.kill_all_sessions(sessions_info)
                # If sessions were killed, automatically return to the main menu without asking
                if sessions_killed:
                    continue

            # Automatically return to the main menu after any action
            # No need to ask the user if they want to return
            if action != "exit":
                CONSOLE.rule(style="dim") 
                # Just continue to the next loop iteration to show the main menu again

    except KeyboardInterrupt:
        print(t('user_exit_request'))
        sys.exit(0)

if __name__ == "__main__":
    main()
