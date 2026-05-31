import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const redirectTo = location.state?.from?.pathname || "/appointments";

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (!form.email || !form.password) {
      setError("Podaj e-mail oraz hasło.");
      return;
    }
    setLoading(true);
    try {
      const user = await login(form.email, form.password);
      if (user.roles?.some((role) => ["ADMIN", "THERAPIST"].includes(role))) {
        navigate("/staff", { replace: true });
      } else {
        navigate(redirectTo, { replace: true });
      }
    } catch (err) {
      setError(err.message || "Nie udało się zalogować.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel narrow">
      <h1>Logowanie</h1>
      <p className="muted">Użyj konta pacjenta lub terapeuty. Dane demo: jan@example.com / Password123!</p>
      <form className="form" onSubmit={handleSubmit}>
        <label>
          E-mail
          <input name="email" type="email" value={form.email} onChange={updateField} placeholder="jan@example.com" />
        </label>
        <label>
          Hasło
          <input name="password" type="password" value={form.password} onChange={updateField} placeholder="Password123!" />
        </label>
        {error && <div className="form-error" role="alert">{error}</div>}
        <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? "Logowanie..." : "Zaloguj"}</button>
      </form>
      <p className="muted">Nie masz konta? <Link to="/register">Zarejestruj pacjenta</Link>.</p>
    </section>
  );
}
