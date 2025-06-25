import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  title,
  className = '',
  padding = 'md',
  hover = false,
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  const baseClasses = 'bg-white rounded-xl shadow-sm border border-gray-200';
  const hoverClasses = hover ? 'hover:shadow-md hover:border-gray-300 transition-all duration-200' : '';
  
  const classes = [
    baseClasses,
    hoverClasses,
    paddingClasses[padding],
    className,
  ].join(' ');
  
  return (
    <div className={classes}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b border-gray-100 pb-2">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;
