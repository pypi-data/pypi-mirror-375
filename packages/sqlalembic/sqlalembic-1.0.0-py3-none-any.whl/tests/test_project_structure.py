import pytest
from unittest.mock import patch, MagicMock
from sqlalembic.core.project_structure import ProjectStructure

@pytest.fixture
def temp_project_dir(tmp_path):
    return tmp_path

@pytest.fixture
def mock_templates(temp_project_dir):
    template_dir = temp_project_dir / 'conf'
    alembic_template_dir = template_dir / 'alembic_template'
    project_template_dir = template_dir / 'project_templates'

    alembic_template_dir.mkdir(parents=True)
    project_template_dir.mkdir(parents=True)

    (alembic_template_dir / 'alembic.ini.template').write_text(
        '[alembic]\n'
        'script_location = %(here)s/{{ project_name }}\n'
        'prepend_sys_path = .\n'
        'version_path_separator = os\n'
        'sqlalchemy.url = {{ database_url }}\n'
        '[loggers]\n'
        'keys = root,sqlalchemy,alembic\n'
    )
    (project_template_dir / 'manage.py.template').write_text('# {{ project_name }} management\nfrom {{ project_name }} import app\n')
    (alembic_template_dir / 'env.py.template').write_text('# Alembic env for {{ project_name }}\npass')
    (project_template_dir / 'env.template').write_text('DATABASE_URL={{ database_url }}\nDEBUG={{ debug_mode }}')
    (alembic_template_dir / 'script.py.mako.template').write_text('"""${message}"""\nrevision = ${repr(up_revision)}\n')
    (alembic_template_dir / 'README.md.template').write_text('# {{ project_name_title }}\n\nProject: {{ project_name }}')
    
    (alembic_template_dir / 'test.png').write_bytes(b'fake_binary_content')
    
    return template_dir

@pytest.fixture
def clean_project(temp_project_dir, mock_templates):
    project_name = "test_project"
    project = ProjectStructure(name=project_name)
    project.template_dir = mock_templates
    return project


def test_valid_project_names():
    """Test valid project name validation."""
    project = ProjectStructure(name="my_project")
    assert project._is_valid_project_name("my_project")
    assert project._is_valid_project_name("my-project-name")
    assert project._is_valid_project_name("my_project_1")
    assert project._is_valid_project_name("myproject")

def test_invalid_project_names():
    """Test invalid project name validation."""
    with pytest.raises(ValueError, match="Invalid project name"):
        ProjectStructure(name="1project")
    with pytest.raises(ValueError, match="Invalid project name"):
        ProjectStructure(name="my project")
    with pytest.raises(ValueError, match="Invalid project name"):
        ProjectStructure(name="my@project")
    with pytest.raises(ValueError, match="Invalid project name"):
        ProjectStructure(name="")


def test_startproject_success(clean_project, temp_project_dir):
    """Test successful project creation."""
    clean_project.startproject(target_dir=str(temp_project_dir))

    project_path = temp_project_dir / "test_project"
    assert project_path.exists()
    assert (project_path / "versions").exists()
    assert (project_path / "env.py").exists()
    assert (project_path / "script.py.mako").exists()
    assert (project_path / "README.md").exists()
    assert (temp_project_dir / "alembic.ini").exists()
    assert (temp_project_dir / "manage.py").exists()
    assert (temp_project_dir / ".env").exists()

def test_startproject_project_exists_no_force(clean_project, temp_project_dir):
    """Test failure when project exists and force is False."""
    (temp_project_dir / "test_project").mkdir()
    result = clean_project.startproject(target_dir=str(temp_project_dir), force=False)
    assert result is False
    
def test_startproject_project_exists_with_force(clean_project, temp_project_dir):
    """Test successful overwrite with force=True."""
    existing_project = temp_project_dir / "test_project"
    existing_project.mkdir()
    (existing_project / "old_file.txt").write_text("old content")
    
    clean_project.startproject(target_dir=str(temp_project_dir), force=True)
    assert existing_project.exists()
    assert not (existing_project / "old_file.txt").exists()
    assert (temp_project_dir / "manage.py").exists()


def test_validate_project_success(clean_project, temp_project_dir):
    """Test successful project validation after creation."""
    clean_project.startproject(target_dir=str(temp_project_dir))
    
    project_path = temp_project_dir / "test_project"
    result = clean_project.validate_project(project_path=str(project_path))
    assert result is True

def test_validate_project_failure_missing_file(clean_project, temp_project_dir):
    """Test failure when a required file is missing."""
    clean_project.startproject(target_dir=str(temp_project_dir))
    
    project_path = temp_project_dir / "test_project"
    (temp_project_dir / "alembic.ini").unlink()
    
    result = clean_project.validate_project(project_path=str(project_path))
    assert result is False
    

def test_update_alembic_ini_success(clean_project, temp_project_dir):
    """Test successful update of alembic.ini."""
    clean_project.startproject(target_dir=str(temp_project_dir))
    
    ini_path = temp_project_dir / "alembic.ini"
    assert ini_path.exists()
    
    content = ini_path.read_text()
    assert f"script_location = %(here)s/{clean_project.name}" in content

def test_update_alembic_ini_file_not_found(clean_project, temp_project_dir):
    """Test update_alembic_ini when file doesn't exist."""
    project_path = temp_project_dir / "test_project"
    project_path.mkdir()
    
    result = clean_project.update_alembic_ini(project_path)
    assert result is False

def test_copy_template_success_text_file(clean_project, temp_project_dir, mock_templates):
    """Test successful copy of a text template file."""
    dest_path = temp_project_dir / 'output.ini'
    
    result = clean_project._copy_template('alembic_template/alembic.ini.template', dest_path)
    assert result is True
    
    assert dest_path.exists()
    content = dest_path.read_text()
    assert '{{ project_name }}' not in content
    assert 'test_project' in content

def test_copy_template_success_binary_file(clean_project, temp_project_dir, mock_templates):
    """Test successful copy of a binary template file."""
    dest_path = temp_project_dir / 'output.png'

    result = clean_project._copy_template('alembic_template/test.png', dest_path)
    assert result is True
    
    assert dest_path.exists()
    assert dest_path.read_bytes() == b'fake_binary_content'

def test_copy_template_failure_template_not_found(clean_project, temp_project_dir):
    """Test failure when template file does not exist."""
    dest_path = temp_project_dir / 'output.txt'
    result = clean_project._copy_template("non_existent.template", dest_path)
    assert result is False

def test_process_template_variables(clean_project):
    """Test template variable processing."""
    content = "Project: {{ project_name }}, Title: {{ project_name_title }}"
    processed = clean_project._process_template_variables(content)
    
    assert "{{ project_name }}" not in processed
    assert "test_project" in processed
    assert "TestProject" in processed

def test_process_template_variables_with_config(temp_project_dir, mock_templates):
    """Test template variable processing with config."""
    mock_config = MagicMock()
    mock_config.DATABASE_URI = "postgresql://localhost/testdb"
    mock_config.DB_ENGINE = "postgresql"
    mock_config.DEBUG = False
    
    project = ProjectStructure(name="test_project", config=mock_config)
    project.template_dir = mock_templates
    
    content = "DB: {{ database_url }}, Engine: {{ database_engine }}, Debug: {{ debug_mode }}"
    processed = project._process_template_variables(content)
    
    assert "postgresql://localhost/testdb" in processed
    assert "postgresql" in processed
    assert "false" in processed

@patch('sqlalembic.core.project_structure.logger')
def test_startproject_exception_handling(mock_logger, clean_project, temp_project_dir):
    """Test exception handling in startproject."""
    with patch.object(clean_project, '_create_project_structure', side_effect=Exception("Test error")):
        result = clean_project.startproject(target_dir=str(temp_project_dir))
        assert result is False
        mock_logger.exception.assert_called()

def test_create_project_structure_creates_directories(clean_project, temp_project_dir):
    """Test that _create_project_structure creates required directories."""
    project_path = temp_project_dir / "test_project"
    
    result = clean_project._create_project_structure(project_path)
    assert result is True
    
    assert project_path.exists()
    assert (project_path / "versions").exists()

def test_validate_project_current_directory(clean_project, temp_project_dir):
    """Test validate_project with current directory (no project_path specified)."""
    clean_project.startproject(target_dir=str(temp_project_dir))
    
    project_path = temp_project_dir / "test_project"
    
    with patch('pathlib.Path.cwd', return_value=project_path):
        result = clean_project.validate_project()
        assert result is True