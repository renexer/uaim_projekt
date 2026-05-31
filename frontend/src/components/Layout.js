import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Layout() {
  const { user, isAuthenticated, logout, hasAnyRole } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">Spokojna Przystań</Link>
        <nav className="nav-links" aria-label="Główna nawigacja">
          <NavLink to="/services">Usługi</NavLink>
          <NavLink to="/therapists">Terapeuci</NavLink>
          <NavLink to="/booking">Rezerwacja</NavLink>
          {isAuthenticated && <NavLink to="/appointments">Moje wizyty</NavLink>}
          {isAuthenticated && <NavLink to="/consultations">Historia</NavLink>}
          {isAuthenticated && hasAnyRole(["ADMIN", "THERAPIST"]) && <NavLink to="/staff">Panel terapeuty</NavLink>}
        </nav>
        <div className="auth-actions">
          {isAuthenticated ? (
            <>
              <span className="user-chip">{user?.firstName} {user?.lastName}</span>
              <button className="btn btn-light" onClick={handleLogout}>Wyloguj</button>
            </>
          ) : (
            <>
              <Link className="btn btn-light" to="/login">Logowanie</Link>
              <Link className="btn btn-primary" to="/register">Rejestracja</Link>
            </>
          )}
        </div>
      </header>
      <main className="main-content">
        <Outlet />
      </main>
      <footer className="footer">Projekt UAIM — gabinet psychologiczno-terapeutyczny</footer>
    </div>
  );
}
