
import React from 'react';
import { Role } from '../../types';
import { Button } from '../UI';
import { UsersIcon, BriefcaseIcon, BookOpenIcon } from '../Icons';

interface LoginScreenProps {
  onLogin: (role: Role) => void;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin }) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md p-8 space-y-8 bg-white rounded-2xl shadow-xl dark:bg-gray-800">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary-600">AI Mentoring System</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Select your role to continue</p>
        </div>
        <div className="space-y-4">
          <Button
            className="w-full text-lg py-3"
            onClick={() => onLogin(Role.STUDENT)}
          >
            <BookOpenIcon className="w-6 h-6 mr-3" />
            Login as Student
          </Button>
          <Button
            className="w-full text-lg py-3"
            onClick={() => onLogin(Role.MENTOR)}
          >
            <UsersIcon className="w-6 h-6 mr-3" />
            Login as Mentor
          </Button>
          <Button
            className="w-full text-lg py-3"
            onClick={() => onLogin(Role.ADMIN)}
          >
            <BriefcaseIcon className="w-6 h-6 mr-3" />
            Login as Admin
          </Button>
        </div>
        <p className="text-xs text-center text-gray-500 dark:text-gray-400">
          This is a demonstration. No real authentication is performed.
        </p>
      </div>
    </div>
  );
};

export default LoginScreen;
