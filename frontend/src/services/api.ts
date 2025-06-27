import axios from 'axios';
import {
WorkflowCreate,
WorkflowResponse,
WorkflowStatusDetails,
WorkflowStatistics,
ModelInfo,
Project,
ProjectInfo,
WorkspaceInfo,
SystemRequirements,
  FileContent
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30초 타임아웃
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response.data;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.data || error.message);
    
    // 에러 메시지 정리
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        '알 수 없는 오류가 발생했습니다.';
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Workflow API
export const workflowApi = {
  // 새로운 워크플로 생성
  createWorkflow: async (data: WorkflowCreate): Promise<WorkflowResponse> => {
    return api.post('/api/v1/workflows/', data);
  },

  // 워크플로 상태 조회
  getWorkflowStatus: async (workflowId: string): Promise<WorkflowStatusDetails> => {
    return api.get(`/api/v1/workflows/${workflowId}`);
  },

  // 활성 워크플로 목록
  listWorkflows: async (): Promise<{ workflows: WorkflowStatusDetails[], total: number }> => {
    return api.get('/api/v1/workflows/');
  },

  // 워크플로 취소
  cancelWorkflow: async (workflowId: string): Promise<{ message: string }> => {
    return api.delete(`/api/v1/workflows/${workflowId}`);
  },

  // 워크플로 통계
  getStatistics: async (): Promise<WorkflowStatistics> => {
    return api.get('/api/v1/workflows/statistics/summary');
  },

  // 완료된 워크플로 정리
  cleanupWorkflows: async (maxAgeHours: number = 24): Promise<{ message: string, cleaned_count: number }> => {
    return api.post(`/api/v1/workflows/cleanup?max_age_hours=${maxAgeHours}`);
  },

  // 워크플로 진행상황 스트림 (EventSource 사용)
  streamProgress: (workflowId: string): EventSource => {
    const eventSource = new EventSource(`${API_BASE_URL}/api/v1/workflows/${workflowId}/stream`);
    return eventSource;
  }
};

// Projects API
export const projectsApi = {
  // 프로젝트 목록 조회
  listProjects: async (): Promise<{ projects: Project[], total: number }> => {
    return api.get('/api/v1/projects/');
  },

  // 프로젝트 정보 조회
  getProjectInfo: async (projectId: string): Promise<ProjectInfo> => {
    return api.get(`/api/v1/projects/${projectId}`);
  },

  // 프로젝트 시작
  startProject: async (projectId: string): Promise<{ message: string, frontend_url?: string, backend_url?: string, project_id: string }> => {
    return api.post(`/api/v1/projects/${projectId}/start`);
  },

  // 프로젝트 중지
  stopProject: async (projectId: string): Promise<{ message: string }> => {
    return api.post(`/api/v1/projects/${projectId}/stop`);
  },

  // 프로젝트 삭제
  deleteProject: async (projectId: string): Promise<{ message: string }> => {
    return api.delete(`/api/v1/projects/${projectId}`);
  },

  // 프로젝트 로그 조회
  getProjectLogs: async (projectId: string): Promise<{ [key: string]: string }> => {
    return api.get(`/api/v1/projects/${projectId}/logs`);
  },

  // 작업 공간 정보
  getWorkspaceInfo: async (): Promise<WorkspaceInfo> => {
    return api.get('/api/v1/projects/workspace/info');
  },

  // 시스템 요구사항 확인
  checkSystemRequirements: async (): Promise<SystemRequirements> => {
    return api.get('/api/v1/projects/workspace/requirements');
  },

  // 프로젝트 파일 내용 조회
  getProjectFile: async (projectId: string, filePath: string): Promise<FileContent> => {
    return api.get(`/api/v1/projects/${projectId}/files`, {
      params: { file_path: filePath }
    });
  }
};

// Models API
export const modelsApi = {
  // 사용 가능한 모델 목록 조회
  getAvailableModels: async (): Promise<ModelInfo[]> => {
    return api.get('/api/v1/models/');
  },

  // 특정 모델 정보 조회
  getModelInfo: async (modelId: string): Promise<ModelInfo> => {
    return api.get(`/api/v1/models/${modelId}`);
  },

  // 현재 기본 모델 조회
  getCurrentModel: async (): Promise<ModelInfo> => {
    return api.get('/api/v1/models/current/default');
  }
};

// System API
export const systemApi = {
  // 헬스 체크
  healthCheck: async (): Promise<any> => {
    return api.get('/health');
  },

  // API 상태
  getApiStatus: async (): Promise<any> => {
    return api.get('/api/v1/status');
  },

  // 루트 정보
  getRootInfo: async (): Promise<any> => {
    return api.get('/');
  }
};

export default api;
