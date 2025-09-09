import os
import ast
import sys
import subprocess
import pickle
import hashlib
import logging
from typing import List, Optional
from pathlib import Path
from sqlalchemy import MetaData
from ..core.config import Config

logger = logging.getLogger(__name__)

class ModelDiscoverer:
    """
    SQLAlchemy Model Discovery and Metadata Extraction Class
    """
    DEFAULT_CACHE_DIR = ".alembic_cache"
    CACHE_FILE = "metadata.pkl"
    CACHE_HASH_FILE = "metadata.hash"
    DEFAULT_EXCLUDE_DIRS = {
        "venv", ".venv", "__pycache__", "env", ".env", 
        "Lib", "Include", "Scripts", ".git", 
        "migrations", "alembic", "versions"
    }
    
    def __init__(self, 
                 cache_dir: str = DEFAULT_CACHE_DIR,
                 use_cache: bool = True,
                 debug: bool = False,):
        """
        Initialize Model Discoverer
        
        Args:
            project_path: Root path to scan (default: current directory)
            exclude_dirs: Directories to exclude from scanning
            cache_dir: Directory for caching results
            use_cache: Whether to use cached results
            debug: Enable debug logging
        """
        self.config = Config()
        self.project_path = str(Path(self.config.project_root or os.getcwd()).resolve())
        self.exclude_dirs = self.config.EXCLUDE_PATHS or self.DEFAULT_EXCLUDE_DIRS.copy()
        self.cache_dir = Path(self.project_path) / cache_dir
        self.use_cache = use_cache
        self.debug = debug
        self.auto_discovery = self.config.AUTO_DISCOVER_MODELS
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            
        logger.info(f"Initialized ModelDiscoverer for: {self.project_path}")
    
    def is_sqlalchemy_file(self, file_path: str) -> bool:
        """Enhanced detection for SQLAlchemy model files using AST."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            sqlalchemy_indicators = [
                'from sqlalchemy',
                'import sqlalchemy',
                'Column(',
                '__tablename__',
                'declarative_base',
                'DeclarativeBase',
                'relationship(',
                'ForeignKey(',
                'Table(',
            ]
            
            if not any(indicator in content for indicator in sqlalchemy_indicators):
                return False

            try:
                tree = ast.parse(content)
            except SyntaxError:
                return False
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and ('sqlalchemy' in node.module):
                        return True
                        
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if 'sqlalchemy' in alias.name:
                            return True
                
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id == '__tablename__':
                                    return True
                        elif isinstance(item, ast.AnnAssign):
                            if isinstance(item.annotation, ast.Name) and 'Column' in getattr(item.annotation, 'id', ''):
                                return True
                
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['Column', 'relationship', 'Table']:
                        return True
                        
            return False
            
        except Exception as e:
            logger.debug(f"Error analyzing file {file_path}: {e}")
            return False

    def scan_python_files(self) -> List[str]:
        """Scan project for potential SQLAlchemy model files."""
        model_files = []
        project_path = Path(self.project_path).resolve()
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)

                    rel_path = os.path.relpath(file_path, project_path)
                    if any(excluded in rel_path for excluded in self.exclude_dirs):
                        continue
                        
                    if self.is_sqlalchemy_file(file_path):
                        model_files.append(file_path)
                        logger.debug(f"Found potential model file: {file_path}")
        
        return model_files

    def get_file_hash(self, files: List[str]) -> str:
        """Generate hash for file contents to detect changes."""
        hasher = hashlib.md5()
        
        for file_path in sorted(files):
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            except Exception as e:
                logger.warning(f"Could not hash file {file_path}: {e}")
                hasher.update(file_path.encode())
        
        return hasher.hexdigest()

    def import_models_and_extract_metadata(self, model_files: List[str]) -> MetaData:
        """Import model files and extract metadata in subprocess for safety."""
        
        subprocess_script = f'''
import sys
import os
import importlib.util
import traceback
from pathlib import Path
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import DeclarativeBase

sys.path.insert(0, {repr(self.project_path)})

def safe_import_module(file_path):
    """Safely import a Python module from file path with proper package handling."""
    try:
        abs_file_path = os.path.abspath(file_path)
        project_root = {repr(self.project_path)}
        
        try:
            rel_path = os.path.relpath(abs_file_path, project_root)
        except ValueError:
            rel_path = abs_file_path
        
        path_parts = rel_path.replace('\\\\', '/').split('/')
        
        if path_parts[-1].endswith('.py'):
            path_parts[-1] = path_parts[-1][:-3]
        
        if path_parts[-1] == '__init__':
            path_parts = path_parts[:-1]
        
        module_name = '.'.join(path_parts)
        
        current_dir = os.path.dirname(abs_file_path)
        parent_dirs = []
        
        temp_dir = current_dir
        while temp_dir and temp_dir != project_root:
            parent_dirs.append(temp_dir)
            temp_dir = os.path.dirname(temp_dir)
        
        parent_dirs.append(project_root)
        
        for dir_path in reversed(parent_dirs):
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)
        
        parent_modules = []
        for i in range(len(path_parts) - 1):
            parent_name = '.'.join(path_parts[:i+1])
            if parent_name not in sys.modules:
                import types
                parent_module = types.ModuleType(parent_name)
                parent_module.__path__ = [os.path.join(project_root, *path_parts[:i+1])]
                parent_module.__package__ = parent_name
                sys.modules[parent_name] = parent_module
                parent_modules.append(parent_name)
        
        spec = importlib.util.spec_from_file_location(module_name, abs_file_path)
        if spec is None or spec.loader is None:

            return None
        
        module = importlib.util.module_from_spec(spec)
        
        module.__package__ = '.'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
        
        sys.modules[module_name] = module
        
        spec.loader.exec_module(module)
        
        return module
        
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

def extract_models_from_module(module):
    """Extract SQLAlchemy model classes from a module."""
    models = []
    
    if not module:
        return models
        
    for attr_name in dir(module):
        if attr_name.startswith('_'):
            continue
            
        try:
            obj = getattr(module, attr_name)
            
            if not isinstance(obj, type):
                continue
                
            if hasattr(obj, '__tablename__') and hasattr(obj, '__table__'):
                models.append(obj)
                print(f"Found model: {{obj.__name__}} -> {{obj.__tablename__}}", file=sys.stderr)
                
        except Exception as e:
            print(f"Error inspecting {{attr_name}}: {{e}}", file=sys.stderr)
            continue
            
    return models

all_models = []
model_files = {repr(model_files)}

for file_path in model_files:
    print(f"Processing: {{file_path}}", file=sys.stderr)
    module = safe_import_module(file_path)
    models = extract_models_from_module(module)
    all_models.extend(models)

final_metadata = MetaData()
tables_added = set()

for model_class in all_models:
    try:
        if hasattr(model_class, '__table__'):
            table = model_class.__table__
            if table.name not in tables_added:
                table.tometadata(final_metadata)
                tables_added.add(table.name)
                print(f"Added table: {{table.name}}", file=sys.stderr)
                
    except Exception as e:
        print(f"Error processing model {{model_class}}: {{e}}", file=sys.stderr)
        continue

print(f"Total tables found: {{len(final_metadata.tables)}}", file=sys.stderr)

import pickle
import sys
sys.stdout.buffer.write(pickle.dumps(final_metadata))
'''
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', subprocess_script],
                cwd=self.project_path,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                logger.error(f"Subprocess failed with code {result.returncode}")
                logger.error(f"Error output: {error_msg}")
                raise RuntimeError(f"Model discovery failed: {error_msg}")
            
            if not result.stdout:
                logger.warning("No metadata returned from subprocess")
                return MetaData()
                
            metadata = pickle.loads(result.stdout)
            logger.info(f"Successfully discovered {len(metadata.tables)} tables")
            
            return metadata
            
        except subprocess.TimeoutExpired:
            logger.error("Model discovery timed out")
            return MetaData()
        except Exception as e:
            logger.error(f"Failed to discover models: {e}")
            return MetaData()

    def load_from_cache(self, current_hash: str) -> Optional[MetaData]:
        """Load metadata from cache if valid."""
        if not self.use_cache:
            return None
            
        hash_file = self.cache_dir / self.CACHE_HASH_FILE
        cache_file = self.cache_dir / self.CACHE_FILE
        
        if not (hash_file.exists() and cache_file.exists()):
            return None
            
        try:
            with open(hash_file, 'r') as f:
                cached_hash = f.read().strip()
            
            if cached_hash == current_hash:
                with open(cache_file, 'rb') as f:
                    cached_metadata = pickle.load(f)
                logger.info(f"Using cached metadata ({len(cached_metadata.tables)} tables)")
                return cached_metadata
                
        except Exception as e:
            logger.debug(f"Cache read failed: {e}")
            
        return None

    def save_to_cache(self, metadata: MetaData, files_hash: str) -> None:
        """Save metadata to cache."""
        if not self.use_cache:
            return
            
        try:
            self.cache_dir.mkdir(exist_ok=True)
            
            with open(self.cache_dir / self.CACHE_FILE, 'wb') as f:
                pickle.dump(metadata, f)
            
            with open(self.cache_dir / self.CACHE_HASH_FILE, 'w') as f:
                f.write(files_hash)
                
            logger.debug("Results cached successfully")
            
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")

    def discover(self) -> MetaData:
        """
        Main method to discover SQLAlchemy models and return consolidated metadata.
        
        Returns:
            MetaData: Consolidated metadata from all discovered models
        """
        if not self.auto_discovery:
            logger.info("Auto discovery is disabled in config.")
            return MetaData()
        
        logger.info(f"Starting model discovery in: {self.project_path}")
        
        model_files = self.scan_python_files()
        
        if not model_files:
            logger.warning("No potential model files found!")
            if self.debug:
                logger.debug(f"Searched in: {self.project_path}")
                logger.debug(f"Excluded: {self.exclude_dirs}")
            return MetaData()
        
        logger.info(f"Found {len(model_files)} potential model files")
        if self.debug:
            for f in model_files:
                logger.debug(f"  - {f}")
        
        current_hash = self.get_file_hash(model_files)
        
        cached_metadata = self.load_from_cache(current_hash)
        if cached_metadata is not None:
            return cached_metadata
        
        metadata = self.import_models_and_extract_metadata(model_files)
        
        self.save_to_cache(metadata, current_hash)
        
        logger.info(f"Model discovery completed: {len(metadata.tables)} tables found")
        
        if self.debug and metadata.tables:
            logger.debug("Discovered tables:")
            for table_name in metadata.tables.keys():
                logger.debug(f"  - {table_name}")
        
        return metadata

    def clear_cache(self) -> bool:
        """Clear the discovery cache."""
        try:
            if self.cache_dir.exists():
                import shutil
                shutil.rmtree(self.cache_dir)
                logger.info("Cache cleared successfully")
                return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
        
        return True

    def get_cache_info(self) -> dict:
        """Get information about the current cache."""
        info = {
            'cache_exists': False,
            'cache_dir': str(self.cache_dir),
            'files_count': 0,
            'last_hash': None
        }
        
        try:
            if self.cache_dir.exists():
                info['cache_exists'] = True
                
                hash_file = self.cache_dir / self.CACHE_HASH_FILE
                if hash_file.exists():
                    with open(hash_file, 'r') as f:
                        info['last_hash'] = f.read().strip()
                
                cache_file = self.cache_dir / self.CACHE_FILE
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        metadata = pickle.load(f)
                        info['tables_count'] = len(metadata.tables)
                        
        except Exception as e:
            logger.debug(f"Error getting cache info: {e}")
            
        return info



def discover_target_metadata(
    use_cache: bool = True,
    debug: bool = False
) -> MetaData:
    """
    Backward compatibility function for existing code.
    """
    discoverer = ModelDiscoverer(
        use_cache=use_cache,
        debug=debug
    )
    return discoverer.discover()