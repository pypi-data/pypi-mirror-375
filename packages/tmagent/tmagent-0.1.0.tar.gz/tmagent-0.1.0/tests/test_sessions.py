from subprocess import PIPE, CalledProcessError
from unittest.mock import patch, MagicMock

from tmagent import sessions


@patch('tmagent.sessions.config')
@patch('tmagent.sessions.glob')
@patch('tmagent.sessions.subprocess')
@patch('tmagent.sessions.os')
@patch('shutil.which')
def test_get_existing_sessions(mock_which, mock_os, mock_subprocess, mock_glob, mock_config):
    """Test retrieving existing tmate sessions."""
    # Arrange
    mock_which.return_value = '/usr/bin/tmate'
    mock_glob.glob.return_value = ['/tmp/tmate-blue.sock', '/tmp/tmate-red.sock']
    mock_os.path.basename.side_effect = lambda p: p.split('/')[-1]
    mock_os.path.exists.return_value = True
    
    # Simulate that one session is live and one is dead
    def has_session_effect(*args, **kwargs):
        if any('tmate-blue.sock' in arg for arg in args[0]):
            return MagicMock(returncode=0)
        else:
            raise CalledProcessError(1, 'cmd')
    mock_subprocess.run.side_effect = has_session_effect
    
    mock_config.load_session_data.return_value = {
        "tmate-blue": "/path/to/blue",
        "tmate-red": "/path/to/red", # Stale session
    }

    # Act
    existing_sessions = sessions.get_existing_sessions()

    # Assert
    assert len(existing_sessions) == 1
    assert existing_sessions[0]["name"] == "tmate-blue"
    assert existing_sessions[0]["path"] == "/path/to/blue"
    
    # Check that the stale session was removed
    mock_os.remove.assert_called_with('/tmp/tmate-red.sock')
    mock_config.save_session_data.assert_called_with({"tmate-blue": "/path/to/blue"})


@patch('tmagent.sessions.config')
@patch('tmagent.sessions.utils')
@patch('tmagent.sessions.display')
@patch('tmagent.sessions.subprocess')
@patch('tmagent.sessions.shutil')
@patch('tmagent.sessions.os')
@patch('tempfile.gettempdir')
def test_create_new_session(mock_gettempdir, mock_os, mock_shutil, mock_subprocess, mock_display, mock_utils, mock_config):
    """Test the successful creation of a new session."""
    # Arrange
    mock_gettempdir.return_value = '/tmp'
    mock_os.path.join.side_effect = lambda *args: "/".join(args)
    mock_os.path.isdir.return_value = True
    mock_os.getcwd.return_value = "/current/dir"
    mock_shutil.which.side_effect = lambda x: f'/usr/bin/{x}' # Assume all executables exist
    mock_utils.get_session_links.return_value = {"read_write": "ssh rw_link", "read_only": "ssh ro_link"}
    mock_config.load_session_data.return_value = {}

    answers = {
        "color": "green",
        "client_name": "Gemini (Pro)",
        "send_notification": True,
        "working_dir": "/test/dir",
        "connect": False,
    }

    available_clients = {"Gemini (Pro)": ["gemini"]}

    # Act
    sessions.create_new_session([], available_clients, answers=answers)

    # Assert
    # 1. Check that the tmate command was constructed and run correctly
    tmate_command_args = mock_subprocess.run.call_args_list[0].args[0]
    assert tmate_command_args == ["/usr/bin/tmate", "-S", "/tmp/tmate-green.sock", "new-session", "-d", "-s", "tmate-green", "-c", "/test/dir", "gemini"]
    
    # 2. Check that session data was saved
    mock_config.save_session_data.assert_called_with({"tmate-green": "/test/dir"})

    # 3. Check that links were displayed
    mock_display.display_links_and_qrs.assert_called_once()

    # 4. Check that Telegram notification was sent
    mock_utils.send_telegram_notification.assert_called_once()


@patch('tmagent.sessions.config')
@patch('tmagent.sessions.utils')
@patch('tmagent.sessions.display')
@patch('tmagent.sessions.subprocess')
@patch('shutil.which')
def test_manage_session_destroy(mock_which, mock_subprocess, mock_display, mock_utils, mock_config):
    """Test destroying a session via the manage menu."""
    # Arrange
    mock_which.return_value = '/usr/bin/tmate'
    mock_config.load_session_data.return_value = {"tmate-blue": "/path/to/blue"}
    sessions_info = [
        {"name": "tmate-blue", "socket": "/tmp/tmate-blue.sock", "path": "/path/to/blue"}
    ]
    answers = {
        "session_name": "tmate-blue",
        "action": sessions.t('action_destroy'),
        "confirm_destroy": True
    }

    # Act
    sessions.manage_sessions(sessions_info, answers=answers)

    # Assert
    # 1. Check that the kill-session command was called
    kill_command_args = mock_subprocess.run.call_args.args[0]
    assert kill_command_args == ["/usr/bin/tmate", "-S", "/tmp/tmate-blue.sock", "kill-session"]

    # 2. Check that the session was removed from config
    mock_config.save_session_data.assert_called_with({})


@patch('tmagent.sessions.config')
@patch('tmagent.sessions.subprocess')
@patch('shutil.which')
def test_kill_all_sessions(mock_which, mock_subprocess, mock_config):
    """Test the 'kill all' functionality."""
    # Arrange
    mock_which.return_value = '/usr/bin/killall'
    sessions_info = [
        {"name": "tmate-blue", "socket": "/tmp/tmate-blue.sock", "path": "/path/to/blue"}
    ]
    answers = {
        "confirm_kill": True
    }

    # Act
    sessions.kill_all_sessions(sessions_info, answers=answers)

    # Assert
    # 1. Check that 'killall tmate' was called
    mock_subprocess.run.assert_any_call(["/usr/bin/killall", "tmate"], check=True, stdout=PIPE, stderr=PIPE, text=True)

    # 2. Check that session data was cleared
    mock_config.save_session_data.assert_called_with({})