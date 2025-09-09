import pytest
import logging
import os
from pathlib import Path
from datetime import datetime
from prepdir.config import __version__

@pytest.fixture(autouse=True)
def reset_loggers():
    """Reset all prepdir-related loggers before each test."""
    loggers = [
        logging.getLogger("prepdir"),
        logging.getLogger("prepdir.config"),
        logging.getLogger("prepdir.prepdir_processor"),
        logging.getLogger("prepdir.prepdir_output_file"),
        logging.getLogger("prepdir.prepdir_file_entry"),
        logging.getLogger("prepdir.glob_translate"),
        logging.getLogger("prepdir.is_excluded_file"),
        logging.getLogger("prepdir.scrub_uuids"),
        logging.getLogger("dynaconf"),
    ]
    for logger in loggers:
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)
    yield

@pytest.fixture(autouse=True, scope="function")
def reset_env():
    """Reset key environment variables before each test."""
    env_keys = ["PREPDIR_SKIP_CONFIG_FILE_LOAD", "PREPDIR_SKIP_BUNDLED_CONFIG_LOAD", "HOME"]
    original_env = {key: os.environ.get(key) for key in env_keys}
    yield
    for key in env_keys:
        if original_env[key] is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_env[key]

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with sample files."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "file1.py").write_text(
        'print("Hello")\n# UUID: 123e4567-e89b-12d3-a456-426614174000\n', encoding="utf-8"
    )
    (project_dir / "file2.txt").write_text("Sample text\n", encoding="utf-8")
    (project_dir / "logs").mkdir()
    (project_dir / "logs" / "app.log").write_text("Log entry\n", encoding="utf-8")
    (project_dir / ".git").mkdir()
    (project_dir / "output.txt").write_text(
        f"File listing generated {datetime.now().isoformat()} by prepdir version {__version__}\n"
        f"Base directory is '{project_dir}'\n\n"
        "=-=-= Begin File: 'file1.py' =-=-=\n"
        'print("Hello")\n'
        "# UUID: PREPDIR_UUID_PLACEHOLDER_1\n"
        "=-=-= End File: 'file1.py' =-=-=\n",
        encoding="utf-8",
    )
    return project_dir