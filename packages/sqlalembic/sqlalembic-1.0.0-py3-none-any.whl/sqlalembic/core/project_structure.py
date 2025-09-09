import logging
import shutil
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class ProjectStructure:
    """
    Enhanced project structure management with better error handling,
    template processing, and configuration integration.
    """
    
    def __init__(self, name: str, config: Optional[Any] = None):
        """
        Initialize project structure manager.
        
        Args:
            name: Project name
            config: Configuration object (optional)
        """
        self.name = name
        self.config = config
        self.template_dir = Path(__file__).parent.parent / 'conf'
        
        if not self._is_valid_project_name(name):
            raise ValueError(f"Invalid project name: {name}")
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name according to Python conventions."""
        if not name:
            return False
        if not name.replace('_', '').replace('-', '').isalnum():
            return False
        if name[0].isdigit():
            return False
        return True
    
    def startproject(self, target_dir: Optional[str] = None, force: bool = False) -> bool:
        """
        Create a new project structure with enhanced options.
        
        Args:
            target_dir: Target directory (defaults to current directory)
            force: Overwrite existing project if True
            
        Returns:
            bool: True if successful, False otherwise
        """
        base_dir = Path(target_dir) if target_dir else Path.cwd()
        project_path = base_dir / self.name
        
        logger.info(f"Creating new SqlAlembic project: {self.name}")
        logger.info(f"Target location: {project_path}")
        
        if project_path.exists():
            if not force:
                logger.error(f"Project '{self.name}' already exists at {project_path}")
                logger.info("Use --force to overwrite existing project")
                return False
            else:
                logger.warning(f"Overwriting existing project at {project_path}")
                shutil.rmtree(project_path)
        
        try:
            success = self._create_project_structure(project_path)
            if success:
                self.update_alembic_ini(project_path)
                logger.info(f"Project '{self.name}' created successfully!")
            
        except Exception as e:
            logger.exception(f"Failed to create project '{self.name}': {e}")
            if project_path.exists():
                shutil.rmtree(project_path, ignore_errors=True)
            return False
    
    def _create_project_structure(self, project_path: Path) -> bool:
        """
        Create the complete project directory structure.
        
        Args:
            project_path: Path where project should be created
            
        Returns:
            bool: True if successful
        """
        logger.info(f"Creating project structure at {project_path}")
        
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            
            versions_dir = project_path / 'versions'
            versions_dir.mkdir(exist_ok=True)
            
            
            templates_to_copy = [
                ('alembic_template/alembic.ini.template', project_path / '../alembic.ini'),
                ('alembic_template/env.py.template', project_path / 'env.py'),
                ('alembic_template/script.py.mako.template', project_path / 'script.py.mako'),
                
                ('project_templates/manage.py.template', project_path / '../manage.py'),
                ('project_templates/env.template', project_path / '../.env'),
                
            ]
            
            for template_path, destination_path in templates_to_copy:
                if not self._copy_template(template_path, destination_path):
                    return False
            
            logger.info("Project structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating project structure: {e}")
            return False
    
    def _copy_template(self, template_path: str, destination_path: Path) -> bool:
        """
        Copy and process a template file.
        
        Args:
            template_path: Relative path to template file
            destination_path: Destination path
            
        Returns:
            bool: True if successful
        """
        try:
            template_full_path = self.template_dir / template_path
            
            if not template_full_path.exists():
                logger.error(f"Template file not found: {template_full_path}")
                return False
            
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            if template_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico')):
                shutil.copy2(template_full_path, destination_path)
                logger.debug(f"Copied binary template: {template_path}")
                
            else:
                with open(template_full_path, 'r', encoding='utf-8') as template_file:
                    content = template_file.read()
                
                content = self._process_template_variables(content)
                
                with open(destination_path, 'w', encoding='utf-8') as destination_file:
                    destination_file.write(content)
                
                logger.debug(f"Processed template: {template_path} -> {destination_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing template {template_path}: {e}")
            return False
    
    def _process_template_variables(self, content: str) -> str:
        """
        Process template variables in content.
        
        Args:
            content: Template content
            
        Returns:
            str: Processed content
        """
        template_vars = {
            'project_name': self.name,
            'project_name_title': self.name.title().replace('_', '').replace('-', ''),
            'project_name_upper': self.name.upper().replace('-', '_'),
            'project_name_lower': self.name.lower().replace('-', '_'),
        }
        
        if self.config:
            template_vars.update({
                'database_url': getattr(self.config, 'DATABASE_URI', 'sqlite:///app.db'),
                'database_engine': getattr(self.config, 'DB_ENGINE', 'sqlite'),
                'debug_mode': str(getattr(self.config, 'DEBUG', True)).lower(),
            })
        
        for var, value in template_vars.items():
            content = content.replace(f'{{{{ {var} }}}}', str(value))
            content = content.replace(f'{{{{{var}}}}}', str(value))
        
        return content
    
    def validate_project(self, project_path: Optional[str] = None) -> bool:
        """
        Validate that a project structure is complete and valid.
        
        Args:
            project_path: Path to project (defaults to current directory)
            
        Returns:
            bool: True if valid
        """
        if project_path:
            path = Path(project_path)
        else:
            path = Path.cwd()
        
        logger.info(f"Validating project structure at: {path}")
        
        required_files = [
            '../alembic.ini',
            'env.py',
            'script.py.mako',
            'versions',
            '../.env',
            '../manage.py',
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error("Project validation failed. Missing files:")
            for missing in missing_files:
                logger.error(f"  - {missing}")
            return False
        
        logger.info("Project structure validation passed")
        return True
    

    def update_alembic_ini(self, project_path: Path) -> bool:
        """
        Update alembic.ini with the correct script_location based on project name.
        """
        try:
            ini_file = project_path.parent / "alembic.ini"
            print(ini_file)

            if not ini_file.exists():
                logger.error(f"alembic.ini not found at {ini_file}")
                return False

            lines = ini_file.read_text(encoding="utf-8").splitlines()

            if len(lines) >= 6:
                lines[5] = f"script_location = %(here)s/{self.name}"
            else:
                logger.error("alembic.ini does not have enough lines to update")
                return False

            ini_file.write_text("\n".join(lines), encoding="utf-8")
            logger.info(f"Updated alembic.ini with script_location = %(here)s/{self.name}")
            return True

        except Exception as e:
            logger.error(f"Error updating alembic.ini: {e}")
            return False