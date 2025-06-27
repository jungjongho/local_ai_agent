import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import Alert from '../components/Alert';
import WorkflowProgressDisplay from '../components/WorkflowProgress';
import ModelSelector from '../components/ModelSelector';
import { workflowApi } from '../services/api';
import { WorkflowCreate, WorkflowProgress, WorkflowStatusDetails, WorkflowStatus } from '../types';

const WorkflowPage: React.FC = () => {
  const navigate = useNavigate();
  const [userInput, setUserInput] = useState('');
  const [projectName, setProjectName] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isCreating, setIsCreating] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowStatusDetails | null>(null);
  const [progress, setProgress] = useState<WorkflowProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  // 컴포넌트 언마운트 시 EventSource 정리
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userInput.trim()) {
      setError('프로젝트 아이디어를 입력해주세요.');
      return;
    }

    if (userInput.trim().length < 10) {
      setError('더 구체적인 설명을 입력해주세요. (최소 10글자)');
      return;
    }

    try {
      setIsCreating(true);
      setError(null);
      setProgress(null);

      const workflowData: WorkflowCreate = {
        user_input: userInput.trim(),
        project_name: projectName.trim() || undefined,
        model: selectedModel || undefined
      };

      console.log('Creating workflow with data:', workflowData);
      const response = await workflowApi.createWorkflow(workflowData);
      console.log('Workflow created:', response);

      // 워크플로 생성 성공
      setCurrentWorkflow({
        id: response.id,
        status: response.status,
        current_stage: 'planning',
        progress_percentage: 0,
        created_at: response.created_at,
        project_name: projectName || '새 프로젝트'
      });

      // 진행상황 스트림 시작
      startProgressStream(response.id);
      
    } catch (err: any) {
      console.error('Workflow creation error:', err);
      setError(err.message || '워크플로 생성에 실패했습니다.');
    } finally {
      setIsCreating(false);
    }
  };

  const startProgressStream = (workflowId: string) => {
    // 기존 EventSource 정리
    if (eventSource) {
      eventSource.close();
    }

    try {
      const newEventSource = workflowApi.streamProgress(workflowId);
      setEventSource(newEventSource);

      newEventSource.onmessage = (event) => {
        try {
          const progressData: WorkflowProgress = JSON.parse(event.data);
          console.log('Progress update:', progressData);
          setProgress(progressData);
          
          // 워크플로 상태 업데이트
          setCurrentWorkflow(prev => prev ? {
            ...prev,
            current_stage: progressData.stage,
            progress_percentage: progressData.progress_percentage
          } : null);
          
          // 완료 또는 실패 시 스트림 종료
          if (progressData.stage === 'completed' || progressData.stage === 'failed') {
            newEventSource.close();
            if (progressData.stage === 'completed') {
              setTimeout(() => {
                navigate('/projects');
              }, 3000); // 3초 후 프로젝트 페이지로 이동
            }
          }
        } catch (parseError) {
          console.error('Progress parsing error:', parseError);
        }
      };

      newEventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        setError('실시간 진행상황 업데이트에 실패했습니다.');
        newEventSource.close();
      };

    } catch (err) {
      console.error('EventSource creation error:', err);
      setError('진행상황 모니터링을 시작할 수 없습니다.');
    }
  };

  const handleCancel = async () => {
    if (!currentWorkflow) return;

    try {
      await workflowApi.cancelWorkflow(currentWorkflow.id);
      
      // EventSource 정리
      if (eventSource) {
        eventSource.close();
        setEventSource(null);
      }
      
      // 상태 초기화
      setCurrentWorkflow(null);
      setProgress(null);
      setUserInput('');
      setProjectName('');
      
    } catch (err: any) {
      setError(err.message || '워크플로 취소에 실패했습니다.');
    }
  };

  const handleReset = () => {
    // EventSource 정리
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
    }
    
    // 상태 초기화
    setCurrentWorkflow(null);
    setProgress(null);
    setUserInput('');
    setProjectName('');
    setSelectedModel('');
      setError(null);
  };

  const exampleIdeas = [
    "할일 관리 앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해.",
    "간단한 블로그 시스템을 만들어줘. 글 작성, 수정, 삭제, 목록 보기 기능이 있어야 해.",
    "온라인 북마크 관리 시스템을 만들어줘. URL 저장, 카테고리 분류, 검색 기능이 필요해.",
    "재고 관리 시스템을 만들어줘. 상품 등록, 수량 관리, 입출고 기록 기능이 있어야 해.",
    "간단한 투표 시스템을 만들어줘. 투표 생성, 참여, 결과 확인 기능이 필요해."
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 페이지 헤더 */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          새로운 웹서비스 생성
        </h1>
        <p className="text-lg text-gray-600">
          아이디어를 설명하면 AI 에이전트들이 협력하여 완성된 웹서비스를 만들어드립니다.
        </p>
      </div>

      {/* 에러 표시 */}
      {error && (
        <Alert 
          type="error" 
          title="오류 발생"
          message={error} 
          onClose={() => setError(null)}
        />
      )}

      {/* 워크플로가 진행 중이 아닐 때 */}
      {!currentWorkflow && (
        <>
          {/* 입력 폼 */}
          <Card title="프로젝트 아이디어 입력">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="userInput" className="block text-sm font-medium text-gray-700 mb-2">
                  프로젝트 아이디어 *
                </label>
                <textarea
                  id="userInput"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="예: 할일 관리 앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-700 text-sm bg-white placeholder-gray-400"
                  rows={4}
                  required
                  disabled={isCreating}
                />
                <p className="mt-1 text-sm text-gray-500">
                  구체적이고 명확한 설명을 입력하면 더 정확한 결과를 얻을 수 있습니다.
                </p>
              </div>

              <div>
                <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 mb-2">
                  프로젝트 이름 (선택사항)
                </label>
                <input
                  id="projectName"
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="예: todo-app (비워두면 자동 생성됩니다)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700 text-sm bg-white placeholder-gray-400"
                  disabled={isCreating}
                />
                <p className="mt-1 text-sm text-gray-500">
                  영문 소문자, 숫자, 하이픈(-)만 사용 가능합니다.
                </p>
              </div>

              <ModelSelector
                selectedModel={selectedModel}
                onModelChange={setSelectedModel}
                className="mb-6"
              />

              <div className="flex justify-end space-x-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setUserInput('');
                    setProjectName('');
                    setSelectedModel('');
                  }}
                  disabled={isCreating}
                >
                  초기화
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  loading={isCreating}
                  disabled={isCreating || !userInput.trim()}
                >
                  {isCreating ? '생성 중...' : '웹서비스 생성 시작'}
                </Button>
              </div>
            </form>
          </Card>

          {/* 예시 아이디어 */}
          <Card title="예시 아이디어">
            <div className="space-y-3">
              <p className="text-sm text-gray-600 mb-4">
                아래 예시를 참고하여 프로젝트 아이디어를 입력해보세요:
              </p>
              {exampleIdeas.map((idea, index) => (
                <div key={index} className="group">
                  <button
                    onClick={() => setUserInput(idea)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
                    disabled={isCreating}
                  >
                    <span className="text-sm text-gray-700 group-hover:text-blue-700">
                      {idea}
                    </span>
                  </button>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      {/* 워크플로 진행 중일 때 */}
      {currentWorkflow && (
        <>
          <Card title={`프로젝트: ${currentWorkflow.project_name}`}>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600">워크플로 ID</p>
                  <p className="text-xs font-mono text-gray-800">{currentWorkflow.id}</p>
                </div>
                <div className="flex space-x-2">
                  {currentWorkflow.status === WorkflowStatus.RUNNING && (
                    <Button variant="danger" size="sm" onClick={handleCancel}>
                      취소
                    </Button>
                  )}
                  <Button variant="secondary" size="sm" onClick={handleReset}>
                    새로 시작
                  </Button>
                </div>
              </div>
              
              {/* 입력된 아이디어 표시 */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-2">입력된 아이디어:</p>
                <p className="text-sm text-gray-600">{userInput}</p>
              </div>
            </div>
          </Card>

          {/* 진행상황 표시 */}
          <WorkflowProgressDisplay
            progress={progress}
            overallProgress={currentWorkflow.progress_percentage}
            currentStage={currentWorkflow.current_stage}
          />

          {/* 완료 메시지 */}
          {currentWorkflow.status === WorkflowStatus.COMPLETED && (
            <Alert
              type="success"
              title="프로젝트 생성 완료!"
              message="웹서비스가 성공적으로 생성되었습니다. 3초 후 프로젝트 페이지로 이동합니다."
            />
          )}

          {/* 실패 메시지 */}
          {currentWorkflow.status === WorkflowStatus.FAILED && (
            <Alert
              type="error"
              title="프로젝트 생성 실패"
              message={currentWorkflow.error?.message || '프로젝트 생성 중 오류가 발생했습니다.'}
              onRetry={handleReset}
            />
          )}
        </>
      )}
    </div>
  );
};

export default WorkflowPage;
