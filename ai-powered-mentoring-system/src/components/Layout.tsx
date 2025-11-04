import React, { useState, ReactNode } from "react";
import { User, NavLink as NavLinkType } from "../types";
import { MenuIcon, XIcon, LogOutIcon } from "./Icons";

interface LayoutProps {
  user: User;
  navLinks: NavLinkType[];
  activeComponent: React.ComponentType;
  onNavClick: (component: React.ComponentType) => void;
  onLogout: () => void;
  children: ReactNode;
}

const Sidebar: React.FC<{
  navLinks: NavLinkType[];
  activeComponent: React.ComponentType;
  onNavClick: (component: React.ComponentType) => void;
  onLogout: () => void;
  user: User;
  className?: string;
  onLinkClick?: () => void;
}> = ({
  navLinks,
  activeComponent,
  onNavClick,
  onLogout,
  user,
  className,
  onLinkClick,
}) => {
  return (
    <aside
      className={`flex flex-col bg-white dark:bg-gray-800 shadow-lg ${className}`}
    >
      <div className="flex items-center justify-center h-20 border-b dark:border-gray-700">
        <h1 className="text-2xl font-bold text-primary-600">Mentoring AI</h1>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navLinks.map((link) => (
          <a
            key={link.name}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              onNavClick(link.component);
              if (onLinkClick) onLinkClick();
            }}
            className={`flex items-center px-4 py-2 text-gray-700 dark:text-gray-300 rounded-lg transition-colors duration-200 ${
              activeComponent === link.component
                ? "bg-primary-100 dark:bg-primary-900/50 text-primary-600 dark:text-primary-400"
                : "hover:bg-gray-100 dark:hover:bg-gray-700"
            }`}
          >
            <link.icon className="w-5 h-5" />
            <span className="ml-3">{link.name}</span>
          </a>
        ))}
      </nav>
      <div className="p-4 border-t dark:border-gray-700">
        <div className="flex items-center">
          <img
            src={user.avatar}
            alt={user.name}
            className="w-10 h-10 rounded-full"
          />
          <div className="ml-3">
            <p className="font-semibold text-sm">{user.name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {user.role}
            </p>
          </div>
          <button
            onClick={onLogout}
            className="ml-auto text-gray-500 hover:text-primary-600 dark:hover:text-primary-400"
          >
            <LogOutIcon className="w-6 h-6" />
          </button>
        </div>
      </div>
    </aside>
  );
};

const Layout: React.FC<LayoutProps> = ({
  user,
  navLinks,
  activeComponent,
  onNavClick,
  onLogout,
  children,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Desktop Sidebar */}
      <Sidebar
        navLinks={navLinks}
        activeComponent={activeComponent}
        onNavClick={onNavClick}
        onLogout={onLogout}
        user={user}
        className="hidden lg:flex w-64"
      />

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 flex lg:hidden">
          <div
            className="fixed inset-0 bg-black opacity-50"
            onClick={() => setSidebarOpen(false)}
          ></div>
          <Sidebar
            navLinks={navLinks}
            activeComponent={activeComponent}
            onNavClick={onNavClick}
            onLogout={onLogout}
            user={user}
            className="relative z-40 w-64"
            onLinkClick={() => setSidebarOpen(false)}
          />
        </div>
      )}

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 shadow-md lg:hidden">
          <h1 className="text-xl font-bold text-primary-600">Mentoring AI</h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-500 focus:outline-none"
          >
            {sidebarOpen ? (
              <XIcon className="w-6 h-6" />
            ) : (
              <MenuIcon className="w-6 h-6" />
            )}
          </button>
        </header>

        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 dark:bg-gray-900">
          <div className="container mx-auto px-6 py-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
