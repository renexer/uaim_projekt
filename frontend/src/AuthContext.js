import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, authStorage } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => authStorage.getUser());
  const [isAuthLoading, setIsAuthLoading] = useState(Boolean(authStorage.getToken()));

  useEffect(() => {
    let ignore = false;

    async function hydrateUser() {
      if (!authStorage.getToken()) {
        setIsAuthLoading(false);
        return;
      }
      try {
        const currentUser = await api.me();
        if (!ignore) {
          authStorage.saveSession({ accessToken: authStorage.getToken(), refreshToken: authStorage.getRefreshToken(), user: currentUser });
          setUser(currentUser);
        }
      } catch {
        authStorage.clear();
        if (!ignore) setUser(null);
      } finally {
        if (!ignore) setIsAuthLoading(false);
      }
    }

    hydrateUser();
    return () => {
      ignore = true;
    };
  }, []);

  async function login(email, password) {
    const session = await api.login(email, password);
    // Po poprawnym logowaniu zapisujemy token JWT oraz podstawowe dane użytkownika.
    authStorage.saveSession(session);
    setUser(session.user);
    return session.user;
  }

  async function register(payload) {
    return api.register(payload);
  }

  function logout() {
    authStorage.clear();
    setUser(null);
  }

  const hasAnyRole = useCallback((roles = []) => {
    if (!roles.length) return true;
    return roles.some((role) => user?.roles?.includes(role));
  }, [user]);

  const value = useMemo(() => ({ user, isAuthenticated: Boolean(user && authStorage.getToken()), isAuthLoading, login, register, logout, hasAnyRole }), [user, isAuthLoading, hasAnyRole]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth musi być użyty wewnątrz AuthProvider");
  }
  return value;
}
