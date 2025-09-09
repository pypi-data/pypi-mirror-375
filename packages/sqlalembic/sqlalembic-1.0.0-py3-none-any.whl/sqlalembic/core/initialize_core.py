import logging
from typing import Dict, Any
from dotenv import load_dotenv

from .config import Config, get_project_root
from .logging_setup import setup_logging
from .error_handler import ErrorHandler
from .signals import SignalDispatcher

logger = logging.getLogger(__name__)

def initialize_core_components(config_file: str = None) -> Dict[str, Any]:
    """
    Initializes all core framework components and returns them in a dictionary.
    
    The initialization order is critical:
    1. Load environment variables.
    2. Load configuration from file/env/defaults.
    3. Validate configuration.
    4. Setup logging based on the loaded configuration.
    5. Initialize other core components.
    
    Args:
        config_file: Optional path to configuration file
    
    Returns:
        A dictionary containing all initialized core components.
        
    Raises:
        Exception: If any critical initialization step fails.
    """
    global logger
    
    load_dotenv()
    
    logger.info(".env file loaded successfully")

    try:
        config = Config(config_file=config_file)
        if not hasattr(config, 'project_root') or config.project_root:
            config.project_root=get_project_root()
            
        logger.info(f"Configuration initialized from: {config._config_file_path or 'environment/defaults'}")
    except Exception as e:
        logger.critical(f"Failed to initialize configuration: {e}")
        raise

    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except Exception as e:
        logger.critical(f"Configuration validation failed: {e}")
        raise

    try:
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("Logging system configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure advanced logging: {e}. Using basic config")
        

    try:
        error_handler_instance = ErrorHandler(config=config)
        logger.info("ErrorHandler initialized successfully")
        
        dispatcher_instance = SignalDispatcher()
        logger.info("SignalDispatcher initialized successfully")
        
    except Exception as e:
        logger.critical(f"Failed to initialize core components: {e}")
        raise

    logger.info("All core components initialized successfully")
    
    return {
        "config": config,
        "logger": logger,
        "error_handler": error_handler_instance,
        "dispatcher": dispatcher_instance
    }


def get_initialized_components(reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get initialized core components with singleton pattern.
    
    Args:
        reload: Force re-initialization
        **kwargs: Additional arguments for initialization
        
    Returns:
        Dictionary of initialized components
    """
    if not hasattr(get_initialized_components, '_components') or reload:
        get_initialized_components._components = initialize_core_components(**kwargs)
    
    return get_initialized_components._components