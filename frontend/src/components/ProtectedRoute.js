import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext";
import LoadingState from "./StateBlocks";

export default function ProtectedRoute({ roles = [] }) {
  const { isAuthenticated, isAuthLoading, hasAnyRole } = useAuth();
  const location = useLocation();

  if (isAuthLoading) {
    return <LoadingState message="Sprawdzanie sesji..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!hasAnyRole(roles)) {
    return (
      <section className="panel narrow">
        <h1>Brak dostępu</h1>
        <p>To miejsce jest dostępne tylko dla użytkowników z odpowiednią rolą.</p>
      </section>
    );
  }

  return <Outlet />;
}