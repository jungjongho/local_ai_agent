from typing import Dict, Any, List, Optional
import json
from .base import EnhancedBaseAgent


class BackendAgent(EnhancedBaseAgent):
    """Backend 에이전트 - FastAPI + SQLAlchemy 기반 백엔드 코드 생성"""
    
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="backend",
            description="FastAPI + SQLAlchemy + SQLite 기반 백엔드 API를 생성하는 에이전트",
            model=model
        )
    
    def get_system_prompt(self) -> str:
        return """당신은 전문 Backend 개발자 AI 에이전트입니다.

주어진 요구사항을 바탕으로 다음과 같은 작업을 수행해야 합니다:

1. FastAPI 애플리케이션 구조 생성
   - main.py (앱 진입점)
   - routers (API 엔드포인트)
   - models (SQLAlchemy 모델)
   - schemas (Pydantic 스키마)
   - database.py (DB 연결)

2. SQLAlchemy 모델 생성
   - 데이터베이스 테이블 정의
   - 관계 설정 (Foreign Key, Relationship)
   - 인덱스 및 제약조건

3. Pydantic 스키마 생성
   - 요청/응답 데이터 검증
   - CRUD 작업용 스키마
   - 타입 안전성 보장

4. API 엔드포인트 생성
   - RESTful API 설계
   - CRUD 작업 구현
   - 에러 처리
   - HTTP 상태 코드

5. 미들웨어 및 설정
   - CORS 설정
   - 데이터베이스 연결
   - 환경변수 관리

모든 코드는 Python 3.9+ 기준으로 작성하고,
Clean Code 원칙과 RESTful API 설계 원칙을 따르세요."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backend 에이전트 실행"""
        try:
            requirements = input_data.get("requirements_analysis", {})
            project_plan = input_data.get("project_plan", {})
            
            # 1. 프로젝트 설정 파일 생성
            config_files = await self._generate_config_files(requirements)
            
            # 2. 데이터베이스 모델 생성
            models = await self._generate_models(requirements)
            
            # 3. Pydantic 스키마 생성
            schemas = await self._generate_schemas(requirements)
            
            # 4. API 라우터 생성
            routers = await self._generate_routers(requirements)
            
            # 5. 메인 애플리케이션 생성
            main_app = await self._generate_main_app(requirements)
            
            # 6. 데이터베이스 설정 생성
            database_config = await self._generate_database_config()
            
            return {
                "config_files": config_files,
                "models": models,
                "schemas": schemas,
                "routers": routers,
                "main_app": main_app,
                "database_config": database_config,
                "next_agent": "devops"
            }
            
        except Exception as e:
            raise Exception(f"Backend 에이전트 실행 실패: {str(e)}")
    
    async def _generate_config_files(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """프로젝트 설정 파일들 생성"""
        
        # requirements.txt
        requirements_txt = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
sqlite3
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-dotenv==1.0.0
alembic==1.12.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1"""
        
        # .env.example
        env_example = """# Database
DATABASE_URL=sqlite:///./app.db

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Generated API

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30"""
        
        return {
            "requirements.txt": requirements_txt,
            ".env.example": env_example,
            ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
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
MANIFEST
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.DS_Store
*.db
*.sqlite
*.sqlite3"""
        }
    
    async def _generate_models(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """SQLAlchemy 모델 생성"""
        data_models = requirements.get("data_models", [])
        
        if not data_models:
            # 기본 모델 생성
            return {
                "app/models/__init__.py": "",
                "app/models/base.py": self._get_base_model(),
                "app/models/item.py": self._get_default_item_model()
            }
        
        generated_models = {
            "app/models/__init__.py": "",
            "app/models/base.py": self._get_base_model()
        }
        
        for model in data_models:
            model_code = await self._generate_single_model(model)
            model_name = model["name"].lower()
            generated_models[f"app/models/{model_name}.py"] = model_code
        
        return generated_models
    
    async def _generate_single_model(self, model: Dict[str, Any]) -> str:
        """단일 SQLAlchemy 모델 생성"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 데이터 모델을 SQLAlchemy로 구현해주세요:

모델 정보:
{json.dumps(model, indent=2, ensure_ascii=False)}

요구사항:
1. SQLAlchemy 모델 클래스 정의
2. 적절한 컬럼 타입 사용
3. 인덱스 및 제약조건 설정
4. 관계 설정 (필요시)
5. __repr__ 메서드 구현

완전한 SQLAlchemy 모델 코드를 생성해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=1000)
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_fallback_model(model["name"])
    
    async def _generate_schemas(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Pydantic 스키마 생성"""
        data_models = requirements.get("data_models", [])
        
        if not data_models:
            return {
                "app/schemas/__init__.py": "",
                "app/schemas/item.py": self._get_default_item_schema()
            }
        
        generated_schemas = {"app/schemas/__init__.py": ""}
        
        for model in data_models:
            schema_code = await self._generate_single_schema(model)
            model_name = model["name"].lower()
            generated_schemas[f"app/schemas/{model_name}.py"] = schema_code
        
        return generated_schemas
    
    async def _generate_single_schema(self, model: Dict[str, Any]) -> str:
        """단일 Pydantic 스키마 생성"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 데이터 모델에 대한 Pydantic 스키마를 생성해주세요:

모델 정보:
{json.dumps(model, indent=2, ensure_ascii=False)}

요구사항:
1. Base 스키마 (공통 필드)
2. Create 스키마 (생성용)
3. Update 스키마 (수정용)
4. Response 스키마 (응답용)
5. 타입 힌트 및 검증 규칙

완전한 Pydantic 스키마 코드를 생성해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=1000)
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_fallback_schema(model["name"])
    
    async def _generate_routers(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """API 라우터 생성"""
        api_endpoints = requirements.get("api_endpoints", [])
        data_models = requirements.get("data_models", [])
        
        if not api_endpoints:
            return {
                "app/api/__init__.py": "",
                "app/api/v1/__init__.py": "",
                "app/api/v1/api.py": self._get_default_api_router(),
                "app/api/v1/endpoints/__init__.py": "",
                "app/api/v1/endpoints/items.py": self._get_default_items_router()
            }
        
        generated_routers = {
            "app/api/__init__.py": "",
            "app/api/v1/__init__.py": "",
            "app/api/v1/api.py": self._generate_main_api_router(data_models)
        }
        
        # 각 모델별 라우터 생성
        for model in data_models:
            router_code = await self._generate_single_router(model, api_endpoints)
            model_name = model["name"].lower()
            generated_routers[f"app/api/v1/endpoints/{model_name}s.py"] = router_code
        
        return generated_routers
    
    async def _generate_single_router(self, model: Dict[str, Any], api_endpoints: List[Dict[str, Any]]) -> str:
        """단일 API 라우터 생성"""
        model_endpoints = [ep for ep in api_endpoints if model["name"].lower() in ep.get("path", "").lower()]
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 모델에 대한 FastAPI 라우터를 생성해주세요:

모델 정보:
{json.dumps(model, indent=2, ensure_ascii=False)}

관련 API 엔드포인트:
{json.dumps(model_endpoints, indent=2, ensure_ascii=False)}

요구사항:
1. FastAPI APIRouter 사용
2. CRUD 작업 구현
3. 적절한 HTTP 상태 코드
4. 에러 처리
5. 의존성 주입 (데이터베이스 세션)
6. Pydantic 스키마 사용

완전한 FastAPI 라우터 코드를 생성해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=1500)
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_fallback_router(model["name"])
    
    async def _generate_main_app(self, requirements: Dict[str, Any]) -> str:
        """메인 FastAPI 애플리케이션 생성"""
        project_name = requirements.get("project_name", "Generated API")
        
        return f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base
from app.api.v1.api import api_router

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{project_name} API",
    description="자동 생성된 API 서버",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {{"message": "Welcome to {project_name} API"}}

@app.get("/health")
def health_check():
    return {{"status": "healthy"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)"""
    
    async def _generate_database_config(self) -> Dict[str, str]:
        """데이터베이스 설정 생성"""
        return {
            "app/core/__init__.py": "",
            "app/core/config.py": """from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Generated API"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()""",
            "app/db/__init__.py": "",
            "app/db/base.py": """from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()""",
            "app/db/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()"""
        }
    
    def _get_base_model(self) -> str:
        """기본 모델 클래스"""
        return """from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())"""
    
    def _get_default_item_model(self) -> str:
        """기본 Item 모델"""
        return """from sqlalchemy import Column, String, Text, Boolean
from app.models.base import BaseModel

class Item(BaseModel):
    __tablename__ = "items"
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }"""
    
    def _get_default_item_schema(self) -> str:
        """기본 Item 스키마"""
        return """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True"""
    
    def _get_default_api_router(self) -> str:
        """기본 API 라우터"""
        return """from fastapi import APIRouter
from app.api.v1.endpoints import items

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])"""
    
    def _get_default_items_router(self) -> str:
        """기본 Items 라우터"""
        return """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return None"""
    
    def _generate_main_api_router(self, data_models: List[Dict[str, Any]]) -> str:
        """메인 API 라우터 생성"""
        includes = []
        for model in data_models:
            model_name = model["name"].lower()
            includes.append(f"""from app.api.v1.endpoints import {model_name}s
api_router.include_router({model_name}s.router, prefix="/{model_name}s", tags=["{model_name}s"])""")
        
        return f"""from fastapi import APIRouter

api_router = APIRouter()

{chr(10).join(includes)}"""
    
    def _get_fallback_model(self, name: str) -> str:
        """기본 모델 템플릿"""
        return f"""from sqlalchemy import Column, String, Text, Boolean
from app.models.base import BaseModel

class {name}(BaseModel):
    __tablename__ = "{name.lower()}s"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<{name}(id={{self.id}}, name='{{self.name}}')>"
    
    def to_dict(self):
        return {{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }}"""
    
    def _get_fallback_schema(self, name: str) -> str:
        """기본 스키마 템플릿"""
        return f"""from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class {name}Base(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class {name}Create({name}Base):
    pass

class {name}Update(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class {name}Response({name}Base):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True"""
    
    def _get_fallback_router(self, name: str) -> str:
        """기본 라우터 템플릿"""
        model_name = name.lower()
        return f"""from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.{model_name} import {name}
from app.schemas.{model_name} import {name}Create, {name}Update, {name}Response

router = APIRouter()

@router.get("/", response_model=List[{name}Response])
def read_{model_name}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query({name}).offset(skip).limit(limit).all()
    return items

@router.get("/{{item_id}}", response_model={name}Response)
def read_{model_name}(item_id: int, db: Session = Depends(get_db)):
    item = db.query({name}).filter({name}.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="{name} not found")
    return item

@router.post("/", response_model={name}Response, status_code=status.HTTP_201_CREATED)
def create_{model_name}(item: {name}Create, db: Session = Depends(get_db)):
    db_item = {name}(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{{item_id}}", response_model={name}Response)
def update_{model_name}(item_id: int, item: {name}Update, db: Session = Depends(get_db)):
    db_item = db.query({name}).filter({name}.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="{name} not found")
    
    update_data = item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{model_name}(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query({name}).filter({name}.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="{name} not found")
    
    db.delete(db_item)
    db.commit()
    return None"""
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        required_fields = ["requirements_analysis"]
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        return True
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        required_fields = ["config_files", "models", "schemas", "routers", "main_app", "database_config"]
        
        for field in required_fields:
            if field not in output_data:
                return False
        
        return True
