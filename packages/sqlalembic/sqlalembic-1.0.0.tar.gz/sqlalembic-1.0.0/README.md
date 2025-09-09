# SqlAlembic Framework
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)

A comprehensive Python framework for SQLAlchemy model discovery, configuration management, and database migrations with Alembic integration.

## 💡 Why SqlAlembic?
Modern Python projects often rely on SQLAlchemy for database management and Alembic for migrations. While both are powerful, integrating them smoothly can be a tedious, manual, and time-consuming process.

**SqlAlembic** solves this problem by providing a comprehensive, out-of-the-box framework that automates the most frustrating parts of the workflow.

* **Saves Hours on Manual Setup**: Forget about writing boilerplate code. SqlAlembic handles the configuration and project structure for you, so you can focus on building your application.

* **Automated Model Discovery**: Instead of manually registering your models, our framework intelligently scans your project and automatically discovers all your SQLAlchemy models, ensuring your migrations are always up to date.

* **Seamless CLI Integration**: We provide a powerful and intuitive command-line interface that integrates all core database and migration tasks into a single, unified tool.

## 🚀 Features

- **Automatic Model Discovery**: Intelligently scans your project for SQLAlchemy models
- **Multi-format Configuration**: Supports TOML, YAML, JSON, and environment variables
- **Advanced Caching System**: Caches discovered models for improved performance
- **Comprehensive Logging**: Structured logging with multiple output formats
- **Error Handling**: Robust error handling and validation
- **Signal System**: Event-driven architecture with signal dispatching
- **Multiple Database Support**: PostgreSQL, MySQL, SQLite
- **Migration Management**: Seamless Alembic integration
- **Advanced CLI**: A powerful command-line interface for managing all migration and database tasks

## 📁 Project Structure
```
sqlalembic/
├── sqlalembic/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                       # Configuration management
│   │   ├── initialize_core.py              # Core components initialization
│   │   ├── migration.py                    # Migration management and utilities
│   │   ├── logging_setup.py                # Logging configuration
│   │   ├── error_handler.py                # Error handling and exceptions
│   │   ├── project_structure.py            # Project structure utilities
│   │   └── signals.py                      # Signal dispatching system
│   ├── conf/
│   │   ├── alembic_template/     
│   │   │   ├── alembic.ini.template       # Alembic configuration template
│   │   │   ├── env.py.template             # Alembic environment script template
│   │   |   ├── README.md.template          # Project README template
│   │   │   └── script.py.mako.template     # Migration script template
│   │   └── project_template/     
│   │       ├── .env.template               # Environment variables template
│   │       └── manage.py.template          # Management script template
│   ├── integrations/                       # Third-party integrations
│   │   ├── __init__.py
│   │   └── alembic_setup.py                # Alembic integration setup
│   └── main.py                             # Main entry point
├── tests/    
│   ├── __init__.py
│   ├── test_model_discoverer.py            # Model discovery tests
│   ├── test_config.py                      # config tests
│   ├── test_signals.py                     # signals tests
│   ├── test_project_structure.py           # project structure tests
│   └── tests_integration.py                # Integration tests
├── LICENSE                                 # MIT License file
├── MANIFEST.in                             # Package manifest file
├── README.md                               # Project documentation
├── requirements.txt                        # Python dependencies
└── setup.py                               # Package setup configuration
```
## 🛠️ Installation

```bash
pip install sqlalembic
```
## 🚀 Quick Start

### 1. Create a New Project
Use the startproject command to create a new project structure:

```bash
sqlalembic startproject myproject
```

### 2. Project Structure
A new folder named after your project will be created:
```

├── myproject/
│   ├── versions/
│   ├── env.py
|   ├── README.md 
│   └── script.py.mako  
├── .env                # Environment variables file (optional)
└── manage.py           # Command-line utility for project management
```
### 3. Run Your First Migration
```bash
python manage.py makemigrations "Initial migration"
python manage.py migrate
```
## 💻 Migration Commands
The framework provides a powerful command-line interface to manage all aspects of your database migrations.

All commands are run using:
```bash
python manage.py <command>
```

### 1. Core Migration Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `makemigrations [message]` | Creates new migration files based on model changes. | `makemigrations "Add user table"` |
| `makemigrations --empty` | Creates an empty migration file. | `makemigrations --empty "Initial setup"` |
| `migrate [version]` | Applies migrations to the database. | `migrate head` |
| `rollback [version]` | Rolls back migrations to a previous state. | `rollback -1` |
| `stamp [revision]` | Stamps the database with a specific revision without running migrations. | `stamp 1a2b3c4d5e` |
| `merge [revisions]` | Merges multiple revision heads into a single new migration file. | `merge head1 head2` |
| `fresh` | Resets the database and reapplies all migrations from scratch. | `fresh --confirm` |
| `reset` | Rolls back all migrations to the initial state (`base`). | `reset --confirm` |

---

### 2. Information & Status Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `status` | Shows the comprehensive migration status. | `status` |
| `current` | Displays the current migration revision. | `current --verbose` |
| `history` | Shows the full migration history. | `history --range base:head` |
| `show [revision]` | Displays the details of a specific migration revision. | `show 1a2b3c4d5e` |
| `heads` | Shows the current migration heads. | `heads` |
| `branches` | Displays all branches in the migration tree. | `branches` |
| `list` | Lists all migrations, with options to filter. | `list --pending-only` |
| `check` | Checks if there are any pending migrations to apply. | `check` |
| `validate` | Validates the current migration state and checks for issues. | `validate` |

---

### 3. Utility Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `clean` | Cleans migration cache files and bytecode. | `clean --cache-only` |
## ⚙️ Configuration

### Configuration Priority

The framework loads configuration in the following order (highest to lowest priority):

1. **Environment Variables**
2. **Configuration Files** (TOML/YAML/JSON)
3. **Default Values**

### Configuration Files

The framework automatically searches for configuration files in this order:

```
sqlalembic.toml
sqlalembic.yaml / sqlalembic.yml
sqlalembic.json
config.toml
config.yaml / config.yml
config.json
alembic.toml
alembic.yaml
alembic.json
```

### Sample Configuration Files

#### TOML Configuration (`sqlalembic.toml`)

```toml
[general]
DEBUG = true
ENVIRONMENT = "development"
PROJECT_NAME = "My SQLAlchemy Project"

[database]
DB_ENGINE = "postgresql"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "myuser"
DB_PASS = "mypassword"
DB_NAME = "mydatabase"
DATABASE_ECHO = false

[migration]
MIGRATION_DIR = "alembic"
MIGRATION_VERSIONS_PATH = "versions"
MIGRATION_COMPARE_TYPE = true
MIGRATION_COMPARE_SERVER_DEFAULT = true
MIGRATION_TIMEZONE = "UTC"
MIGRATION_VERSION_TABLE = "alembic_version"

[logging]
LOGGING_LEVEL = "INFO"
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_FILE = "logs/sqlalembic.log"

[discovery]
AUTO_DISCOVER_MODELS = true
MODEL_DISCOVERY_PATHS = "models:app/models"
EXCLUDE_PATHS = "venv,.venv,__pycache__,env,.env,Lib,Include,Scripts,.git"
```

#### YAML Configuration (`sqlalembic.yaml`)

```yaml
general:
  DEBUG: true
  ENVIRONMENT: development
  PROJECT_NAME: My SQLAlchemy Project

database:
  DB_ENGINE: postgresql
  DB_HOST: localhost
  DB_PORT: 5432
  DB_USER: myuser
  DB_PASS: mypassword
  DB_NAME: mydatabase
  DATABASE_ECHO: false

migration:
  MIGRATION_DIR: alembic
  MIGRATION_VERSIONS_PATH: versions
  MIGRATION_COMPARE_TYPE: true
  MIGRATION_COMPARE_SERVER_DEFAULT: true
  MIGRATION_TIMEZONE: UTC

logging:
  LOGGING_LEVEL: INFO
  LOGGING_FORMAT: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

discovery:
  AUTO_DISCOVER_MODELS: true
  EXCLUDE_PATHS: venv,.venv,__pycache__,env,.env,Lib,Include,Scripts,.git
```

#### Environment Variables (`.env`)

```env
# Database Configuration
DB_ENGINE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=myuser
DB_PASS=mypassword
DB_NAME=mydatabase
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_ECHO=false

# General Settings
DEBUG=true
ENVIRONMENT=development
PROJECT_NAME=My SQLAlchemy Project

# Logging
LOGGING_LEVEL=INFO
LOGGING_FILE=logs/app.log

# Model Discovery
AUTO_DISCOVER_MODELS=true
MODEL_DISCOVERY_PATHS=models:app/models
EXCLUDE_PATHS=venv,.venv,__pycache__,env,.env
```

## 🗃️ Database Support

### PostgreSQL

```toml
[database]
DB_ENGINE = "postgresql"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "username"
DB_PASS = "password"
DB_NAME = "database_name"
```

Or use connection URL:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### MySQL

```toml
[database]
DB_ENGINE = "mysql"
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "username"
DB_PASS = "password"
DB_NAME = "database_name"
```

### SQLite

```toml
[database]
DB_ENGINE = "sqlite"
DB_NAME = "database.db"  # File will be created in project root
```

Or absolute path:
```env
DB_NAME=/path/to/database.db
```

## 📝 Model Definition Examples

### Basic Model

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Model with Relationships

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationship
    author = relationship("User", back_populates="posts")

# Add to User model
User.posts = relationship("Post", back_populates="author")
```

### Advanced Model with Indexes and Constraints

```python
from sqlalchemy import Column, Integer, String, Index, UniqueConstraint, CheckConstraint

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)  # Price in cents
    category = Column(String(50), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    
    # Table constraints
    __table_args__ = (
        Index('idx_product_category', 'category'),
        Index('idx_product_name_category', 'name', 'category'),
        UniqueConstraint('name', 'category', name='unique_name_category'),
        CheckConstraint('price > 0', name='positive_price'),
    )
```

## 🔍 Model Discovery Process

The framework uses a sophisticated process to discover SQLAlchemy models:

### 1. File Scanning

- Recursively scans the project directory
- Excludes specified directories (venv, __pycache__, etc.)
- Identifies Python files with SQLAlchemy indicators

### 2. AST Analysis

Uses Python's AST (Abstract Syntax Tree) to detect:

```python
# SQLAlchemy indicators
- from sqlalchemy import ...
- import sqlalchemy
- Column(...)
- __tablename__ = "..."
- declarative_base()
- DeclarativeBase
- relationship(...)
- ForeignKey(...)
- Table(...)
```

### 3. Safe Import Process

- Uses subprocess isolation for safety
- Dynamically imports discovered files
- Extracts model classes and metadata
- Handles import errors gracefully

### 4. Metadata Consolidation

- Combines all discovered tables
- Avoids duplicate tables
- Creates unified MetaData object

# Signal System

The Sqlalembic framework includes a powerful signal system that allows you to hook into various events throughout the migration process.

## Quick Start

```python
from sqlalembic.core.signals import dispatcher

# Define your handler
def my_handler(sender, **kwargs):
    print(f"Migration event: {kwargs}")

# Connect to a signal
dispatcher.connect("command_finished", my_handler)

# That's it! Your handler will be called when migrations complete
```

## How It Works

The signal system follows the observer pattern:
1. **Connect** handlers to specific signals
2. When events occur, the framework **sends** signals
3. All connected handlers are **automatically called**

## SignalDispatcher API

### `dispatcher.connect(signal_name, handler)`
Register a function to be called when a signal is sent.

**Parameters:**
- `signal_name` (str): Name of the signal to listen for
- `handler` (callable): Function to call when signal is sent

```python
def on_migration_complete(sender, **kwargs):
    print(f"{kwargs['command_name']} completed!")

dispatcher.connect("command_finished", on_migration_complete)
```

### `dispatcher.disconnect(signal_name, handler)`
Remove a handler from a signal.

```python
dispatcher.disconnect("command_finished", on_migration_complete)
```

### `dispatcher.send(signal_name, sender=None, **kwargs)`
Send a signal (usually called by the framework, not by you).

**Returns:** List of `(handler, result)` tuples

## Built-in Signals

### Command Lifecycle
- `command_finished` - Command completed successfully
- `command_failed` - Command failed with an error

```python
def log_results(sender, **kwargs):
    if 'success' in kwargs:
        print(f"{kwargs['command_name']} succeeded")
    elif 'exception' in kwargs:
        print(f"{kwargs['command_name']} failed: {kwargs['exception']}")

dispatcher.connect("command_finished", log_results)
dispatcher.connect("command_failed", log_results)
```

### Migration Commands
Each migration command sends a signal when it starts:

```python
# Listen for specific commands
dispatcher.connect("migration_migrate_command", on_migrate_start)
dispatcher.connect("migration_rollback_command", on_rollback_start)
dispatcher.connect("migration_makemigrations_command", on_makemigrations_start)

# Or listen for all commands
def on_any_command(sender, **kwargs):
    command = kwargs.get('command_name', 'unknown')
    print(f"Starting {command}")

# Connect to all command signals
commands = [
    "migration_migrate_command",
    "migration_rollback_command", 
    "migration_makemigrations_command",
    "migration_history_command",
    "migration_current_command"
]

for cmd in commands:
    dispatcher.connect(cmd, on_any_command)
```

## All Available Signals

### Command Lifecycle
- `command_finished` - Any command completed successfully
- `command_failed` - Any command failed

### Specific Commands
- `migration_makemigrations_command` - Create new migration
- `migration_migrate_command` - Apply migrations
- `migration_rollback_command` - Rollback migrations
- `migration_history_command` - Show migration history
- `migration_current_command` - Show current migration
- `migration_show_command` - Show specific migration
- `migration_heads_command` - Show head migrations
- `migration_branches_command` - Show migration branches
- `migration_stamp_command` - Mark migration as applied
- `migration_merge_command` - Merge migration branches
- `migration_squash_command` - Combine migrations
- `migration_check_command` - Validate migrations
- `migration_validate_command` - Check migration syntax
- `migration_reset_command` - Reset migration state
- `migration_fresh_command` - Fresh migration setup
- `migration_clean_command` - Clean migration files
- `migration_status_command` - Show migration status
- `migration_list_command` - List all migrations

### Alembic Process
- `alembic_command_started` - Before Alembic runs
- `alembic_command_completed` - Alembic succeeded
- `alembic_command_failed` - Alembic failed

## 🚨 Error Handling

### Configuration Errors

```python
from sqlalembic.core.config import ConfigurationError

try:
    config = Config()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Common Issues and Solutions

#### Model Discovery Issues

**Problem**: No models discovered
```python
# Check if auto-discovery is enabled
config.AUTO_DISCOVER_MODELS = True

# Check excluded paths
print(config.EXCLUDE_PATHS)

# Enable debug mode
discoverer = ModelDiscoverer(dependencies, debug=True)
```

**Problem**: Import errors during discovery
```python
# Check Python path
import sys
sys.path.insert(0, '/path/to/your/project')

# Check for circular imports
# Move import statements inside functions if needed
```

#### Database Connection Issues

**Problem**: Connection refused
```bash
# Check if database server is running
sudo service postgresql start  # PostgreSQL
sudo service mysql start       # MySQL
```

**Problem**: Authentication failed
```python
# Verify credentials in configuration
print(config.DATABASE_URI)

# Test connection manually
from sqlalchemy import create_engine
engine = create_engine(config.DATABASE_URI)
engine.connect()
```

## 📊 Logging

### Configuration

```python
# Enable SQL logging
DATABASE_ECHO = true

# Set log level
LOGGING_LEVEL = "DEBUG"

# Log to file
LOGGING_FILE = "logs/sqlalembic.log"
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about framework operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for handled exceptions
- **CRITICAL**: Critical errors that may stop the application

### Example Log Output

```
2024-01-15 10:30:45 - sqlalembic.config - INFO - Configuration initialized from: /project/sqlalembic.toml
2024-01-15 10:30:45 - sqlalembic.discovery - INFO - Starting model discovery in: /project
2024-01-15 10:30:45 - sqlalembic.discovery - INFO - Found 3 potential model files
2024-01-15 10:30:46 - sqlalembic.discovery - INFO - Successfully discovered 5 tables
```

## 🧪 Testing

### Unit Tests

```python
import unittest
from sqlalembic.core.config import Config
from sqlalembic.intergrations.alembic_setup import ModelDiscoverer

class TestModelDiscovery(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.dependencies = {
            "config": self.config,
            "logger": logging.getLogger(__name__)
        }
    
    def test_model_discovery(self):
        discoverer = ModelDiscoverer(self.dependencies)
        metadata = discoverer.discover()
        self.assertGreater(len(metadata.tables), 0)
    
    def test_cache_functionality(self):
        discoverer = ModelDiscoverer(self.dependencies, use_cache=True)
        # First call - should populate cache
        metadata1 = discoverer.discover()
        # Second call - should use cache
        metadata2 = discoverer.discover()
        self.assertEqual(len(metadata1.tables), len(metadata2.tables))
```

### Integration Tests

```python
from sqlalembic.core.initialize_core import initialize_core_components

def test_full_initialization():
    """Test complete framework initialization"""
    components = initialize_core_components()
    
    assert "config" in components
    assert "logger" in components
    assert "error_handler" in components
    assert "dispatcher" in components
    
    # Test database connection
    from sqlalchemy import create_engine
    engine = create_engine(components["config"].DATABASE_URI)
    connection = engine.connect()
    connection.close()
```
## Common Use Cases

### 1. Notifications
```python
def send_slack_notification(sender, **kwargs):
    if kwargs.get('success'):
        send_to_slack(f"Migration {kwargs['command_name']} completed")
    else:
        send_to_slack(f"Migration failed: {kwargs.get('exception')}")

dispatcher.connect("command_finished", send_slack_notification)
dispatcher.connect("command_failed", send_slack_notification)
```

### 2. Custom Logging
```python
import logging

migration_logger = logging.getLogger('migrations')

def log_migration_events(sender, **kwargs):
    command = kwargs.get('command_name', 'unknown')
    migration_logger.info(f"Migration command: {command}", extra=kwargs)

dispatcher.connect("command_finished", log_migration_events)
```

### 3. Database Cleanup
```python
def cleanup_after_rollback(sender, **kwargs):
    if kwargs.get('command_name') == 'rollback':
        # Clean up temporary data
        cleanup_temp_tables()

dispatcher.connect("command_finished", cleanup_after_rollback)
```

### 4. Performance Monitoring
```python
import time

start_times = {}

def track_performance_start(sender, **kwargs):
    command = kwargs.get('command_name')
    start_times[command] = time.time()

def track_performance_end(sender, **kwargs):
    command = kwargs.get('command_name')
    if command in start_times:
        duration = time.time() - start_times[command]
        print(f"⏱️  {command} took {duration:.2f} seconds")

dispatcher.connect("migration_migrate_command", track_performance_start)
dispatcher.connect("command_finished", track_performance_end)
```

## Best Practices

1. **Keep handlers lightweight** - Signals are called synchronously
2. **Handle exceptions** - Failing handlers don't stop the migration
3. **Use descriptive names** - Make your handler functions self-documenting
4. **Disconnect when done** - Clean up handlers you no longer need

```python
# Good: Clear, specific handler
def notify_team_on_production_migration(sender, **kwargs):
    if is_production() and kwargs.get('success'):
        send_notification("Production migration completed")

# Better: Include error handling
def safe_notification_handler(sender, **kwargs):
    try:
        notify_team_on_production_migration(sender, **kwargs)
    except Exception as e:
        logger.error(f"Notification failed: {e}")
```
## 🔧 Advanced Usage

### Custom Model Discovery Paths

```toml
# Specify custom paths to search for models
MODEL_DISCOVERY_PATHS = "app/models:src/database/models:custom/path"
```

### Custom Exclusions

```toml
# Add custom directories to exclude
EXCLUDE_PATHS = "venv,.venv,__pycache__,tests,docs,build,dist"
```

### Programmatic Configuration

```python
from sqlalembic.core.config import Config

# Create config with custom settings
config = Config(config_file="custom_config.toml", load_env=False)

# Modify configuration at runtime
config.set("DEBUG", True)
config.set("LOGGING_LEVEL", "DEBUG", section="logging")

# Export configuration
config_dict = config.to_dict()
```

## 🚀 Performance Optimization

### Caching

The framework includes an intelligent caching system:

- **File-based caching**: Stores discovered metadata to disk
- **Hash validation**: Detects changes in model files
- **Automatic invalidation**: Clears cache when files change

### Best Practices

1. **Use caching in production**:
   ```python
   discoverer = ModelDiscoverer(dependencies, use_cache=True)
   ```

2. **Exclude unnecessary directories**:
   ```toml
   EXCLUDE_PATHS = "venv,tests,docs,build,dist,node_modules"
   ```

3. **Minimize model file complexity**:
   - Avoid complex imports in model files
   - Use lazy loading for relationships
   - Keep models focused and simple

## 🐛 Troubleshooting

### Common Issues

#### Issue: "No models discovered"

**Solutions**:
1. Check that `AUTO_DISCOVER_MODELS = True`
2. Verify model files contain SQLAlchemy indicators
3. Check excluded paths don't include model directories
4. Enable debug mode: `debug=True`

#### Issue: "Import errors during discovery"

**Solutions**:
1. Check for circular imports
2. Ensure all dependencies are installed
3. Verify Python path includes project root
4. Check for syntax errors in model files

#### Issue: "Database connection failed"

**Solutions**:
1. Verify database server is running
2. Check connection credentials
3. Test DATABASE_URI manually
4. Check network connectivity and firewall settings

#### Issue: "Configuration file not found"

**Solutions**:
1. Place config file in project root
2. Use supported file names (sqlalembic.toml, config.yaml, etc.)
3. Specify config file path explicitly
4. Use environment variables as fallback

### Debug Mode

Enable debug mode for detailed logging:

```python
# In model discovery
discoverer = ModelDiscoverer(dependencies, debug=True)

# In configuration
config = Config()
config.DEBUG = True

# Set logging level
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Development Setup

1. **Clone the repository**
2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for all public methods
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Use GitHub Discussions for questions and ideas

## 📋 Changelog

### Version 1.0.0
- Initial release
- Basic model discovery
- Configuration management
- Multi-database support
- Caching system
- Logging integration

---