"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

type AuthState = {
  token: string;
  setToken: (t: string) => void;
  clearToken: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("hireus_token");
    if (stored) setTokenState(stored);
  }, []);

  const setToken = (t: string) => {
    setTokenState(t);
    localStorage.setItem("hireus_token", t);
  };

  const clearToken = () => {
    setTokenState("");
    localStorage.removeItem("hireus_token");
  };

  const value = useMemo(() => ({ token, setToken, clearToken }), [token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
