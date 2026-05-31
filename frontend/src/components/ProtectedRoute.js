import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext";
import LoadingState from "./StateBlocks";

export default function ProtectedRoute({ children, roles = [] }) {
  const { isAuthenticated, isAuthLoading, hasAnyRole } = useAuth();
  const location = useLocation();

  // ProtectedRoute blokuje widoki pacjenta/staff bez tokenu JWT i wymaganej roli.
  if (isAuthLoading) return <LoadingState message="Sprawdzanie sesji..." />;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />;
  if (!hasAnyRole(roles)) {
    return (
      <section className="panel narrow">
        <h1>Brak dostępu</h1>
        <p>To miejsce jest dostępne tylko dla użytkowników z odpowiednią rolą.</p>
      </section>
    );
  }
  return children;
}
