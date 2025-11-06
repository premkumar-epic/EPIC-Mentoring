import React, { useState, useMemo } from "react";
import { User, Role } from "./types";
import { USERS } from "./constants";
import LoginScreen from "./components/pages/LoginScreen";
import StudentDashboard from "./components/pages/StudentDashboard";
import MentorDashboard from "./components/pages/MentorDashboard";
import AdminDashboard from "./components/pages/AdminDashboard";

const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const handleLogin = (role: Role) => {
    const user = Object.values(USERS).find((u) => u.role === role);
    if (user) {
      setCurrentUser(user);
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  const DashboardComponent = useMemo(() => {
    if (!currentUser) return null;

    switch (currentUser.role) {
      case Role.STUDENT:
        return <StudentDashboard user={currentUser} onLogout={handleLogout} />;
      case Role.MENTOR:
        return <MentorDashboard user={currentUser} onLogout={handleLogout} />;
      case Role.ADMIN:
        return <AdminDashboard user={currentUser} onLogout={handleLogout} />;
      default:
        return null;
    }
  }, [currentUser]);

  if (!currentUser) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen text-gray-900 dark:text-gray-100">
      {DashboardComponent}
    </div>
  );
};

export default App;
