import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeftIcon, 
  PlayIcon, 
  StopIcon, 
  DocumentTextIcon, 
  FolderIcon,
  CodeBracketIcon,
  CogIcon,
  ArrowTopRightOnSquareIcon,  // ExternalLinkIcon 대체
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Card from '../components/Card';
import Button from '../components/Button';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import { projectsApi } from '../services/api';
import { ProjectInfo, FileContent } from '../types';

const ProjectDetailPage: React.FC = () => {
  const { projectName } = useParams<{ projectName: string }>();
  const navigate = useNavigate();
  const [projectInfo, setProjectInfo] = useState<ProjectInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<FileContent | null>(null);
  const [fileLoading, setFileLoading] = useState(false);

  useEffect(() => {
    if (!projectName) {
      navigate('/projects');
      return;
    }

    loadProjectInfo();
  }, [projectName, navigate]);

  const loadProjectInfo = async () => {
    if (!projectName) return;

    try {
      setIsLoading(true);
      setError(null);
      const info = await projectsApi.getProjectInfo(projectName);
      setProjectInfo(info);
    } catch (error) {
      console.error('프로젝트 정보 로딩 실패:', error);
      setError(error instanceof Error ? error.message : '프로젝트 정보를 불러올 수 없습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartProject = async () => {
    if (!projectName) return;

    try {
      setIsStarting(true);
      const result = await projectsApi.startProject(projectName);
      setIsRunning(true);
      alert(`프로젝트가 시작되었습니다!\n\n${result.message}`);
    } catch (error) {
      console.error('프로젝트 시작 실패:', error);
      alert(`프로젝트 시작 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsStarting(false);
    }
  };

  const handleStopProject = async () => {
    if (!projectName) return;

    try {
      setIsStopping(true);
      const result = await projectsApi.stopProject(projectName);
      setIsRunning(false);
      alert(`프로젝트가 중지되었습니다!\n\n${result.message}`);
    } catch (error) {
      console.error('프로젝트 중지 실패:', error);
      alert(`프로젝트 중지 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setIsStopping(false);
    }
  };

  const loadFileContent = async (filePath: string) => {
    if (!projectName) return;

    try {
      setFileLoading(true);
      setSelectedFile(filePath);
      const content = await projectsApi.getProjectFile(projectName, filePath);
      setFileContent(content);
    } catch (error) {
      console.error('파일 로딩 실패:', error);
      alert(`파일을 불러올 수 없습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
      setSelectedFile(null);
    } finally {
      setFileLoading(false);
    }
  };

  const closeFileViewer = () => {
    setSelectedFile(null);
    setFileContent(null);
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileIcon = (fileName: string) => {
    if (fileName.endsWith('.md')) return <DocumentTextIcon className="w-4 h-4" />;
    if (fileName.includes('docker') || fileName.endsWith('.yml') || fileName.endsWith('.yaml')) return <CogIcon className="w-4 h-4" />;
    if (fileName.endsWith('.sh') || fileName.endsWith('.json') || fileName.endsWith('.js') || fileName.endsWith('.ts') || fileName.endsWith('.tsx')) return <CodeBracketIcon className="w-4 h-4" />;
    return <DocumentTextIcon className="w-4 h-4" />;
  };

  const getLanguageFromFilePath = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'js': case 'jsx': return 'javascript';
      case 'ts': case 'tsx': return 'typescript';
      case 'py': return 'python';
      case 'json': return 'json';
      case 'yml': case 'yaml': return 'yaml';
      case 'md': return 'markdown';
      case 'sh': return 'bash';
      case 'css': return 'css';
      case 'html': return 'html';
      default: return 'text';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Loading message="프로젝트 정보를 불러오는 중..." />
      </div>
    );
  }

  if (error || !projectInfo) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/projects')} variant="outline" className="flex items-center gap-2">
            <ArrowLeftIcon className="w-4 h-4" />
            프로젝트 목록
          </Button>
        </div>
        <Alert type="error">
          <ExclamationTriangleIcon className="w-5 h-5" />
          <div>
            <h3 className="font-medium">프로젝트를 찾을 수 없습니다</h3>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/projects')} variant="outline" className="flex items-center gap-2">
            <ArrowLeftIcon className="w-4 h-4" />
            프로젝트 목록
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{projectInfo.project_name}</h1>
            <p className="text-gray-600 mt-1">
              생성일: {formatDate(projectInfo.created_at)}
            </p>
          </div>
        </div>
        
        <div className="flex gap-3">
          <Button
            onClick={loadProjectInfo}
            variant="outline"
            className="flex items-center gap-2"
          >
            <ClockIcon className="w-4 h-4" />
            새로고침
          </Button>
          
          {!isRunning ? (
            <Button
              onClick={handleStartProject}
              disabled={isStarting}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
            >
              <PlayIcon className="w-4 h-4" />
              {isStarting ? '시작 중...' : '프로젝트 시작'}
            </Button>
          ) : (
            <Button
              onClick={handleStopProject}
              disabled={isStopping}
              variant="outline"
              className="flex items-center gap-2 border-red-300 text-red-600 hover:bg-red-50"
            >
              <StopIcon className="w-4 h-4" />
              {isStopping ? '중지 중...' : '프로젝트 중지'}
            </Button>
          )}
        </div>
      </div>

      {/* 실행 상태 표시 */}
      {isRunning && (
        <Alert type="success">
          <CheckCircleIcon className="w-5 h-5" />
          <div>
            <h3 className="font-medium">프로젝트가 실행 중입니다</h3>
            <p className="text-sm mt-1">
              개발 서버가 백그라운드에서 실행되고 있습니다. 
              웹 브라우저에서 확인해보세요.
            </p>
            <div className="mt-2 flex gap-2">
              <a
                href="http://localhost:3000"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
              >
                <ArrowTopRightOnSquareIcon className="w-3 h-3" />
                Frontend (포트 3000)
              </a>
              <a
                href="http://localhost:8000"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
              >
                <ArrowTopRightOnSquareIcon className="w-3 h-3" />
                Backend (포트 8000)
              </a>
            </div>
          </div>
        </Alert>
      )}

      {/* 프로젝트 상태 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 환경 파일 상태 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CogIcon className="w-5 h-5 text-blue-600" />
            환경 설정
          </h3>
          <div className="space-y-3">
            {Object.entries(projectInfo.env_files).map(([key, exists]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {key.replace(/_/g, ' ').toUpperCase()}
                </span>
                {exists ? (
                  <CheckCircleIcon className="w-4 h-4 text-green-500" />
                ) : (
                  <ExclamationTriangleIcon className="w-4 h-4 text-gray-300" />
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Docker 파일 상태 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CogIcon className="w-5 h-5 text-purple-600" />
            Docker 설정
          </h3>
          <div className="space-y-3">
            {Object.entries(projectInfo.docker_files).map(([key, exists]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {key.replace(/_/g, ' ').toUpperCase()}
                </span>
                {exists ? (
                  <CheckCircleIcon className="w-4 h-4 text-green-500" />
                ) : (
                  <ExclamationTriangleIcon className="w-4 h-4 text-gray-300" />
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* 실행 스크립트 상태 */}
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CodeBracketIcon className="w-5 h-5 text-green-600" />
            실행 스크립트
          </h3>
          <div className="space-y-3">
            {Object.entries(projectInfo.scripts).map(([key, exists]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  {key.replace(/_/g, ' ').toUpperCase()}
                </span>
                {exists ? (
                  <CheckCircleIcon className="w-4 h-4 text-green-500" />
                ) : (
                  <ExclamationTriangleIcon className="w-4 h-4 text-gray-300" />
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 패키지 정보 */}
      {projectInfo.package_info && (
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <InformationCircleIcon className="w-5 h-5 text-indigo-600" />
            패키지 정보
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="space-y-2">
                <div>
                  <span className="text-sm font-medium text-gray-700">이름:</span>
                  <span className="ml-2 text-sm text-gray-900">{projectInfo.package_info.name}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">버전:</span>
                  <span className="ml-2 text-sm text-gray-900">{projectInfo.package_info.version}</span>
                </div>
                {projectInfo.package_info.description && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">설명:</span>
                    <span className="ml-2 text-sm text-gray-900">{projectInfo.package_info.description}</span>
                  </div>
                )}
              </div>
            </div>
            
            {projectInfo.package_info.scripts && Object.keys(projectInfo.package_info.scripts).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">사용 가능한 스크립트:</h4>
                <div className="space-y-1">
                  {Object.entries(projectInfo.package_info.scripts).map(([script, command]) => (
                    <div key={script} className="text-xs bg-gray-50 p-2 rounded">
                      <span className="font-mono text-blue-600">{script}:</span>
                      <span className="ml-2 text-gray-700">{command}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* README 내용 */}
      {projectInfo.readme_content && (
        <Card>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <DocumentTextIcon className="w-5 h-5 text-orange-600" />
            README
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">
              {projectInfo.readme_content}
            </pre>
          </div>
        </Card>
      )}

      {/* 빠른 파일 액세스 */}
      <Card>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FolderIcon className="w-5 h-5 text-gray-600" />
          주요 파일
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { name: 'README.md', path: 'README.md' },
            { name: 'package.json', path: 'frontend/package.json' },
            { name: 'main.py', path: 'backend/main.py' },
            { name: 'docker-compose.yml', path: 'docker-compose.yml' },
            { name: 'run.sh', path: 'run.sh' },
            { name: '.env.example', path: '.env.example' }
          ].map((file) => (
            <button
              key={file.path}
              onClick={() => loadFileContent(file.path)}
              className="flex items-center gap-2 p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-left"
              disabled={fileLoading && selectedFile === file.path}
            >
              {getFileIcon(file.name)}
              <span className="text-sm text-gray-700 truncate">{file.name}</span>
              {fileLoading && selectedFile === file.path && (
                <div className="w-3 h-3 border border-gray-300 border-t-blue-500 rounded-full animate-spin" />
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* 파일 내용 미리보기 */}
      {selectedFile && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              {getFileIcon(selectedFile)}
              파일 내용: {selectedFile}
            </h3>
            <Button
              onClick={closeFileViewer}
              variant="outline"
              className="flex items-center gap-2"
            >
              <XMarkIcon className="w-4 h-4" />
              닫기
            </Button>
          </div>
          
          {fileLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loading message="파일을 불러오는 중..." />
            </div>
          ) : fileContent ? (
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="text-sm leading-relaxed">
                <code className={`language-${getLanguageFromFilePath(selectedFile)}`}>
                  {fileContent.content}
                </code>
              </pre>
            </div>
          ) : (
            <Alert type="warning">
              <ExclamationTriangleIcon className="w-5 h-5" />
              <div>
                <h3 className="font-medium">파일을 불러올 수 없습니다</h3>
                <p className="text-sm mt-1">파일이 존재하지 않거나 읽기 권한이 없습니다.</p>
              </div>
            </Alert>
          )}
        </Card>
      )}

      {/* 프로젝트 경로 정보 */}
      <Card className="bg-gray-50">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FolderIcon className="w-5 h-5 text-gray-600" />
          프로젝트 경로
        </h3>
        <div className="bg-white p-3 rounded border">
          <code className="text-sm text-gray-800 break-all">
            {projectInfo.project_path}
          </code>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          터미널에서 이 경로로 이동하여 직접 프로젝트를 관리할 수 있습니다.
        </p>
      </Card>
    </div>
  );
};

export default ProjectDetailPage;