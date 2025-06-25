import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  RocketLaunchIcon, 
  CogIcon, 
  FolderIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import Card from '../components/Card';
import Button from '../components/Button';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import { systemApi, workflowApi, projectsApi } from '../services/api';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 병렬로 데이터 로드
      const [systemData, workflowStats, projectsList] = await Promise.all([
        systemApi.getApiStatus().catch(() => null),
        workflowApi.getStatistics().catch(() => null),
        projectsApi.listProjects().catch(() => ({ projects: [], total: 0 }))
      ]);

      setSystemStatus(systemData);
      setStats(workflowStats);
      setProjects(projectsList.projects.slice(0, 5)); // 최근 5개만 표시
    } catch (err) {
      setError('대시보드 데이터를 불러오는데 실패했습니다.');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading text="대시보드 로딩 중..." />;
  }

  const features = [
    {
      icon: RocketLaunchIcon,
      title: '빠른 프로젝트 생성',
      description: '사용자 입력 한 줄로 5분 내에 완전한 웹서비스를 자동 생성합니다.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      icon: CogIcon,
      title: 'AI 에이전트 협업',
      description: 'PM, UI/UX, Frontend, Backend, DevOps 에이전트가 협력하여 작업합니다.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      icon: FolderIcon,
      title: '실제 파일 생성',
      description: 'MCP를 통해 실제 로컬 파일 시스템에 프로젝트 파일을 생성합니다.',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  ];

  return (
    <div className="space-y-8">
      {/* 에러 표시 */}
      {error && (
        <Alert 
          type="error" 
          message={error} 
          onRetry={loadDashboardData}
          onClose={() => setError(null)}
        />
      )}

      {/* 헤로 섹션 */}
      <div className="text-center py-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white">
        <RocketLaunchIcon className="w-16 h-16 mx-auto mb-4 opacity-90" />
        <h1 className="text-4xl font-bold mb-4">
          멀티 AI 에이전트 웹서비스 생성 시스템
        </h1>
        <p className="text-xl opacity-90 mb-8 max-w-3xl mx-auto">
          사용자 입력 한 줄로 React + FastAPI 기반의 완전한 웹서비스를 자동 생성하는 
          혁신적인 AI 에이전트 시스템입니다.
        </p>
        <div className="flex justify-center space-x-4">
          <Link to="/workflow">
            <Button variant="secondary" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
              지금 시작하기
            </Button>
          </Link>
          <Link to="/projects">
            <Button variant="secondary" size="lg" className="bg-blue-500 text-white hover:bg-blue-400 border-white">
              프로젝트 보기
            </Button>
          </Link>
        </div>
      </div>

      {/* 시스템 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-4">
            <CheckCircleIcon className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">시스템 상태</h3>
          <p className="text-sm text-gray-600">
            {systemStatus ? '정상 운영 중' : '상태 확인 중...'}
          </p>
          {systemStatus && (
            <div className="mt-2 text-xs text-gray-500">
              API v{systemStatus.api_version} 
            </div>
          )}
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-4">
            <ChartBarIcon className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">총 워크플로</h3>
          <p className="text-2xl font-bold text-blue-600">
            {stats?.total_workflows || 0}
          </p>
          <p className="text-sm text-gray-600">개 생성됨</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-4">
            <FolderIcon className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">생성된 프로젝트</h3>
          <p className="text-2xl font-bold text-purple-600">
            {projects.length}
          </p>
          <p className="text-sm text-gray-600">개 프로젝트</p>
        </Card>
      </div>

      {/* 주요 기능 */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">주요 기능</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="text-center" hover>
                <div className={`inline-flex items-center justify-center w-12 h-12 ${feature.bgColor} rounded-lg mb-4`}>
                  <Icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* 최근 프로젝트 */}
      {projects.length > 0 && (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">최근 프로젝트</h2>
            <Link to="/projects">
              <Button variant="secondary" size="sm">전체 보기</Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project, index) => (
              <Card key={index} hover className="transition-all duration-200">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 truncate">{project.name}</h3>
                  <div className="flex items-center text-xs text-gray-500">
                    <ClockIcon className="w-3 h-3 mr-1" />
                    {new Date(project.created_at * 1000).toLocaleDateString()}
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-xs text-gray-600">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-1 ${project.has_docker ? 'bg-green-400' : 'bg-gray-300'}`} />
                    Docker
                  </div>
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-1 ${project.has_scripts ? 'bg-green-400' : 'bg-gray-300'}`} />
                    Scripts
                  </div>
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-1 ${project.has_readme ? 'bg-green-400' : 'bg-gray-300'}`} />
                    README
                  </div>
                </div>
                <div className="mt-3">
                  <Link to={`/projects/${project.name}`}>
                    <Button variant="secondary" size="sm" className="w-full text-sm">
                      자세히 보기
                    </Button>
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 워크플로 상태 */}
      {stats && stats.status_breakdown && Object.keys(stats.status_breakdown).length > 0 && (
        <Card title="워크플로 상태 현황">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.status_breakdown).map(([status, count]) => (
              <div key={status} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{count as number}</div>
                <div className="text-sm text-gray-600 capitalize">{status}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 시작하기 섹션 */}
      <Card className="text-center bg-gradient-to-r from-gray-50 to-blue-50">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          지금 바로 웹서비스를 만들어보세요!
        </h2>
        <p className="text-gray-600 mb-6">
          아이디어를 한 줄로 입력하면 AI 에이전트들이 협력하여 완성된 웹서비스를 만들어드립니다.
        </p>
        <Link to="/workflow">
          <Button variant="primary" size="lg">
            새 프로젝트 시작하기
          </Button>
        </Link>
      </Card>
    </div>
  );
};

export default HomePage;
