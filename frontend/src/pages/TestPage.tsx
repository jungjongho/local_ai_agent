import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          🚀 Frontend 테스트
        </h1>
        <p className="text-gray-600 mb-6">
          Frontend가 정상적으로 동작하고 있습니다!
        </p>
        <div className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800 font-medium">✅ React 로드됨</p>
          </div>
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-blue-800 font-medium">✅ TypeScript 동작 중</p>
          </div>
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-md">
            <p className="text-purple-800 font-medium">✅ TailwindCSS 적용됨</p>
          </div>
        </div>
        <div className="mt-6">
          <button 
            onClick={() => alert('Frontend가 정상 동작합니다!')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            테스트 버튼
          </button>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          현재 시간: {new Date().toLocaleString()}
        </div>
      </div>
    </div>
  );
};

export default TestPage;