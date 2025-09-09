import os
import logging
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

CONFIG_FILES = [
    "sqlalembic.toml",
    "sqlalembic.yaml", 
    "sqlalembic.yml",
    "sqlalembic.json",
    "config.toml",
    "config.yaml",
    "config.yml", 
    "config.json",
    "alembic.toml",
    "alembic.yaml",
    "alembic.json"
]

ENV_FILES = [".env", ".env.local", ".env.development", ".env.production"]

@dataclass
class DatabaseConfig:
    """Database configuration container."""
    engine: str = "sqlite"
    host: str = "localhost"
    port: Optional[int] = 5432
    user: str = ""
    password: str = ""
    database: str = "db"
    url: Optional[str] = None
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    connect_args: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate database configuration after initialization."""
        pass

@dataclass 
class MigrationConfig:
    """Migration-specific configuration."""
    directory: str = "alembic"
    versions_path: str = "versions"
    script_location: str = "alembic"
    file_template: str = "%%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(rev)s_%%(slug)s"
    truncate_slug_length: int = 40
    compare_type: bool = True
    compare_server_default: bool = True
    timezone: str = "UTC"
    process_revision_directives: Optional[str] = None
    include_schemas: bool = True
    version_table: str = "alembic_version"
    version_table_schema: Optional[str] = None
    
@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file: Optional[str] = None
    max_bytes: int = 10485760
    backup_count: int = 5
    console: bool = True
    sql_echo: bool = False

DEFAULTS = {
    "DB_ENGINE": "sqlite",
    "DB_HOST": "localhost", 
    "DB_PORT": "5432",
    "DB_USER": "",
    "DB_PASS": "",
    "DB_NAME": "db",
    "DATABASE_ECHO": "False",
    "DATABASE_POOL_SIZE": "5",
    "DATABASE_MAX_OVERFLOW": "10",
    "DATABASE_POOL_TIMEOUT": "30",
    "DATABASE_POOL_RECYCLE": "3600",
    
    "DEBUG": "True",
    "ENVIRONMENT": "development",
    "PROJECT_NAME": "SqlAlembic Project",
    "SECRET_KEY": "",
    
    "LOGGING_LEVEL": "INFO",
    "LOGGING_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "LOGGING_FILE": "",
    
    "MIGRATION_DIR": "alembic",
    "MIGRATION_VERSIONS_PATH": "versions",
    "MIGRATION_COMPARE_TYPE": "True",
    "MIGRATION_COMPARE_SERVER_DEFAULT": "True",
    "MIGRATION_TIMEZONE": "UTC",
    "MIGRATION_VERSION_TABLE": "alembic_version",
    
    "AUTO_DISCOVER_MODELS": "True",
    "MODEL_DISCOVERY_PATHS": "",
    "EXCLUDE_PATHS": "venv,.venv,__pycache__,env,.env,Lib,Include,Scripts,.git",
}


class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass


def load_env_file(env_file_path: str) -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    if os.path.exists(env_file_path):
        logger.info(f"Loading environment from {env_file_path}")
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' not in line:
                        logger.warning(f"Invalid line {line_no} in {env_file_path}: {line}")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('\'"')
                    
                    if key:
                        env_vars[key] = value
                        
        except Exception as e:
            logger.error(f"Error loading env file {env_file_path}: {e}")
    
    return env_vars


def find_config_file(start_dir: Optional[str] = None) -> Optional[str]:
    """Find configuration file in project hierarchy."""
    if start_dir is None:
        start_dir = os.getcwd()
    
    current_dir = Path(start_dir).resolve()
    
    for directory in [current_dir] + list(current_dir.parents):
        for config_file in CONFIG_FILES:
            config_path = directory / config_file
            if config_path.exists():
                logger.info(f"Found config file: {config_path}")
                return str(config_path)
    
    return None


def load_config_file(config_file: str) -> Dict[str, Any]:
    """Load configuration from file (JSON, YAML, or TOML)."""
    if not os.path.exists(config_file):
        return {}
    
    config_path = Path(config_file)
    suffix = config_path.suffix.lower()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            if suffix == '.json':
                return json.load(f)
            elif suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif suffix == '.toml':
                return toml.load(f)
            else:
                logger.warning(f"Unsupported config file format: {suffix}")
                return {}
                
    except Exception as e:
        logger.error(f"Error loading config file {config_file}: {e}")
        raise ConfigurationError(f"Failed to load configuration file: {e}")


def get_project_root(marker_files: Optional[List[str]] = None) -> str:
    """Find project root by looking for marker files."""
    if marker_files is None:
        marker_files = ['.git', 'setup.py', 'pyproject.toml', 'requirements.txt', 'alembic.ini']
    
    current = Path.cwd()
    
    for directory in [current] + list(current.parents):
        if any((directory / marker).exists() for marker in marker_files):
            return str(directory)
    
    return str(current)


class Config:
    """
    Comprehensive configuration management for SqlAlembic Framework.
    
    Loads configuration with priority:
    1. Environment Variables
    2. Configuration File (TOML/YAML/JSON)  
    3. Default Values
    
    Supports multiple configuration file formats and automatic discovery.
    """
    
    def __init__(self, 
                 config_file: Optional[str] = None,
                 load_env: bool = True,
                 project_root: Optional[str] = None):
        """
        Initialize configuration system.
        
        Args:
            config_file: Path to configuration file (auto-detected if None)
            load_env: Whether to load .env files
            project_root: Project root directory (auto-detected if None)
        """
        logger.info("Initializing SqlAlembic configuration system")
        
        self.project_root = project_root or get_project_root()
        logger.info(f"Project root: {self.project_root}")
        
        self._env_vars = {}
        if load_env:
            self._load_env_files()
        
        self._config_file_path = config_file or find_config_file(self.project_root)
        self._config_data = {}
        
        if self._config_file_path:
            self._config_data = load_config_file(self._config_file_path)
            logger.info(f"Loaded configuration from: {self._config_file_path}")
        else:
            logger.info("No configuration file found, using environment and defaults")
        
        self._initialize_configuration()
        
        self.validate()
        
        logger.info("Configuration initialization completed")
    
    def _load_env_files(self):
        """Load environment variables from .env files."""
        for env_file in ENV_FILES:
            env_path = os.path.join(self.project_root, env_file)
            if os.path.exists(env_path):
                env_vars = load_env_file(env_path)
                self._env_vars.update(env_vars)
                for key, value in env_vars.items():
                    if key not in os.environ:
                        os.environ[key] = value
    
    def _get_value(self, key: str, 
                  conversion_func=None, 
                  default=None,
                  section: Optional[str] = None) -> Any:
        """
        Get configuration value with priority: Environment -> Config File -> Default.
        
        Args:
            key: Configuration key
            conversion_func: Function to convert string value
            default: Default value if not found
            section: Configuration file section to look in
        """
        env_value = os.getenv(key) or self._env_vars.get(key)
        if env_value is not None:
            return self._convert_value(env_value, conversion_func, key, "environment")
        
        if section and isinstance(self._config_data, dict):
            section_data = self._config_data.get(section, {})
            if isinstance(section_data, dict) and key in section_data:
                config_value = section_data[key]
                return self._convert_value(config_value, conversion_func, key, "config file")
        
        if isinstance(self._config_data, dict) and key in self._config_data:
            config_value = self._config_data[key]
            return self._convert_value(config_value, conversion_func, key, "config file")
        
        if default is not None:
            return self._convert_value(default, conversion_func, key, "provided default")
        
        system_default = DEFAULTS.get(key)
        if system_default is not None:
            return self._convert_value(system_default, conversion_func, key, "system default")
        
        return None
    
    def _convert_value(self, value: Any, conversion_func, key: str, source: str) -> Any:
        """Convert value using conversion function with error handling."""
        if conversion_func is None:
            return value
        
        try:
            return conversion_func(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert {source} value for '{key}': {value} -> {e}")
            return value
    
    @staticmethod
    def _str_to_bool(value: Any) -> bool:
        """Convert string to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "t", "yes", "on")
        return bool(value)
    
    @staticmethod
    def _str_to_int(value: Any) -> int:
        """Convert string to integer."""
        if isinstance(value, int):
            return value
        return int(str(value))
    
    @staticmethod
    def _str_to_list(value: Any, separator: str = ',') -> List[str]:
        """Convert string to list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return []
    
    def _initialize_configuration(self):
        """Initialize all configuration sections."""
        self.DEBUG = self._get_value("DEBUG", self._str_to_bool)
        self.ENVIRONMENT = self._get_value("ENVIRONMENT", default="development")
        self.PROJECT_NAME = self._get_value("PROJECT_NAME", default="SqlAlembic Project")
        self.SECRET_KEY = self._get_value("SECRET_KEY", default="")
        
        self.database = DatabaseConfig(
            engine=self._get_value("DB_ENGINE", str.lower, section="database"),
            host=self._get_value("DB_HOST", section="database"),
            port=self._get_value("DB_PORT", self._str_to_int, section="database"),
            user=self._get_value("DB_USER", default="", section="database"),
            password=self._get_value("DB_PASS", default="", section="database"),
            database=self._get_value("DB_NAME", section="database"),
            url=self._get_value("DATABASE_URL", section="database"),
            echo=self._get_value("DATABASE_ECHO", self._str_to_bool, section="database"),
            pool_size=self._get_value("DATABASE_POOL_SIZE", self._str_to_int, section="database"),
            max_overflow=self._get_value("DATABASE_MAX_OVERFLOW", self._str_to_int, section="database"),
            pool_timeout=self._get_value("DATABASE_POOL_TIMEOUT", self._str_to_int, section="database"),
            pool_recycle=self._get_value("DATABASE_POOL_RECYCLE", self._str_to_int, section="database")
        )
        
        if self.database.engine == "sqlite":
            self.database.port = None
        elif self.database.engine == "mysql":
            if self.database.port == 5432:
                self.database.port = 3306

        self.migration = MigrationConfig(
            directory=self._get_value("MIGRATION_DIR", section="migration"),
            versions_path=self._get_value("MIGRATION_VERSIONS_PATH", section="migration"),
            compare_type=self._get_value("MIGRATION_COMPARE_TYPE", self._str_to_bool, section="migration"),
            compare_server_default=self._get_value("MIGRATION_COMPARE_SERVER_DEFAULT", self._str_to_bool, section="migration"),
            timezone=self._get_value("MIGRATION_TIMEZONE", section="migration"),
            version_table=self._get_value("MIGRATION_VERSION_TABLE", section="migration")
        )
        
        self.logging = LoggingConfig(
            level=self._get_value("LOGGING_LEVEL", str.upper, section="logging"),
            format=self._get_value("LOGGING_FORMAT", section="logging"),
            file=self._get_value("LOGGING_FILE", section="logging"),
            sql_echo=self._get_value("DATABASE_ECHO", self._str_to_bool, section="logging")
        )
        
        self.AUTO_DISCOVER_MODELS = self._get_value("AUTO_DISCOVER_MODELS", self._str_to_bool)
        self.MODEL_DISCOVERY_PATHS = self._get_value("MODEL_DISCOVERY_PATHS", 
                                                     lambda x: self._str_to_list(x, ':'))
        self.EXCLUDE_PATHS = self._get_value("EXCLUDE_PATHS", 
                                             lambda x: set(self._str_to_list(x)))
        
        self.DB_ENGINE = self.database.engine
        self.DATABASE_ECHO = self.database.echo
        self.LOGGING_LEVEL = self.logging.level
        self.DATABASE_CONFIG = {
            "engine": self.database.engine,
            "host": self.database.host,
            "port": self.database.port,
            "user": self.database.user,
            "password": self.database.password,
            "database": self.database.database
        }
    
    @property
    def DATABASE_URI(self) -> str:
        """Generate database connection URI."""
        if self.database.url:
            return self.database.url
        
        engine = self.database.engine
        
        if engine == "postgresql":
            if not all([self.database.user, self.database.host, self.database.database]):
                missing = []
                if not self.database.user: missing.append("DB_USER")
                if not self.database.host: missing.append("DB_HOST") 
                if not self.database.database: missing.append("DB_NAME")
                raise ConfigurationError(f"Missing PostgreSQL credentials: {', '.join(missing)}")
            
            password_part = f":{self.database.password}" if self.database.password else ""
            port_part = f":{self.database.port}" if self.database.port else ""
            
            return f"postgresql://{self.database.user}{password_part}@{self.database.host}{port_part}/{self.database.database}"
        
        elif engine == "mysql":
            if not all([self.database.user, self.database.host, self.database.database]):
                missing = []
                if not self.database.user: missing.append("DB_USER")
                if not self.database.host: missing.append("DB_HOST")
                if not self.database.database: missing.append("DB_NAME") 
                raise ConfigurationError(f"Missing MySQL credentials: {', '.join(missing)}")
            
            password_part = f":{self.database.password}" if self.database.password else ""
            port_part = f":{self.database.port}" if self.database.port else ""
            
            return f"mysql://{self.database.user}{password_part}@{self.database.host}{port_part}/{self.database.database}"
        
        elif engine in ("sqlite", "sqlite3"):
            db_name = self.database.database or "db.db"
            if not db_name.endswith(('.db', '.sqlite', '.sqlite3')):
                db_name += ".db"
            
            if not os.path.isabs(db_name):
                db_name = os.path.join(self.project_root, db_name)
            
            return f"sqlite:///{db_name}"
        
        else:
            raise ConfigurationError(f"Unsupported database engine: {engine}")
    
    def validate(self):
        """Validate configuration settings."""
        supported_engines = {"postgresql", "mysql", "sqlite", "sqlite3"}
        if self.database.engine not in supported_engines:
            raise ConfigurationError(f"Invalid DB_ENGINE '{self.database.engine}'. "
                                   f"Supported: {', '.join(supported_engines)}")
        
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.logging.level not in valid_levels:
            raise ConfigurationError(f"Invalid LOGGING_LEVEL '{self.logging.level}'. "
                                   f"Valid levels: {', '.join(valid_levels)}")
        
        try:
            uri = self.DATABASE_URI
            parsed = urlparse(uri)
            if not parsed.scheme:
                raise ConfigurationError("Invalid database URI: missing scheme")
        except Exception as e:
            if not isinstance(e, ConfigurationError):
                raise ConfigurationError(f"Database URI validation failed: {e}")
            raise
        
        logger.info("Configuration validation passed")
    
    def get(self, key: str, default=None, section: Optional[str] = None):
        """Get configuration value by key."""
        return self._get_value(key, default=default, section=section)
    
    def set(self, key: str, value: Any, section: Optional[str] = None):
        """Set configuration value (runtime only)."""
        if section:
            if section not in self._config_data:
                self._config_data[section] = {}
            self._config_data[section][key] = value
        else:
            self._config_data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "general": {
                "debug": self.DEBUG,
                "environment": self.ENVIRONMENT,
                "project_name": self.PROJECT_NAME,
                "project_root": self.project_root,
            },
            "database": {
                "engine": self.database.engine,
                "host": self.database.host,
                "port": self.database.port,
                "user": self.database.user,
                "database": self.database.database,
                "echo": self.database.echo,
                "uri": self.DATABASE_URI,
            },
            "migration": {
                "directory": self.migration.directory,
                "versions_path": self.migration.versions_path,
                "compare_type": self.migration.compare_type,
                "compare_server_default": self.migration.compare_server_default,
                "version_table": self.migration.version_table,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
            }
        }
    
    def __repr__(self) -> str:
        return f"<Config environment={self.ENVIRONMENT} engine={self.database.engine}>"

_config_instance = None


def get_config(reload: bool = False, **kwargs) -> Config:
    """Get global configuration instance (singleton pattern)."""
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = Config(**kwargs)
    
    return _config_instance
