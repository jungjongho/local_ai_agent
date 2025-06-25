import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MCPFilesystemClient:
    """MCP 파일시스템 클라이언트 - 실제 파일 조작을 담당"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
    async def create_project_directory(self, project_name: str) -> str:
        """프로젝트 디렉토리 생성"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_dir_name = f"{project_name}_{timestamp}"
            project_path = self.workspace_path / project_dir_name
            
            project_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"프로젝트 디렉토리 생성됨: {project_path}")
            return str(project_path)
            
        except Exception as e:
            logger.error(f"프로젝트 디렉토리 생성 실패: {e}")
            raise
    
    async def create_file_structure(self, project_path: str, structure: Dict[str, Any]) -> List[str]:
        """전체 프로젝트 파일 구조 생성"""
        created_files = []
        base_path = Path(project_path)
        
        try:
            for path, content in structure.items():
                file_path = base_path / path
                
                # 디렉토리 생성
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 파일 생성
                if isinstance(content, str):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                
                created_files.append(str(file_path))
                logger.info(f"파일 생성됨: {file_path}")
            
            return created_files
            
        except Exception as e:
            logger.error(f"파일 구조 생성 실패: {e}")
            raise
    
    async def write_file(self, file_path: str, content: str) -> bool:
        """단일 파일 작성"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"파일 작성됨: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"파일 작성 실패: {e}")
            return False
    
    async def copy_template(self, template_name: str, destination: str) -> bool:
        """템플릿 파일 복사"""
        try:
            # 템플릿 경로는 실제 환경에 맞게 수정 필요
            template_path = Path(__file__).parent.parent / "templates" / template_name
            dest_path = Path(destination)
            
            if template_path.exists():
                shutil.copy2(template_path, dest_path)
                logger.info(f"템플릿 복사됨: {template_path} -> {dest_path}")
                return True
            else:
                logger.warning(f"템플릿 파일 없음: {template_path}")
                return False
                
        except Exception as e:
            logger.error(f"템플릿 복사 실패: {e}")
            return False
    
    async def read_file(self, file_path: str) -> Optional[str]:
        """파일 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"파일 읽기 실패: {e}")
            return None
    
    async def list_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """디렉토리 내용 조회"""
        try:
            path = Path(directory_path)
            items = []
            
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return items
            
        except Exception as e:
            logger.error(f"디렉토리 조회 실패: {e}")
            return []


class MCPGitClient:
    """MCP Git 클라이언트 - Git 조작을 담당"""
    
    async def init_repository(self, project_path: str) -> bool:
        """Git 저장소 초기화"""
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Git 저장소 초기화됨: {project_path}")
                return True
            else:
                logger.error(f"Git 초기화 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Git 초기화 실패: {e}")
            return False
    
    async def create_gitignore(self, project_path: str, template: str = "node_python") -> bool:
        """gitignore 파일 생성"""
        try:
            gitignore_content = self._get_gitignore_template(template)
            gitignore_path = Path(project_path) / ".gitignore"
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            logger.info(f"gitignore 파일 생성됨: {gitignore_path}")
            return True
            
        except Exception as e:
            logger.error(f"gitignore 생성 실패: {e}")
            return False
    
    async def create_initial_commit(self, project_path: str, message: str = "Initial commit") -> bool:
        """초기 커밋 생성"""
        try:
            # git add .
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                logger.error(f"git add 실패: {add_result.stderr}")
                return False
            
            # git commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode == 0:
                logger.info(f"초기 커밋 생성됨: {project_path}")
                return True
            else:
                logger.error(f"git commit 실패: {commit_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"초기 커밋 실패: {e}")
            return False
    
    def _get_gitignore_template(self, template: str) -> str:
        """gitignore 템플릿 반환"""
        templates = {
            "node_python": '''# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
'''
        }
        return templates.get(template, templates["node_python"])


class MCPDockerClient:
    """MCP Docker 클라이언트 - Docker 조작을 담당"""
    
    async def create_dockerfile(self, project_path: str, service_type: str, content: str) -> bool:
        """Dockerfile 생성"""
        try:
            dockerfile_path = Path(project_path) / f"Dockerfile.{service_type}"
            
            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Dockerfile 생성됨: {dockerfile_path}")
            return True
            
        except Exception as e:
            logger.error(f"Dockerfile 생성 실패: {e}")
            return False
    
    async def create_docker_compose(self, project_path: str, content: str) -> bool:
        """Docker Compose 파일 생성"""
        try:
            compose_path = Path(project_path) / "docker-compose.yml"
            
            with open(compose_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Docker Compose 파일 생성됨: {compose_path}")
            return True
            
        except Exception as e:
            logger.error(f"Docker Compose 생성 실패: {e}")
            return False
    
    async def build_containers(self, project_path: str) -> bool:
        """Docker 컨테이너 빌드"""
        try:
            result = subprocess.run(
                ["docker-compose", "build"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Docker 컨테이너 빌드 완료: {project_path}")
                return True
            else:
                logger.error(f"Docker 빌드 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Docker 빌드 실패: {e}")
            return False
    
    async def start_services(self, project_path: str) -> bool:
        """Docker 서비스 시작"""
        try:
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Docker 서비스 시작됨: {project_path}")
                return True
            else:
                logger.error(f"Docker 서비스 시작 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Docker 서비스 시작 실패: {e}")
            return False
    
    async def stop_services(self, project_path: str) -> bool:
        """Docker 서비스 중지"""
        try:
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Docker 서비스 중지됨: {project_path}")
                return True
            else:
                logger.error(f"Docker 서비스 중지 실패: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Docker 서비스 중지 실패: {e}")
            return False


class MCPEnvironmentClient:
    """MCP 환경 클라이언트 - 환경 설정을 담당"""
    
    async def create_env_files(self, project_path: str, env_configs: Dict[str, Dict[str, str]]) -> bool:
        """환경변수 파일들 생성"""
        try:
            for env_name, config in env_configs.items():
                env_file_path = Path(project_path) / f".env.{env_name}"
                
                with open(env_file_path, 'w', encoding='utf-8') as f:
                    for key, value in config.items():
                        f.write(f"{key}={value}\n")
                
                logger.info(f"환경파일 생성됨: {env_file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"환경파일 생성 실패: {e}")
            return False
    
    async def setup_development(self, project_path: str) -> bool:
        """개발 환경 설정"""
        try:
            # 개발용 환경변수 설정
            dev_env = {
                "NODE_ENV": "development",
                "DEBUG": "true",
                "API_URL": "http://localhost:8025",
                "DATABASE_URL": "sqlite:///./dev.db"
            }
            
            env_file_path = Path(project_path) / ".env.development"
            
            with open(env_file_path, 'w', encoding='utf-8') as f:
                for key, value in dev_env.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"개발 환경 설정 완료: {env_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"개발 환경 설정 실패: {e}")
            return False
    
    async def install_dependencies(self, project_path: str, package_manager: str = "auto") -> bool:
        """패키지 의존성 설치"""
        try:
            path = Path(project_path)
            
            # Frontend 의존성 설치
            frontend_path = path / "frontend"
            if frontend_path.exists() and (frontend_path / "package.json").exists():
                npm_result = subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_path,
                    capture_output=True,
                    text=True
                )
                
                if npm_result.returncode != 0:
                    logger.error(f"npm install 실패: {npm_result.stderr}")
                    return False
                
                logger.info(f"Frontend 의존성 설치 완료: {frontend_path}")
            
            # Backend 의존성 설치
            backend_path = path / "backend"
            if backend_path.exists() and (backend_path / "requirements.txt").exists():
                pip_result = subprocess.run(
                    ["pip", "install", "-r", "requirements.txt"],
                    cwd=backend_path,
                    capture_output=True,
                    text=True
                )
                
                if pip_result.returncode != 0:
                    logger.error(f"pip install 실패: {pip_result.stderr}")
                    return False
                
                logger.info(f"Backend 의존성 설치 완료: {backend_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"의존성 설치 실패: {e}")
            return False


class MCPManager:
    """MCP 클라이언트들을 통합 관리하는 매니저"""
    
    def __init__(self, workspace_path: str):
        self.filesystem = MCPFilesystemClient(workspace_path)
        self.git = MCPGitClient()
        self.docker = MCPDockerClient()
        self.environment = MCPEnvironmentClient()
    
    async def create_complete_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """완전한 프로젝트 생성 (모든 MCP 도구 활용)"""
        try:
            project_name = project_data["project_name"]
            
            # 1. 프로젝트 디렉토리 생성
            project_path = await self.filesystem.create_project_directory(project_name)
            
            # 2. 파일 구조 생성
            files_created = await self.filesystem.create_file_structure(
                project_path, 
                project_data["file_structure"]
            )
            
            # 3. Git 초기화
            await self.git.init_repository(project_path)
            await self.git.create_gitignore(project_path)
            
            # 4. Docker 설정
            if "docker_compose" in project_data:
                await self.docker.create_docker_compose(
                    project_path, 
                    project_data["docker_compose"]
                )
            
            # 5. 환경 설정
            if "environment" in project_data:
                await self.environment.create_env_files(
                    project_path, 
                    project_data["environment"]
                )
            
            # 6. 개발 환경 설정
            await self.environment.setup_development(project_path)
            
            # 7. 의존성 설치
            await self.environment.install_dependencies(project_path)
            
            # 8. 초기 커밋
            await self.git.create_initial_commit(project_path, "Initial project setup")
            
            return {
                "success": True,
                "project_path": project_path,
                "files_created": files_created,
                "message": "프로젝트가 성공적으로 생성되었습니다."
            }
            
        except Exception as e:
            logger.error(f"프로젝트 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "프로젝트 생성 중 오류가 발생했습니다."
            }
    
    async def start_project_services(self, project_path: str) -> Dict[str, Any]:
        """프로젝트 서비스 시작"""
        try:
            # Docker Compose 존재 확인
            compose_path = Path(project_path) / "docker-compose.yml"
            
            if compose_path.exists():
                # Docker로 서비스 시작
                success = await self.docker.start_services(project_path)
                
                if success:
                    return {
                    "success": True,
                    "message": "서비스가 성공적으로 시작되었습니다.",
                    "frontend_url": "http://localhost:3025",
                    "backend_url": "http://localhost:8025"
                    }
            else:
                # 직접 서비스 시작 (개발 모드)
                return await self._start_development_servers(project_path)
                
        except Exception as e:
            logger.error(f"서비스 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "서비스 시작 중 오류가 발생했습니다."
            }
    
    async def _start_development_servers(self, project_path: str) -> Dict[str, Any]:
        """개발 서버들 직접 시작"""
        try:
            path = Path(project_path)
            
            # Frontend 서버 시작
            frontend_path = path / "frontend"
            if frontend_path.exists():
                subprocess.Popen(
                    ["npm", "start"],
                    cwd=frontend_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Backend 서버 시작
            backend_path = path / "backend"
            if backend_path.exists():
                subprocess.Popen(
                    ["uvicorn", "main:app", "--reload", "--port", "8000"],
                    cwd=backend_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            return {
                "success": True,
                "message": "개발 서버가 시작되었습니다.",
                "frontend_url": "http://localhost:3025",
                "backend_url": "http://localhost:8025"
            }
            
        except Exception as e:
            logger.error(f"개발 서버 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class MCPProjectClient:
    """프로젝트 관리를 위한 MCP 클라이언트 - 프로젝트 CRUD 및 상태 관리"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.mcp_manager = MCPManager(workspace_path)
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """생성된 프로젝트 목록 조회"""
        try:
            projects = []
            
            for project_dir in self.workspace_path.iterdir():
                if project_dir.is_dir():
                    project_info = await self._get_project_info(project_dir)
                    if project_info:
                        projects.append(project_info)
            
            # 최신 생성 순으로 정렬
            projects.sort(key=lambda x: x['created_at'], reverse=True)
            
            return projects
            
        except Exception as e:
            logger.error(f"프로젝트 목록 조회 실패: {e}")
            return []
    
    async def get_project_detail(self, project_id: str) -> Optional[Dict[str, Any]]:
        """특정 프로젝트 상세 정보 조회"""
        try:
            project_path = self._find_project_path(project_id)
            if not project_path:
                return None
            
            project_info = await self._get_project_info(project_path)
            if project_info:
                # 파일 구조 추가
                project_info['file_structure'] = await self._get_file_structure(project_path)
                # 서비스 상태 추가
                project_info['service_status'] = await self._get_service_status(project_path)
            
            return project_info
            
        except Exception as e:
            logger.error(f"프로젝트 상세 조회 실패: {e}")
            return None
    
    async def delete_project(self, project_id: str) -> bool:
        """프로젝트 삭제"""
        try:
            project_path = self._find_project_path(project_id)
            if not project_path:
                return False
            
            # 실행 중인 서비스 중지
            await self.stop_project_services(project_id)
            
            # 프로젝트 디렉토리 삭제
            shutil.rmtree(project_path)
            
            logger.info(f"프로젝트 삭제됨: {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"프로젝트 삭제 실패: {e}")
            return False
    
    async def start_project_services(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 서비스 시작"""
        try:
            project_path = self._find_project_path(project_id)
            if not project_path:
                return {
                    "success": False,
                    "error": "프로젝트를 찾을 수 없습니다."
                }
            
            return await self.mcp_manager.start_project_services(str(project_path))
            
        except Exception as e:
            logger.error(f"서비스 시작 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_project_services(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 서비스 중지"""
        try:
            project_path = self._find_project_path(project_id)
            if not project_path:
                return {
                    "success": False,
                    "error": "프로젝트를 찾을 수 없습니다."
                }
            
            # Docker Compose가 있으면 Docker로 중지
            compose_path = project_path / "docker-compose.yml"
            if compose_path.exists():
                success = await self.mcp_manager.docker.stop_services(str(project_path))
                return {
                    "success": success,
                    "message": "서비스가 중지되었습니다." if success else "서비스 중지 실패"
                }
            else:
                # 개발 서버 프로세스 종료 (포트 기반)
                await self._kill_development_servers()
                return {
                    "success": True,
                    "message": "개발 서버가 중지되었습니다."
                }
                
        except Exception as e:
            logger.error(f"서비스 중지 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_project_logs(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 로그 조회"""
        try:
            project_path = self._find_project_path(project_id)
            if not project_path:
                return {
                    "success": False,
                    "error": "프로젝트를 찾을 수 없습니다."
                }
            
            logs = {}
            
            # 로그 파일들 확인
            log_files = [
                "frontend/npm-debug.log",
                "backend/app.log",
                "docker-compose.log"
            ]
            
            for log_file in log_files:
                log_path = project_path / log_file
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8') as f:
                        logs[log_file] = f.read()[-1000:]  # 마지막 1000자만
            
            return {
                "success": True,
                "logs": logs
            }
            
        except Exception as e:
            logger.error(f"로그 조회 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_project_path(self, project_id: str) -> Optional[Path]:
        """프로젝트 ID로 프로젝트 경로 찾기"""
        for project_dir in self.workspace_path.iterdir():
            if project_dir.is_dir() and project_id in project_dir.name:
                return project_dir
        return None
    
    async def _get_project_info(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """프로젝트 정보 추출"""
        try:
            # 프로젝트 메타데이터 파일 확인
            metadata_path = project_path / "project.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # 기본 정보 설정
            stat = project_path.stat()
            
            # README.md에서 설명 추출
            readme_path = project_path / "README.md"
            description = "웹 애플리케이션"
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 첫 번째 문단을 설명으로 사용
                    lines = content.split('\n')
                    for line in lines[1:]:  # 첫 번째 줄(제목) 제외
                        if line.strip():
                            description = line.strip()
                            break
            
            return {
                "id": project_path.name,
                "name": metadata.get("name", self._extract_project_name(project_path.name)),
                "description": metadata.get("description", description),
                "path": str(project_path),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": self._calculate_directory_size(project_path),
                "technologies": self._detect_technologies(project_path),
                "status": await self._get_project_status(project_path)
            }
            
        except Exception as e:
            logger.error(f"프로젝트 정보 추출 실패: {e}")
            return None
    
    def _extract_project_name(self, dir_name: str) -> str:
        """디렉토리 이름에서 프로젝트 이름 추출"""
        # timestamp 패턴 제거
        import re
        name = re.sub(r'_\d{8}_\d{6}', '', dir_name)
        return name.replace('_', ' ').title()
    
    def _calculate_directory_size(self, path: Path) -> int:
        """디렉토리 크기 계산"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total
    
    def _detect_technologies(self, project_path: Path) -> List[str]:
        """프로젝트에서 사용된 기술 감지"""
        technologies = []
        
        # package.json 확인 (React/Node.js)
        if (project_path / "frontend" / "package.json").exists():
            technologies.append("React")
            technologies.append("Node.js")
        
        # requirements.txt 확인 (Python)
        if (project_path / "backend" / "requirements.txt").exists():
            technologies.append("Python")
            # FastAPI 확인
            try:
                with open(project_path / "backend" / "requirements.txt", 'r') as f:
                    if "fastapi" in f.read().lower():
                        technologies.append("FastAPI")
            except Exception:
                pass
        
        # Docker 확인
        if (project_path / "docker-compose.yml").exists():
            technologies.append("Docker")
        
        # TailwindCSS 확인
        if (project_path / "frontend" / "tailwind.config.js").exists():
            technologies.append("TailwindCSS")
        
        return technologies
    
    async def _get_project_status(self, project_path: Path) -> str:
        """프로젝트 상태 확인"""
        try:
            # 서비스 실행 중인지 확인
            service_status = await self._get_service_status(project_path)
            
            if service_status.get("frontend_running") or service_status.get("backend_running"):
                return "running"
            else:
                return "stopped"
                
        except Exception:
            return "unknown"
    
    async def _get_service_status(self, project_path: Path) -> Dict[str, bool]:
        """서비스 실행 상태 확인"""
        try:
            status = {
                "frontend_running": False,
                "backend_running": False
            }
            
            # 포트 확인으로 서비스 실행 여부 판단
            import socket
            
            # Frontend 포트 (3025) 확인
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', 3025))
                status["frontend_running"] = (result == 0)
                sock.close()
            except Exception:
                pass
            
            # Backend 포트 (8025) 확인
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', 8025))
                status["backend_running"] = (result == 0)
                sock.close()
            except Exception:
                pass
            
            return status
            
        except Exception as e:
            logger.error(f"서비스 상태 확인 실패: {e}")
            return {"frontend_running": False, "backend_running": False}
    
    async def _get_file_structure(self, project_path: Path) -> Dict[str, Any]:
        """프로젝트 파일 구조 생성"""
        def build_tree(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}
            
            tree = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.') and item.name not in ['.env.example', '.gitignore']:
                        continue
                    
                    if item.is_dir():
                        if item.name not in ['node_modules', '__pycache__', '.git', 'dist', 'build']:
                            tree[item.name] = {
                                "type": "directory",
                                "children": build_tree(item, max_depth, current_depth + 1)
                            }
                    else:
                        tree[item.name] = {
                            "type": "file",
                            "size": item.stat().st_size
                        }
            except Exception:
                pass
            
            return tree
        
        return build_tree(project_path)
    
    async def _kill_development_servers(self) -> None:
        """개발 서버 프로세스 종료"""
        try:
            import psutil
            
            # 포트 3025, 8025에서 실행 중인 프로세스 찾아서 종료
            for port in [3025, 8025]:
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'connections']):
                        try:
                            for conn in proc.info['connections'] or []:
                                if conn.laddr.port == port:
                                    proc.terminate()
                                    logger.info(f"포트 {port}의 프로세스 종료: PID {proc.pid}")
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            continue
                except Exception as e:
                    logger.warning(f"포트 {port} 프로세스 종료 중 오류: {e}")
                    
        except ImportError:
            # psutil이 없으면 subprocess로 대체
            try:
                # kill processes on ports
                subprocess.run(["lsof", "-ti:3025"], capture_output=True)
                subprocess.run(["lsof", "-ti:8025"], capture_output=True)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"개발 서버 종료 실패: {e}")
