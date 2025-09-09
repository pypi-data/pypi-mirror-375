import pytest
import os
from sqlalembic.core.config import Config, ConfigurationError
from sqlalembic.core.config import DEFAULTS

@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture to create a temporary TOML configuration file."""
    config_content = """
[database]
DB_ENGINE = "sqlite"
DB_NAME = "test_db.db"

[migration]
MIGRATION_DIR = "test_migrations"
"""
    config_file = tmp_path / "sqlalembic.toml"
    config_file.write_text(config_content)
    return str(config_file)

@pytest.fixture
def temp_invalid_config_file(tmp_path):
    """Fixture to create a temporary invalid configuration file."""
    invalid_content = "{ this is invalid toml"
    config_file = tmp_path / "invalid_config.toml"
    config_file.write_text(invalid_content)
    return str(config_file)

@pytest.fixture(autouse=True)
def cleanup_env_vars():
    """Fixture to clean up environment variables after each test."""
    original_environ = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_environ)

def test_config_loads_from_file(temp_config_file):
    """Test that configuration is loaded correctly from a TOML file."""
    config = Config(config_file=temp_config_file)
    assert config.database.engine == "sqlite"
    assert config.DB_ENGINE == "sqlite"
    assert config.migration.directory == "test_migrations"

def test_env_variables_have_priority(temp_config_file):
    """Test that environment variables override file settings."""
    os.environ["DB_ENGINE"] = "postgresql"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_NAME"] = "testdb"
    os.environ["DB_USER"] = "test_user"
    
    config = Config(config_file=temp_config_file)
    assert config.database.engine == "postgresql"
    assert config.DB_ENGINE == "postgresql"
    assert config.database.host == "localhost"
    assert config.database.database == "testdb"
    assert config.database.user == "test_user"

def test_config_with_no_file_or_env_vars():
    """Test that the object uses default values when no file or env vars are found."""
    config = Config(config_file=None)
    assert config.DB_ENGINE == DEFAULTS["DB_ENGINE"].lower()
    assert config.database.engine == "sqlite"
    assert config.migration.directory == "alembic"

def test_no_config_file_uses_defaults(tmp_path):
    """Test that the application correctly falls back to defaults when no config file is found."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = Config(load_env=False)
        assert config.DB_ENGINE == "sqlite"
        assert config.migration.directory == "alembic"
    finally:
        os.chdir(original_cwd)

def test_invalid_config_file_raises_error(temp_invalid_config_file):
    """Test that an invalid configuration file raises a ConfigurationError."""
    with pytest.raises(ConfigurationError):
        Config(config_file=temp_invalid_config_file)

def test_unsupported_config_format_fallback(tmp_path):
    """Test that an unsupported config file format falls back to defaults."""
    unsupported_file = tmp_path / "unsupported.txt"
    unsupported_file.write_text("some content")
    
    config = Config(config_file=str(unsupported_file))
    assert config.DB_ENGINE == "sqlite"
    assert config.migration.directory == "alembic"
    
def test_sqlite_port_is_none():
    """Test that the port for the 'sqlite' engine is correctly set to None."""
    config = Config()
    assert config.database.engine == "sqlite"
    assert config.database.port is None
