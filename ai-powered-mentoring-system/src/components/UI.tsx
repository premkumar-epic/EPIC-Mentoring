import React, { ReactNode } from 'react';
import { XIcon } from './Icons';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', size = 'md', className = '', ...props }) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
  
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  const variantClasses = {
    primary: "bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 focus:ring-gray-500",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
  };

  return (
    <button className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => {
  const interactiveClasses = onClick ? 'cursor-pointer hover:shadow-lg hover:-translate-y-1 transition-transform duration-200' : '';
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden ${className} ${interactiveClasses}`} onClick={onClick}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardProps> = ({ children, className = '' }) => {
    return (
        <div className={`p-4 border-b border-gray-200 dark:border-gray-700 ${className}`}>
            {children}
        </div>
    );
}

export const CardContent: React.FC<CardProps> = ({ children, className = '' }) => {
    return (
        <div className={`p-4 ${className}`}>
            {children}
        </div>
    );
}

export const CardTitle: React.FC<CardProps> = ({ children, className = '' }) => {
    return (
        <h3 className={`text-lg font-semibold text-gray-900 dark:text-white ${className}`}>
            {children}
        </h3>
    );
}

export const Spinner: React.FC = () => {
  return (
    <div className="flex justify-center items-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea: React.FC<TextareaProps> = ({ className = '', ...props }) => {
    return (
        <textarea
            className={`w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 ${className}`}
            {...props}
        />
    );
};

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    children: ReactNode;
}
export const Select: React.FC<SelectProps> = ({ children, className = '', ...props }) => {
    return (
        <select
            className={`w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 ${className}`}
            {...props}
        >
            {children}
        </select>
    );
};


interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md m-4">
                <div className="flex justify-between items-center p-4 border-b dark:border-gray-700">
                    <h3 className="text-xl font-semibold">{title}</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-800 dark:hover:text-gray-200">
                        <XIcon className="w-6 h-6" />
                    </button>
                </div>
                <div className="p-4">
                    {children}
                </div>
            </div>
        </div>
    );
};

interface AlertProps {
    message: string;
    type: 'success' | 'error' | 'info';
}

export const Alert: React.FC<AlertProps> = ({ message, type }) => {
    const typeClasses = {
        success: 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300',
        error: 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300',
        info: 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300',
    };

    return (
        <div className={`p-4 rounded-lg text-sm ${typeClasses[type]}`} role="alert">
            {message}
        </div>
    );
};

export const ChartSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`w-full h-full animate-pulse ${className}`}>
      <div className="w-full h-full bg-gray-200 dark:bg-gray-700 rounded-lg" />
    </div>
  );
};