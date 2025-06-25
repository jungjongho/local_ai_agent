import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FolderIcon, CalendarIcon, DocumentTextIcon, CogIcon, PlayIcon, ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import Card from '../components/Card';
import Button from '../components/Button';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import { projectsApi } from '../services/api';
import { Project, WorkspaceInfo, SystemRequirements } from '../types';

const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [workspaceInfo, setWorkspaceInfo] = useState<WorkspaceInfo | null>(null);
  const [systemRequirements, setSystemRequirements] = useState<SystemRequirements | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadProjects = async () => {
    try {
      setRefreshing(true);
      const response = await projectsApi.listProjects();
      setProjects(response.projects);
    } catch (error) {
      console.error('프로젝트 로딩 실패:', error);
      setError(error instanceof Error ? error.message : '프로젝트를 불러올 수 없습니다.');
    } finally {
      setRefreshing(false);
    }
  };

  const loadWorkspaceInfo = async () => {
    try {
      const info = await projectsApi.getWorkspaceInfo();
      setWorkspaceInfo(info);
    } catch (error) {
      console.error('작업 공간 정보 로딩 실패:', error);
    }
  };

  const loadSystemRequirements = async () => {
    try {
      const requirements = await projectsApi.checkSystemRequirements();
      setSystemRequirements(requirements);
    } catch (error) {
      console.error('시스템 요구사항 확인 실패:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        await Promise.all([
          loadProjects(),
          loadWorkspaceInfo(),
          loadSystemRequirements()
        ]);
      } catch (error) {
        console.error('데이터 로딩 실패:', error);
        setError('데이터를 불러올 수 없습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatBytes = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loading message="프로젝트 정보를 불러오는 중..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">생성된 프로젝트</h1>
          <p className="text-gray-600 mt-2">AI 에이전트가 생성한 웹 서비스 프로젝트들을 관리하세요</p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={loadProjects}
            disabled={refreshing}
            variant="outline"
            className="flex items-center gap-2"
          >
            <ClockIcon className="w-4 h-4" />
            {refreshing ? '새로고침 중...' : '새로고침'}
          </Button>
          <Link to="/workflow">
            <Button className="flex items-center gap-2">
              <PlayIcon className="w-4 h-4" />
              새 프로젝트 생성
            </Button>
          </Link>
        </div>
      </div>

      {/* 시스템 요구사항 경고 */}
      {systemRequirements && !systemRequirements.all_satisfied && (
        <Alert type="warning" className="mb-6">
          <ExclamationTriangleIcon className="w-5 h-5" />
          <div>
            <h3 className="font-medium">시스템 요구사항 미충족</h3>
            <p className="text-sm mt-1">
              일부 프로젝트가 정상적으로 실행되지 않을 수 있습니다. 누락된 의존성을 설치해주세요.
            </p>
            <div className="mt-2 text-xs text-gray-600">
              {Object.entries(systemRequirements.requirements)
                .filter(([_, satisfied]) => !satisfied)
                .map(([req, _]) => req)
                .join(', ')} 필요
            </div>
          </div>
        </Alert>
      )}

      {/* 작업 공간 정보 */}
      {workspaceInfo && (
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FolderIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">작업 공간</h3>
                <p className="text-sm text-gray-600">{workspaceInfo.workspace_dir}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-600">{workspaceInfo.projects_count}개</div>
              <div className="text-sm text-gray-500">생성된 프로젝트</div>
              {workspaceInfo.free_space && (
                <div className="text-xs text-gray-400 mt-1">
                  여유 공간: {formatBytes(workspaceInfo.free_space)}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* 에러 메시지 */}
      {error && (
        <Alert type="error">
          <ExclamationTriangleIcon className="w-5 h-5" />
          <div>
            <h3 className="font-medium">오류 발생</h3>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </Alert>
      )}

      {/* 프로젝트 목록 */}
      {projects.length === 0 ? (
        <Card className="text-center py-12">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <FolderIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">아직 생성된 프로젝트가 없습니다</h3>
          <p className="text-gray-600 mb-6">
            AI 에이전트를 사용해서 첫 번째 웹 서비스를 만들어보세요!
          </p>
          <Link to="/workflow">
            <Button className="inline-flex items-center gap-2">
              <PlayIcon className="w-4 h-4" />
              프로젝트 생성하기
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.name} project={project} />
          ))}
        </div>
      )}
    </div>
  );
};

interface ProjectCardProps {
  project: Project;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = () => {
    const badges = [];
    
    if (project.has_readme) {
      badges.push(
        <span key="readme" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <DocumentTextIcon className="w-3 h-3 mr-1" />
          README
        </span>
      );
    }
    
    if (project.has_docker) {
      badges.push(
        <span key="docker" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <CogIcon className="w-3 h-3 mr-1" />
          Docker
        </span>
      );
    }
    
    if (project.has_scripts) {
      badges.push(
        <span key="scripts" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          <PlayIcon className="w-3 h-3 mr-1" />
          Scripts
        </span>
      );
    }
    
    return badges;
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200 cursor-pointer group">
      <Link to={`/projects/${project.name}`} className="block">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors">
              <FolderIcon className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                {project.name}
              </h3>
              <div className="flex items-center text-sm text-gray-500 mt-1">
                <CalendarIcon className="w-4 h-4 mr-1" />
                {formatDate(project.created_at)}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2 mb-3">
          {getStatusBadge()}
        </div>
        
        <div className="text-xs text-gray-500 truncate">
          {project.path}
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">프로젝트 상세 보기</span>
            <svg className="w-4 h-4 text-gray-400 group-hover:text-indigo-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </Link>
    </Card>
  );
};

export default ProjectsPage;