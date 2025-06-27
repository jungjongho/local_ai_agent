// Workflow 관련 타입들
export interface ModelInfo {
  id: string;
  name: string;
  description: string;
  context_length: number;
  pricing: {
    input: string;
    output: string;
  };
  capabilities: string[];
  best_for: string[];
  speed: string;
  cost: string;
  is_default: boolean;
}

export interface WorkflowCreate {
  user_input: string;
  project_name?: string;
  model?: string;
}

export interface WorkflowResponse {
  id: string;
  status: WorkflowStatus;
  message: string;
  created_at: string;
}

export enum WorkflowStatus {
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface WorkflowProgress {
  workflow_id: string;
  stage: string;
  progress_percentage: number;
  current_agent: string;
  message: string;
  timestamp: string;
  stage_results?: any;
  error?: string;
}

export interface WorkflowStatusDetails {
  id: string;
  status: WorkflowStatus;
  current_stage: string;
  progress_percentage: number;
  created_at: string;
  completed_at?: string;
  error?: {
    type: string;
    message: string;
    timestamp: string;
  };
  project_name: string;
  latest_progress?: WorkflowProgress;
}

// Project 관련 타입들
export interface Project {
  id: string;
  name: string;
  description: string;
  path: string;
  created_at: string;
  modified_at: string;
  size: number;
  technologies: string[];
  status: 'running' | 'stopped' | 'unknown';
}

export interface ProjectInfo extends Project {
  project_name: string;
  project_path: string;
  created_at: number;
  env_files: Record<string, boolean>;
  docker_files: Record<string, boolean>;
  scripts: Record<string, boolean>;
  package_info?: {
    name: string;
    version: string;
    description?: string;
    scripts?: Record<string, string>;
  };
  readme_content?: string;
  file_structure?: Record<string, any>;
  service_status?: {
    frontend_running: boolean;
    backend_running: boolean;
  };
}

// API 응답 타입들
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface WorkflowStatistics {
  total_workflows: number;
  status_breakdown: Record<string, number>;
  active_agents: string[];
  average_completion_time?: number;
}

export interface WorkspaceInfo {
  workspace_path: string;
  projects_count: number;
  exists: boolean;
}

// UI 상태 관련 타입들
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: string;
}

// Agent 관련 타입들
export interface Agent {
  name: string;
  description: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
}

// 파일 내용 타입
export interface FileContent {
  file_path: string;
  content: string;
  project_name: string;
}

// 시스템 요구사항 타입
export interface SystemRequirements {
  requirements: Record<string, boolean>;
  all_satisfied: boolean;
  missing: string[];
}
