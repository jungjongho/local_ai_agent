import React from 'react';
import { WorkflowProgress } from '../types';

interface ProgressBarProps {
  progress: number;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress, className = '' }) => {
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div
        className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-in-out progress-bar"
        style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
      />
    </div>
  );
};

interface WorkflowProgressDisplayProps {
  progress?: WorkflowProgress;
  overallProgress: number;
  currentStage: string;
  className?: string;
}

const WorkflowProgressDisplay: React.FC<WorkflowProgressDisplayProps> = ({
  progress,
  overallProgress,
  currentStage,
  className = '',
}) => {
  const stages = [
    { key: 'planning', name: 'PM Agent', description: '프로젝트 계획 수립' },
    { key: 'uiux_design', name: 'UI/UX Agent', description: '디자인 시스템 설계' },
    { key: 'frontend_dev', name: 'Frontend Agent', description: 'React 코드 생성' },
    { key: 'backend_dev', name: 'Backend Agent', description: 'FastAPI 코드 생성' },
    { key: 'devops_setup', name: 'DevOps Agent', description: 'Docker 및 배포 설정' },
    { key: 'file_generation', name: 'File Generation', description: '프로젝트 파일 생성' },
    { key: 'project_deployment', name: 'Deployment', description: '프로젝트 배포 준비' },
  ];

  const getStageStatus = (stageKey: string) => {
    if (!currentStage) return 'pending';
    
    const currentIndex = stages.findIndex(s => s.key === currentStage);
    const stageIndex = stages.findIndex(s => s.key === stageKey);
    
    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        );
      case 'active':
        return (
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
          </div>
        );
      default:
        return (
          <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-gray-500 rounded-full" />
          </div>
        );
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      {/* 전체 진행률 */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-900">워크플로 진행상황</h3>
          <span className="text-sm font-medium text-gray-600">{overallProgress}%</span>
        </div>
        <ProgressBar progress={overallProgress} />
        {progress && (
          <p className="mt-2 text-sm text-gray-600">{progress.message}</p>
        )}
      </div>

      {/* 단계별 진행상황 */}
      <div className="space-y-4">
        {stages.map((stage, index) => {
          const status = getStageStatus(stage.key);
          const isActive = status === 'active';
          
          return (
            <div key={stage.key} className="flex items-center space-x-4">
              {/* 아이콘 */}
              <div className="flex-shrink-0">
                {getStageIcon(status)}
              </div>
              
              {/* 연결선 */}
              {index < stages.length - 1 && (
                <div className="absolute left-9 mt-6 w-px h-6 bg-gray-300" />
              )}
              
              {/* 내용 */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h4 className={`text-sm font-medium ${
                    isActive ? 'text-blue-900' : status === 'completed' ? 'text-green-800' : 'text-gray-500'
                  }`}>
                    {stage.name}
                  </h4>
                  {isActive && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      진행 중
                    </span>
                  )}
                  {status === 'completed' && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      완료
                    </span>
                  )}
                </div>
                <p className={`text-sm ${
                  isActive ? 'text-blue-700' : status === 'completed' ? 'text-green-600' : 'text-gray-400'
                }`}>
                  {stage.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* 현재 진행 중인 작업 세부사항 */}
      {progress && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-blue-900">현재 작업</span>
          </div>
          <p className="mt-1 text-sm text-blue-800">{progress.message}</p>
          <p className="mt-1 text-xs text-blue-600">
            {new Date(progress.timestamp).toLocaleTimeString()}
          </p>
        </div>
      )}
    </div>
  );
};

export default WorkflowProgressDisplay;
export { ProgressBar };
