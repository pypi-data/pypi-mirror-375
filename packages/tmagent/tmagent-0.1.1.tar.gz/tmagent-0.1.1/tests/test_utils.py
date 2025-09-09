import subprocess
from unittest.mock import patch, MagicMock

from tmagent import utils

def test_generate_random_suffix():
    """Test the random suffix generation."""
    suffix = utils.generate_random_suffix(6)
    assert len(suffix) == 6
    assert suffix.isalnum()

@patch('shutil.which')
def test_detect_ai_clients_found(mock_which):
    """Test AI client detection when clients are found."""
    # Simulate that 'gemini' and 'claude' executables are found
    mock_which.side_effect = lambda x: x if x in ['gemini', 'claude'] else None
    
    clients = utils.detect_ai_clients()
    
    assert "Gemini (Pro)" in clients
    assert "Claude" in clients
    assert "Qwen" not in clients
    assert clients["Gemini (Pro)"] == ["gemini", "--model", "gemini-pro"]

@patch('shutil.which')
def test_detect_ai_clients_not_found(mock_which):
    """Test AI client detection when no clients are found."""
    # Simulate that no executables are found
    mock_which.return_value = None
    
    clients = utils.detect_ai_clients()
    
    assert "No clients available" in clients
    assert len(clients) == 1

@patch('subprocess.run')
@patch('shutil.which')
def test_get_session_links_success(mock_which, mock_run):
    """Test getting session links successfully."""
    # Mock the subprocess calls to tmate
    mock_which.return_value = '/usr/bin/tmate'
    mock_rw = MagicMock()
    mock_rw.stdout = "ssh rw_link@example.com"
    mock_ro = MagicMock()
    mock_ro.stdout = "ssh ro_link@example.com"
    
    mock_run.side_effect = [mock_rw, mock_ro]
    
    links = utils.get_session_links("somesocket")
    
    assert links["read_write"] == "ssh rw_link@example.com"
    assert links["read_only"] == "ssh ro_link@example.com"
    assert mock_run.call_count == 2

@patch('subprocess.run')
@patch('shutil.which')
def test_get_session_links_failure(mock_which, mock_run):
    """Test getting session links when the tmate command fails."""
    # Simulate a CalledProcessError
    mock_which.return_value = '/usr/bin/tmate'
    mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
    
    links = utils.get_session_links("somesocket")
    
    assert links["read_write"] == "ssh"
    assert links["read_only"] == utils.t("qr_unavailable")

def test_generate_qr_code_ascii():
    """Test generating a QR code."""
    qr_string = utils.generate_qr_code_ascii("test_data")
    assert isinstance(qr_string, str)
    assert "test_data" not in qr_string # The data itself is not in the ascii output
    assert len(qr_string) > 10