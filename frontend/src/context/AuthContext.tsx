import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

interface User {
  id: string;
  username: string;
  role: 'ADMIN' | 'INVESTIGATOR' | 'ANALYST' | 'AUDITOR' | 'VIEWER';
  email: string;
}

interface AuthContextType {
  user: User;
  token: string | null;
  login: (username: string, role?: string) => void;
  logout: () => void;
  switchRole: (role: 'ADMIN' | 'INVESTIGATOR' | 'ANALYST' | 'AUDITOR' | 'VIEWER') => void;
}

const defaultUser: User = {
  id: 'usr_lead_001',
  username: 'lead_investigator',
  role: 'INVESTIGATOR',
  email: 'investigator@tcf-fx.internal',
};

const AuthContext = createContext<AuthContextType>({
  user: defaultUser,
  token: null,
  login: () => {},
  logout: () => {},
  switchRole: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User>(() => {
    const saved = localStorage.getItem('tcf_user');
    return saved ? JSON.parse(saved) : defaultUser;
  });
  const [token, setToken] = useState<string | null>(localStorage.getItem('tcf_token'));

  const login = (username: string, role: string = 'INVESTIGATOR') => {
    const u: User = {
      id: `usr_${username}`,
      username,
      role: role as any,
      email: `${username}@tcf-fx.internal`,
    };
    setUser(u);
    localStorage.setItem('tcf_user', JSON.stringify(u));
  };

  const switchRole = (role: 'ADMIN' | 'INVESTIGATOR' | 'ANALYST' | 'AUDITOR' | 'VIEWER') => {
    const updated = { ...user, role };
    setUser(updated);
    localStorage.setItem('tcf_user', JSON.stringify(updated));
  };

  const logout = () => {
    setUser(defaultUser);
    setToken(null);
    localStorage.removeItem('tcf_token');
    localStorage.removeItem('tcf_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
