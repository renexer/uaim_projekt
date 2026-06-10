import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

const initialForm = {
  firstName: "",
  lastName: "",
  email: "",
  phone: "",
  password: "",
  confirmPassword: "",
};

export default function RegisterPage() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  function validate() {
    if (!form.firstName.trim() || !form.lastName.trim()) return "Podaj imię i nazwisko.";
    if (!form.email.includes("@")) return "Podaj poprawny adres e-mail.";
    if (form.password.length < 8) return "Hasło musi mieć minimum 8 znaków.";
    if (form.password !== form.confirmPassword) return "Hasła nie są takie same.";
    return "";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    try {
      await register({
        firstName: form.firstName.trim(),
        lastName: form.lastName.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
        password: form.password,
      });
      setSuccess("Konto zostało utworzone. Możesz się teraz zalogować.");
      setForm(initialForm);
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      setError(err.message || "Nie udało się utworzyć konta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel narrow">
      <h1>Rejestracja pacjenta</h1>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form-grid two">
          <label>Imię<input name="firstName" value={form.firstName} onChange={updateField} /></label>
          <label>Nazwisko<input name="lastName" value={form.lastName} onChange={updateField} /></label>
        </div>
        <label>E-mail<input name="email" type="email" value={form.email} onChange={updateField} /></label>
        <label>Telefon<input name="phone" value={form.phone} onChange={updateField} /></label>
        <div className="form-grid two">
          <label>Hasło<input name="password" type="password" value={form.password} onChange={updateField} /></label>
          <label>Powtórz hasło<input name="confirmPassword" type="password" value={form.confirmPassword} onChange={updateField} /></label>
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        {success && <div className="form-success" role="status">{success}</div>}
        <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? "Tworzenie konta..." : "Zarejestruj"}</button>
      </form>
      <p className="muted">Masz już konto? <Link to="/login">Przejdź do logowania</Link>.</p>
    </section>
  );
}
