"""
PawnStack Init 도구

프로젝트 초기화 및 템플릿 생성 도구
"""

import os
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import BaseCLI
from pawnstack.cli.banner import generate_banner

# 모듈 메타데이터
__description__ = 'Project initialization and template generator'

__epilog__ = (
    "Initialize new projects with templates and configurations.\n\n"
    "Usage examples:\n"
    "  1. Initialize Python project:\n\tpawns init python --name my_project\n\n"
    "  2. Initialize Docker project:\n\tpawns init docker --name my_app\n\n"
    "  3. Initialize config files:\n\tpawns init config --type yaml\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class InitConfig:
    """초기화 설정"""
    project_type: str = "python"
    name: str = ""
    path: str = "."
    template: str = "basic"
    force: bool = False


class InitCLI(BaseCLI):
    """Init CLI"""
    
    def __init__(self, args=None):
        super().__init__(args)
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('project_type', help='Project type to initialize', 
                          choices=['python', 'docker', 'config', 'cli'], nargs='?', default='python')
        
        parser.add_argument('--name', type=str, help='Project name', required=True)
        parser.add_argument('--path', type=str, help='Project path (default: current directory)', default='.')
        parser.add_argument('--template', type=str, help='Template type (default: basic)', default='basic')
        parser.add_argument('--force', action='store_true', help='Force overwrite existing files')
        
        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          help='Logging level (default: INFO)', default="INFO")
    
    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'init'
        
        pawn.set(
            PAWN_LOGGER=dict(
                log_level=getattr(args, 'log_level', 'INFO'),
                stdout_level=getattr(args, 'log_level', 'INFO'),
                stdout=True,
                use_hook_exception=True,
                show_path=False,
            ),
            PAWN_CONSOLE=dict(
                redirect=True,
                record=True,
            ),
            app_name=app_name,
            args=args,
        )
    
    def print_banner(self):
        """배너 출력"""
        banner = generate_banner(
            app_name="Init",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)
    
    def create_config(self) -> InitConfig:
        """설정 객체 생성"""
        return InitConfig(
            project_type=getattr(self.args, 'project_type', 'python'),
            name=getattr(self.args, 'name', ''),
            path=getattr(self.args, 'path', '.'),
            template=getattr(self.args, 'template', 'basic'),
            force=getattr(self.args, 'force', False)
        )
    
    def create_directory(self, path: str) -> bool:
        """디렉토리 생성"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            self.log_error(f"Failed to create directory {path}: {e}")
            return False
    
    def write_file(self, filepath: str, content: str, config: InitConfig) -> bool:
        """파일 작성"""
        if os.path.exists(filepath) and not config.force:
            self.log_warning(f"File already exists: {filepath} (use --force to overwrite)")
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            pawn.console.log(f"[green]✅ Created: {filepath}[/green]")
            return True
        except Exception as e:
            self.log_error(f"Failed to write file {filepath}: {e}")
            return False
    
    def init_python_project(self, config: InitConfig):
        """Python 프로젝트 초기화"""
        project_path = os.path.join(config.path, config.name)
        
        pawn.console.log(f"🐍 Initializing Python project: {config.name}")
        
        # 디렉토리 구조 생성
        directories = [
            project_path,
            os.path.join(project_path, config.name),
            os.path.join(project_path, 'tests'),
            os.path.join(project_path, 'docs'),
        ]
        
        for directory in directories:
            self.create_directory(directory)
        
        # 파일 생성
        files = {
            'README.md': f"""# {config.name}

A Python project created with PawnStack.

## Installation

```bash
pip install -e .
```

## Usage

```python
import {config.name}
```

## Development

```bash
pip install -r requirements.dev.txt
pytest
```
""",
            'pyproject.toml': f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{config.name}"
version = "0.1.0"
description = "A Python project created with PawnStack"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "flake8",
    "mypy",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
            'requirements.txt': '# Add your dependencies here\n',
            'requirements.dev.txt': """pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
""",
            f'{config.name}/__init__.py': f'''"""
{config.name}

A Python project created with PawnStack.
"""

__version__ = "0.1.0"
''',
            f'{config.name}/main.py': f'''"""
Main module for {config.name}
"""


def main():
    """Main function"""
    print("Hello from {config.name}!")


if __name__ == "__main__":
    main()
''',
            'tests/__init__.py': '',
            'tests/test_main.py': f'''"""
Tests for {config.name}
"""

import pytest
from {config.name} import main


def test_main():
    """Test main function"""
    # Add your tests here
    assert True
''',
            '.gitignore': """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        }
        
        for filename, content in files.items():
            filepath = os.path.join(project_path, filename)
            self.write_file(filepath, content, config)
        
        pawn.console.log(f"[green]🎉 Python project '{config.name}' created successfully![/green]")
        pawn.console.log(f"📁 Project location: {project_path}")
        pawn.console.log(f"🚀 Next steps:")
        pawn.console.log(f"   cd {config.name}")
        pawn.console.log(f"   pip install -e .")
        pawn.console.log(f"   python -m {config.name}.main")
    
    def init_docker_project(self, config: InitConfig):
        """Docker 프로젝트 초기화"""
        project_path = os.path.join(config.path, config.name)
        
        pawn.console.log(f"🐳 Initializing Docker project: {config.name}")
        
        self.create_directory(project_path)
        
        files = {
            'Dockerfile': f"""FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
""",
            'docker-compose.yml': f"""version: '3.8'

services:
  {config.name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
""",
            'requirements.txt': """flask>=2.0.0
redis>=4.0.0
""",
            'app.py': f'''"""
{config.name} - Docker application
"""

from flask import Flask, jsonify
import redis
import os

app = Flask(__name__)

# Redis connection
try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
except:
    r = None

@app.route('/')
def hello():
    return jsonify({{
        "message": "Hello from {config.name}!",
        "status": "running"
    }})

@app.route('/health')
def health():
    redis_status = "connected" if r and r.ping() else "disconnected"
    return jsonify({{
        "status": "healthy",
        "redis": redis_status
    }})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
''',
            'README.md': f"""# {config.name}

A Docker application created with PawnStack.

## Quick Start

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run with Docker
docker build -t {config.name} .
docker run -p 8000:8000 {config.name}
```

## Endpoints

- `GET /` - Hello message
- `GET /health` - Health check

## Development

```bash
pip install -r requirements.txt
python app.py
```
""",
            '.dockerignore': """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
"""
        }
        
        for filename, content in files.items():
            filepath = os.path.join(project_path, filename)
            self.write_file(filepath, content, config)
        
        pawn.console.log(f"[green]🎉 Docker project '{config.name}' created successfully![/green]")
        pawn.console.log(f"📁 Project location: {project_path}")
        pawn.console.log(f"🚀 Next steps:")
        pawn.console.log(f"   cd {config.name}")
        pawn.console.log(f"   docker-compose up --build")
    
    def init_config_files(self, config: InitConfig):
        """설정 파일 초기화"""
        pawn.console.log(f"⚙️  Initializing config files for: {config.name}")
        
        files = {
            'config.yaml': f"""# {config.name} Configuration
app:
  name: {config.name}
  version: "1.0.0"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  host: "localhost"
  port: 5432
  name: "{config.name}_db"
  user: "user"
  password: "password"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/{config.name}.log"

redis:
  host: "localhost"
  port: 6379
  db: 0
""",
            'config.ini': f"""[app]
name = {config.name}
version = 1.0.0
debug = false

[server]
host = 0.0.0.0
port = 8000
workers = 4

[database]
host = localhost
port = 5432
name = {config.name}_db
user = user
password = password

[logging]
level = INFO
format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
file = logs/{config.name}.log

[redis]
host = localhost
port = 6379
db = 0
""",
            '.env': f"""# {config.name} Environment Variables
APP_NAME={config.name}
APP_VERSION=1.0.0
DEBUG=false

SERVER_HOST=0.0.0.0
SERVER_PORT=8000

DATABASE_URL=postgresql://user:password@localhost:5432/{config.name}_db
REDIS_URL=redis://localhost:6379/0

LOG_LEVEL=INFO
""",
            'docker-compose.override.yml': f"""# Development overrides
version: '3.8'

services:
  {config.name}:
    environment:
      - DEBUG=true
    volumes:
      - .:/app
    command: python app.py --reload
"""
        }
        
        for filename, content in files.items():
            filepath = os.path.join(config.path, filename)
            self.write_file(filepath, content, config)
        
        pawn.console.log(f"[green]🎉 Config files created successfully![/green]")
    
    def run(self) -> int:
        """Init CLI 실행"""
        self.setup_config()
        self.print_banner()
        
        config = self.create_config()
        
        if not config.name:
            self.log_error("Project name is required (--name)")
            return 1
        
        if config.project_type == "python":
            self.init_python_project(config)
        elif config.project_type == "docker":
            self.init_docker_project(config)
        elif config.project_type == "config":
            self.init_config_files(config)
        else:
            self.log_error(f"Unknown project type: {config.project_type}")
            return 1
        
        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = InitCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = InitCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())