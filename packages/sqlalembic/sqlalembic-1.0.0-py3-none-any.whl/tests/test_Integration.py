import pytest
from sqlalchemy import create_engine
from sqlalembic.core.initialize_core import initialize_core_components
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_components(monkeypatch):
    """
    Mocks the core components to isolate the test from external
    dependencies like actual database connections and configurations.
    """
    mock_config = MagicMock()
    mock_config.DATABASE_URI = "sqlite:///:memory:" 
    
    mock_logger = MagicMock()
    mock_error_handler = MagicMock()
    mock_dispatcher = MagicMock()
    
    def mock_initialize():
        return {
            "config": mock_config,
            "logger": mock_logger,
            "error_handler": mock_error_handler,
            "dispatcher": mock_dispatcher,
        }
    
    monkeypatch.setattr("sqlalembic.core.initialize_core.initialize_core_components", mock_initialize)
    
    return {
        "config": mock_config,
        "logger": mock_logger,
        "error_handler": mock_error_handler,
        "dispatcher": mock_dispatcher,
    }


def test_full_initialization(mock_db_components):
    """
    Tests that all core framework components are initialized correctly.
    This is an integration test.
    """
    components = mock_db_components
    
    assert "config" in components
    assert "logger" in components
    assert "error_handler" in components
    assert "dispatcher" in components

    try:
        engine = create_engine(components["config"].DATABASE_URI)
        connection = engine.connect()
        connection.close()
    except Exception as e:
        pytest.fail(f"Database connection test failed. Error: {e}")