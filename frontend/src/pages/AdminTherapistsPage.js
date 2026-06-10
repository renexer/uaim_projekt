import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

const EMPTY_FORM = {
  userId: "",
  title: "",
  bio: "",
  experienceYears: 0,
  photoUrl: "",
  isActive: true,
};

const EMPTY_ASSIGNMENT = {
  serviceId: "",
  priceOverride: "",
  durationOverrideMinutes: "",
  isActive: true,
};

export default function AdminTherapistsPage() {
  const [therapists, setTherapists] = useState([]);
  const [services, setServices] = useState([]);

  const [form, setForm] = useState(EMPTY_FORM);
  const [assignment, setAssignment] = useState(EMPTY_ASSIGNMENT);

  const [selectedTherapistId, setSelectedTherapistId] = useState("");
  const [editingId, setEditingId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [therapistsData, servicesData] = await Promise.all([
        api.adminTherapists(),
        api.adminServices(),
      ]);
      setTherapists(therapistsData);
      setServices(servicesData.filter((item) => item.isActive));
    } catch (err) {
      setError(err.message || "Nie udało się pobrać terapeutów.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  function updateForm(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function updateAssignment(name, value) {
    setAssignment((current) => ({ ...current, [name]: value }));
  }

  function startEdit(therapist) {
    setEditingId(therapist.id);
    setForm({
      userId: therapist.userId || "",
      title: therapist.title || "",
      bio: therapist.bio || "",
      experienceYears: therapist.experienceYears || 0,
      photoUrl: therapist.photoUrl || "",
      isActive: therapist.isActive,
    });
    setMessage("");
    setError("");
  }

  function resetForm() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function saveTherapist(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      if (editingId) {
        await api.updateAdminTherapist(editingId, form);
        setMessage("Profil terapeuty został zaktualizowany.");
      } else {
        await api.createAdminTherapist(form);
        setMessage("Profil terapeuty został utworzony.");
      }
      resetForm();
      await loadData();
    } catch (err) {
      setError(err.message || "Nie udało się zapisać terapeuty.");
    }
  }

  async function assignService(event) {
    event.preventDefault();

    if (!selectedTherapistId) {
      setError("Najpierw wybierz terapeutę.");
      return;
    }

    setError("");
    setMessage("");

    try {
      await api.assignServiceToTherapist(selectedTherapistId, {
        ...assignment,
        durationOverrideMinutes: assignment.durationOverrideMinutes
          ? Number(assignment.durationOverrideMinutes)
          : null,
      });
      setMessage("Usługa została przypisana terapeucie.");
      setAssignment(EMPTY_ASSIGNMENT);
      await loadData();
    } catch (err) {
      setError(err.message || "Nie udało się przypisać usługi.");
    }
  }

  async function removeService(serviceId) {
    if (!selectedTherapistId) return;

    setError("");
    setMessage("");

    try {
      await api.removeServiceFromTherapist(selectedTherapistId, serviceId);
      setMessage("Powiązanie z usługą zostało dezaktywowane.");
      await loadData();
    } catch (err) {
      setError(err.message || "Nie udało się usunąć przypisania.");
    }
  }

  const selectedTherapist = therapists.find((item) => item.id === selectedTherapistId);

  if (loading) return <LoadingState />;
  if (error && !therapists.length) return <ErrorState message={error} onRetry={loadData} />;

  return (
    <section className="page-section two-column">
      <div className="stack">
        <section className="panel">
          <h1>Zarządzanie terapeutami</h1>

          {error && <div className="form-error">{error}</div>}
          {message && <div className="form-success">{message}</div>}

          <form className="review-form" onSubmit={saveTherapist}>
            {!editingId && (
              <label>
                User ID
                <input value={form.userId} onChange={(e) => updateForm("userId", e.target.value)} required />
              </label>
            )}

            <label>
              Tytuł
              <input value={form.title} onChange={(e) => updateForm("title", e.target.value)} required />
            </label>

            <label>
              Bio
              <textarea value={form.bio} onChange={(e) => updateForm("bio", e.target.value)} required />
            </label>

            <label>
              Doświadczenie (lata)
              <input
                type="number"
                value={form.experienceYears}
                onChange={(e) => updateForm("experienceYears", Number(e.target.value))}
              />
            </label>

            <label>
              URL zdjęcia
              <input value={form.photoUrl} onChange={(e) => updateForm("photoUrl", e.target.value)} />
            </label>

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={form.isActive}
                onChange={(e) => updateForm("isActive", e.target.checked)}
              />
              Aktywny
            </label>

            <div className="button-row">
              <button className="btn btn-primary" type="submit">
                {editingId ? "Zapisz zmiany" : "Dodaj terapeutę"}
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
          <h2>Przypisanie usługi terapeucie</h2>

          <label className="inline-label">
            Terapeuta
            <select value={selectedTherapistId} onChange={(e) => setSelectedTherapistId(e.target.value)}>
              <option value="">Wybierz terapeutę</option>
              {therapists.map((therapist) => (
                <option key={therapist.id} value={therapist.id}>
                  {therapist.fullName}
                </option>
              ))}
            </select>
          </label>

          <form className="review-form" onSubmit={assignService}>
            <label>
              Usługa
              <select value={assignment.serviceId} onChange={(e) => updateAssignment("serviceId", e.target.value)} required>
                <option value="">Wybierz usługę</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Price override
              <input
                value={assignment.priceOverride}
                onChange={(e) => updateAssignment("priceOverride", e.target.value)}
                placeholder="np. 230.00"
              />
            </label>

            <label>
              Duration override (min)
              <input
                type="number"
                value={assignment.durationOverrideMinutes}
                onChange={(e) => updateAssignment("durationOverrideMinutes", e.target.value)}
              />
            </label>

            <button className="btn btn-primary" type="submit">
              Przypisz usługę
            </button>
          </form>

          {selectedTherapist?.services?.length ? (
            <div className="stack">
              {selectedTherapist.services.map((service) => (
                <article className="panel" key={service.id}>
                  <h3>{service.name}</h3>
                  <p className="muted">
                    {service.durationMinutes} min · {service.basePrice} {service.currency}
                  </p>
                  <button className="btn btn-danger" onClick={() => removeService(service.id)}>
                    Dezaktywuj powiązanie
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState message="Wybrany terapeuta nie ma jeszcze przypisanych usług." />
          )}
        </section>
      </div>

      <section className="panel">
        <h2>Lista terapeutów</h2>

        {!therapists.length ? (
          <EmptyState message="Brak terapeutów." />
        ) : (
          <div className="stack">
            {therapists.map((therapist) => (
              <article className="panel" key={therapist.id}>
                <div className="section-heading compact-heading">
                  <div>
                    <h3>{therapist.fullName}</h3>
                    <p className="muted">{therapist.title}</p>
                  </div>
                  <span className={`status-pill ${therapist.isActive ? "" : "secondary"}`}>
                    {therapist.isActive ? "AKTYWNY" : "NIEAKTYWNY"}
                  </span>
                </div>

                <p>{therapist.bio}</p>

                <div className="button-row">
                  <button className="btn btn-outline" onClick={() => startEdit(therapist)}>
                    Edytuj
                  </button>
                  <button className="btn btn-light" onClick={() => setSelectedTherapistId(therapist.id)}>
                    Wybierz do przypisań
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}