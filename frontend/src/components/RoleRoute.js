import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext";
import LoadingState from "./StateBlocks";

export default function RoleRoute({ roles = [] }) {
  const location = useLocation();
  const { isAuthenticated, isAuthLoading, hasAnyRole } = useAuth();

  if (isAuthLoading) {
    return <LoadingState message="Sprawdzanie uprawnień..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!hasAnyRole(roles)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}