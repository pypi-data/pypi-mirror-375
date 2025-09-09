import pytest
import pickle
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlalchemy import MetaData, Table, Column, Integer
from sqlalembic.integrations.alembic_setup import ModelDiscoverer, discover_target_metadata

@pytest.fixture
def temp_project_dir(tmp_path):
    """إنشاء مجلد مؤقت للمشروع."""
    return tmp_path

@pytest.fixture
def mock_config():
    """Mock config object."""
    config = MagicMock()
    config.project_root = None
    config.EXCLUDE_PATHS = None
    config.AUTO_DISCOVER_MODELS = True
    return config

@pytest.fixture
def sample_model_files(temp_project_dir):
    """إنشاء ملفات نماذج للاختبار."""
    models_dir = temp_project_dir / "models"
    models_dir.mkdir()
    
    valid_model = models_dir / "user.py"
    valid_model.write_text("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
""")
    
    product_model = models_dir / "product.py"
    product_model.write_text("""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship("User")
""")
    
    utils_file = models_dir / "utils.py"
    utils_file.write_text("""
def helper_function():
    return "no models here"
    
class NotAModel:
    def __init__(self):
        self.data = "just a regular class"
""")
    
    invalid_file = models_dir / "invalid.py"
    invalid_file.write_text("""
from sqlalchemy import Column
class BrokenModel(
    # syntax error here
""")
    
    return {
        'valid_model': str(valid_model),
        'product_model': str(product_model),
        'utils_file': str(utils_file),
        'invalid_file': str(invalid_file),
        'models_dir': str(models_dir)
    }

@pytest.fixture
def discoverer(temp_project_dir, mock_config):
    """إنشاء ModelDiscoverer للاختبار."""
    with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
        with patch('os.getcwd', return_value=str(temp_project_dir)):
            return ModelDiscoverer(use_cache=False, debug=True)

class TestModelDiscoverer:
    
    def test_initialization(self, temp_project_dir, mock_config):
        """اختبار تهيئة ModelDiscoverer."""
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            with patch('os.getcwd', return_value=str(temp_project_dir)):
                discoverer = ModelDiscoverer(use_cache=False, debug=True)
        
        assert discoverer.project_path == str(temp_project_dir.resolve())
        assert not discoverer.use_cache
        assert discoverer.debug
        assert discoverer.auto_discovery

    def test_is_sqlalchemy_file_valid(self, discoverer, sample_model_files):
        """اختبار تحديد ملفات SQLAlchemy الصحيحة."""
        assert discoverer.is_sqlalchemy_file(sample_model_files['valid_model'])
        assert discoverer.is_sqlalchemy_file(sample_model_files['product_model'])

    def test_is_sqlalchemy_file_invalid(self, discoverer, sample_model_files):
        """اختبار رفض الملفات التي لا تحتوي على نماذج."""
        assert not discoverer.is_sqlalchemy_file(sample_model_files['utils_file'])

    def test_is_sqlalchemy_file_syntax_error(self, discoverer, sample_model_files):
        """اختبار التعامل مع ملفات بها أخطاء syntax."""
        assert not discoverer.is_sqlalchemy_file(sample_model_files['invalid_file'])

    def test_is_sqlalchemy_file_nonexistent(self, discoverer):
        """اختبار التعامل مع ملف غير موجود."""
        assert not discoverer.is_sqlalchemy_file("/path/to/nonexistent/file.py")

    def test_scan_python_files(self, discoverer, sample_model_files):
        """اختبار فحص ملفات Python."""
        model_files = discoverer.scan_python_files()
        
        model_paths = [Path(f).name for f in model_files]
        assert "user.py" in model_paths
        assert "product.py" in model_paths
        assert "utils.py" not in model_paths

    def test_scan_python_files_exclude_dirs(self, temp_project_dir, mock_config):
        """اختبار استبعاد مجلدات معينة."""
        venv_dir = temp_project_dir / "venv"
        venv_dir.mkdir()
        venv_model = venv_dir / "model.py"
        venv_model.write_text("""
from sqlalchemy import Column, Integer
class TestModel:
    __tablename__ = 'test'
    id = Column(Integer)
""")
        
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            with patch('os.getcwd', return_value=str(temp_project_dir)):
                discoverer = ModelDiscoverer()
        
        model_files = discoverer.scan_python_files()
        
        assert str(venv_model) not in model_files

    def test_get_file_hash(self, discoverer, sample_model_files):
        """اختبار حساب hash للملفات."""
        files = [sample_model_files['valid_model'], sample_model_files['product_model']]
        hash1 = discoverer.get_file_hash(files)
        hash2 = discoverer.get_file_hash(files)
        
        assert hash1 == hash2
        assert len(hash1) == 32

    def test_get_file_hash_different_files(self, discoverer, sample_model_files):
        """اختبار أن ملفات مختلفة تعطي hash مختلف."""
        files1 = [sample_model_files['valid_model']]
        files2 = [sample_model_files['product_model']]
        
        hash1 = discoverer.get_file_hash(files1)
        hash2 = discoverer.get_file_hash(files2)
        
        assert hash1 != hash2

    def test_get_file_hash_missing_file(self, discoverer):
        """اختبار التعامل مع ملف مفقود في hash calculation."""
        files = ["/nonexistent/file.py"]
        hash_result = discoverer.get_file_hash(files)
        
        assert len(hash_result) == 32

    def test_load_from_cache_no_cache(self, discoverer):
        """اختبار عدم وجود cache."""
        result = discoverer.load_from_cache("some_hash")
        assert result is None

    def test_load_from_cache_disabled(self, temp_project_dir, mock_config):
        """اختبار تعطيل الـ cache."""
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            with patch('os.getcwd', return_value=str(temp_project_dir)):
                discoverer = ModelDiscoverer(use_cache=False)
        
        result = discoverer.load_from_cache("some_hash")
        assert result is None


    def test_save_cache_disabled(self, temp_project_dir, mock_config):
        """اختبار عدم حفظ cache عند التعطيل."""
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            with patch('os.getcwd', return_value=str(temp_project_dir)):
                discoverer = ModelDiscoverer(use_cache=False)
        
        metadata = MetaData()
        discoverer.save_to_cache(metadata, "test_hash")
        
        assert not discoverer.cache_dir.exists()

    def test_clear_cache(self, discoverer):
        """اختبار مسح الـ cache."""
        discoverer.cache_dir.mkdir(exist_ok=True)
        (discoverer.cache_dir / "test_file").write_text("test")
        
        assert discoverer.cache_dir.exists()
        
        result = discoverer.clear_cache()
        assert result is True
        assert not discoverer.cache_dir.exists()

    def test_clear_cache_nonexistent(self, discoverer):
        """اختبار مسح cache غير موجود."""
        result = discoverer.clear_cache()
        assert result is True

    def test_get_cache_info_no_cache(self, discoverer):
        """اختبار معلومات cache غير موجود."""
        info = discoverer.get_cache_info()
        
        assert not info['cache_exists']
        assert info['files_count'] == 0
        assert info['last_hash'] is None


    @patch('subprocess.run')
    def test_import_models_and_extract_metadata_success(self, mock_subprocess, discoverer):
        """اختبار نجاح استخراج metadata من subprocess."""
        test_metadata = MetaData()
        Table('test_table', test_metadata, Column('id', Integer))
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = pickle.dumps(test_metadata)
        mock_result.stderr = b""
        mock_subprocess.return_value = mock_result
        
        result = discoverer.import_models_and_extract_metadata(['test_file.py'])
        
        assert isinstance(result, MetaData)
        assert len(result.tables) == 1

    @patch('subprocess.run')
    def test_import_models_and_extract_metadata_subprocess_error(self, mock_subprocess, discoverer):
        """اختبار التعامل مع خطأ في subprocess."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b""
        mock_result.stderr = b"ImportError: Module not found"
        mock_subprocess.return_value = mock_result
        
        result = discoverer.import_models_and_extract_metadata(['test_file.py'])
        
        assert isinstance(result, MetaData)
        assert len(result.tables) == 0

    @patch('subprocess.run')
    def test_import_models_timeout(self, mock_subprocess, discoverer):
        """اختبار التعامل مع timeout في subprocess."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd=['python'], timeout=30)
        
        result = discoverer.import_models_and_extract_metadata(['test_file.py'])
        
        assert isinstance(result, MetaData)
        assert len(result.tables) == 0

    def test_discover_auto_discovery_disabled(self, temp_project_dir):
        """اختبار عدم الاكتشاف عند تعطيل auto_discovery."""
        mock_config = MagicMock()
        mock_config.project_root = str(temp_project_dir)
        mock_config.EXCLUDE_PATHS = None
        mock_config.AUTO_DISCOVER_MODELS = False
        
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            discoverer = ModelDiscoverer()
        
        result = discoverer.discover()
        
        assert isinstance(result, MetaData)
        assert len(result.tables) == 0

    def test_discover_no_model_files(self, discoverer):
        """اختبار عدم وجود ملفات نماذج."""
        with patch.object(discoverer, 'scan_python_files', return_value=[]):
            result = discoverer.discover()
        
        assert isinstance(result, MetaData)
        assert len(result.tables) == 0

    def test_discover_with_cache_hit(self, discoverer):
        """اختبار استخدام cache عند وجوده."""
        cached_metadata = MetaData()
        Table('cached_table', cached_metadata, Column('id', Integer))
        
        test_files = ['test.py']
        test_hash = "cached_hash"
        
        with patch.object(discoverer, 'scan_python_files', return_value=test_files):
            with patch.object(discoverer, 'get_file_hash', return_value=test_hash):
                with patch.object(discoverer, 'load_from_cache', return_value=cached_metadata):
                    result = discoverer.discover()
        
        assert result is cached_metadata
        assert 'cached_table' in result.tables

    def test_discover_with_cache_miss(self, discoverer):
        """اختبار عدم وجود cache صالح."""
        fresh_metadata = MetaData()
        Table('fresh_table', fresh_metadata, Column('id', Integer))
        
        test_files = ['test.py']
        test_hash = "new_hash"
        
        with patch.object(discoverer, 'scan_python_files', return_value=test_files):
            with patch.object(discoverer, 'get_file_hash', return_value=test_hash):
                with patch.object(discoverer, 'load_from_cache', return_value=None):
                    with patch.object(discoverer, 'import_models_and_extract_metadata', return_value=fresh_metadata):
                        with patch.object(discoverer, 'save_to_cache') as mock_save:
                            result = discoverer.discover()
        
        assert result is fresh_metadata
        mock_save.assert_called_once_with(fresh_metadata, test_hash)

    def test_is_sqlalchemy_file_with_different_imports(self, discoverer, temp_project_dir):
        """اختبار أنواع مختلفة من imports لـ SQLAlchemy."""
        test_file = temp_project_dir / "test_import.py"
        test_file.write_text("""
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TestModel(Base):
    __tablename__ = 'test'
    id = sa.Column(sa.Integer)
""")
        
        assert discoverer.is_sqlalchemy_file(str(test_file))

    def test_is_sqlalchemy_file_table_definition(self, discoverer, temp_project_dir):
        """اختبار التعرف على Table definitions."""
        test_file = temp_project_dir / "test_table.py"
        test_file.write_text("""
from sqlalchemy import Table, MetaData, Column, Integer

metadata = MetaData()

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True)
)
""")
        
        assert discoverer.is_sqlalchemy_file(str(test_file))

    def test_is_sqlalchemy_file_no_indicators(self, discoverer, temp_project_dir):
        """اختبار ملف بدون أي مؤشرات SQLAlchemy."""
        test_file = temp_project_dir / "normal_file.py"
        test_file.write_text("""
def normal_function():
    return "nothing special"

class RegularClass:
    def __init__(self):
        self.data = "normal class"
""")
        
        assert not discoverer.is_sqlalchemy_file(str(test_file))

    def test_exclude_dirs_default(self, temp_project_dir, mock_config):
        """اختبار المجلدات المستبعدة افتراضياً."""
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            with patch('os.getcwd', return_value=str(temp_project_dir)):
                discoverer = ModelDiscoverer()
        
        expected_excludes = {
            "venv", ".venv", "__pycache__", "env", ".env", 
            "Lib", "Include", "Scripts", ".git", 
            "migrations", "alembic", "versions"
        }
        
        assert expected_excludes.issubset(discoverer.exclude_dirs)

    def test_cache_operations_io_error(self, discoverer):
        """اختبار التعامل مع أخطاء IO في cache operations."""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            discoverer.save_to_cache(MetaData(), "test_hash")
            
            result = discoverer.load_from_cache("test_hash")
            assert result is None

class TestDiscoverTargetMetadata:
    
    @patch('sqlalembic.integrations.alembic_setup.ModelDiscoverer')
    def test_discover_target_metadata_default_params(self, mock_discoverer_class):
        """اختبار الدالة للتوافق مع الإصدارات السابقة."""
        mock_discoverer = MagicMock()
        mock_metadata = MetaData()
        mock_discoverer.discover.return_value = mock_metadata
        mock_discoverer_class.return_value = mock_discoverer
        
        result = discover_target_metadata()
        
        mock_discoverer_class.assert_called_once_with(use_cache=True, debug=False)
        mock_discoverer.discover.assert_called_once()
        assert result is mock_metadata

    @patch('sqlalembic.integrations.alembic_setup.ModelDiscoverer')
    def test_discover_target_metadata_custom_params(self, mock_discoverer_class):
        """اختبار الدالة مع معاملات مخصصة."""
        mock_discoverer = MagicMock()
        mock_discoverer_class.return_value = mock_discoverer
        
        discover_target_metadata(use_cache=False, debug=True)
        
        mock_discoverer_class.assert_called_once_with(use_cache=False, debug=True)

class TestModelDiscovererIntegration:
    
    def test_full_discovery_process(self, temp_project_dir, sample_model_files):
        """اختبار العملية الكاملة للاكتشاف."""
        mock_config = MagicMock()
        mock_config.project_root = str(temp_project_dir)
        mock_config.EXCLUDE_PATHS = None
        mock_config.AUTO_DISCOVER_MODELS = True
        
        with patch('sqlalembic.integrations.alembic_setup.Config', return_value=mock_config):
            discoverer = ModelDiscoverer(use_cache=False, debug=True)
        
        test_metadata = MetaData()
        Table('users', test_metadata, Column('id', Integer))
        
        with patch.object(discoverer, 'import_models_and_extract_metadata', return_value=test_metadata):
            result = discoverer.discover()
        
        assert isinstance(result, MetaData)
        assert len(result.tables) >= 0



class TestDiscovererFixtures:
    
    def test_sample_model_files_structure(self, sample_model_files):
        """اختبار أن sample_model_files تم إنشاؤها بشكل صحيح."""
        assert 'valid_model' in sample_model_files
        assert 'product_model' in sample_model_files
        assert 'utils_file' in sample_model_files
        assert 'invalid_file' in sample_model_files
        
        for file_path in sample_model_files.values():
            if file_path != sample_model_files['models_dir']:
                assert Path(file_path).exists()

    def test_mock_config_values(self, mock_config):
        """اختبار قيم mock_config."""
        assert mock_config.project_root is None
        assert mock_config.EXCLUDE_PATHS is None
        assert mock_config.AUTO_DISCOVER_MODELS is True