import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

const EMPTY_FORM = {
  code: "",
  name: "",
  description: "",
  durationMinutes: 50,
  basePrice: "200.00",
  currency: "PLN",
  isActive: true,
};

export default function AdminServicesPage() {
  const [services, setServices] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadServices = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.adminServices();
      setServices(data);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać usług.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadServices();
  }, [loadServices]);

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function startEdit(service) {
    setEditingId(service.id);
    setForm({
      code: service.code,
      name: service.name,
      description: service.description,
      durationMinutes: service.durationMinutes,
      basePrice: service.basePrice,
      currency: service.currency,
      isActive: service.isActive,
    });
    setMessage("");
    setError("");
  }

  function resetForm() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      if (editingId) {
        await api.updateAdminService(editingId, form);
        setMessage("Usługa została zaktualizowana.");
      } else {
        await api.createAdminService(form);
        setMessage("Usługa została dodana.");
      }
      resetForm();
      await loadServices();
    } catch (err) {
      setError(err.message || "Nie udało się zapisać usługi.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !services.length) return <ErrorState message={error} onRetry={loadServices} />;

  return (
    <section className="page-section two-column">
      <section className="panel">
        <h1>Zarządzanie usługami</h1>

        {error && <div className="form-error">{error}</div>}
        {message && <div className="form-success">{message}</div>}

        <form className="review-form" onSubmit={handleSubmit}>
          <label>
            Kod
            <input value={form.code} onChange={(e) => updateField("code", e.target.value)} required />
          </label>

          <label>
            Nazwa
            <input value={form.name} onChange={(e) => updateField("name", e.target.value)} required />
          </label>

          <label>
            Opis
            <textarea value={form.description} onChange={(e) => updateField("description", e.target.value)} required />
          </label>

          <label>
            Czas trwania (min)
            <input
              type="number"
              value={form.durationMinutes}
              onChange={(e) => updateField("durationMinutes", Number(e.target.value))}
              required
            />
          </label>

          <label>
            Cena
            <input value={form.basePrice} onChange={(e) => updateField("basePrice", e.target.value)} required />
          </label>

          <label>
            Waluta
            <input value={form.currency} onChange={(e) => updateField("currency", e.target.value)} required />
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.isActive}
              onChange={(e) => updateField("isActive", e.target.checked)}
            />
            Aktywna
          </label>

          <div className="button-row">
            <button className="btn btn-primary" type="submit">
              {editingId ? "Zapisz zmiany" : "Dodaj usługę"}
            </button>
            {editingId && (
              <button className="btn btn-light" type="button" onClick={resetForm}>
                Anuluj edycję
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>Lista usług</h2>

        {!services.length ? (
          <EmptyState message="Brak usług w systemie." />
        ) : (
          <div className="stack">
            {services.map((service) => (
              <article className="panel" key={service.id}>
                <div className="section-heading compact-heading">
                  <div>
                    <h3>{service.name}</h3>
                    <p className="muted">
                      {service.code} · {service.durationMinutes} min · {service.basePrice} {service.currency}
                    </p>
                  </div>
                  <span className={`status-pill ${service.isActive ? "" : "secondary"}`}>
                    {service.isActive ? "AKTYWNA" : "NIEAKTYWNA"}
                  </span>
                </div>

                <p>{service.description}</p>

                <button className="btn btn-outline" onClick={() => startEdit(service)}>
                  Edytuj
                </button>
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}