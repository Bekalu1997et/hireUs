"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, authApi, Token } from "@/lib/api";

interface User {
  id: string;
  email: string;
  full_name?: string;
  organization_id?: string;
}

interface AuthContextType {
  user: User | null;
  organizationId: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  confirm_password: string;
  full_name?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const token = api.getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const userData = await authApi.getMe() as User;
      setUser(userData);
    } catch (error) {
      // Token is invalid or expired
      api.setAccessToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    api.setAccessToken(response.access_token);
    
    const userData = await authApi.getMe() as User;
    setUser(userData);
  };

  const register = async (data: RegisterData) => {
    const response = await authApi.register(data);
    api.setAccessToken(response.access_token);
    
    const userData = await authApi.getMe() as User;
    setUser(userData);
  };

  const logout = () => {
    api.setAccessToken(null);
    setUser(null);
  };

  const value = {
    user,
    organizationId: user?.organization_id || null,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

