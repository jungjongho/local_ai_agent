import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullscreen?: boolean;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  text = '로딩 중...',
  fullscreen = false,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  const containerClasses = fullscreen 
    ? 'fixed inset-0 bg-white bg-opacity-80 flex flex-col items-center justify-center z-50'
    : 'flex flex-col items-center justify-center p-8';
  
  return (
    <div className={containerClasses}>
      <div className="relative">
        {/* 메인 스피너 */}
        <svg
          className={`animate-spin ${sizeClasses[size]} text-blue-600`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        
        {/* 외부 링 */}
        <div className={`absolute inset-0 border-4 border-blue-100 rounded-full animate-pulse`}></div>
      </div>
      
      {text && (
        <div className="mt-4 text-center">
          <p className={`${textSizeClasses[size]} text-gray-600 font-medium`}>
            {text}
          </p>
          <div className="mt-2 flex items-center justify-center space-x-1">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Loading;
