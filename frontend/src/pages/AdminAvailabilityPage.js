import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

const EMPTY_RULE = {
  weekday: 1,
  startTime: "09:00",
  endTime: "17:00",
  validFrom: new Date().toISOString().slice(0, 10),
  validTo: "",
  isActive: true,
};

const EMPTY_EXCEPTION = {
  type: "UNAVAILABLE",
  startAt: "",
  endAt: "",
  reason: "",
};

export default function AdminAvailabilityPage() {
  const [therapists, setTherapists] = useState([]);
  const [selectedTherapistId, setSelectedTherapistId] = useState("");
  const [rules, setRules] = useState([]);
  const [exceptions, setExceptions] = useState([]);

  const [ruleForm, setRuleForm] = useState(EMPTY_RULE);
  const [exceptionForm, setExceptionForm] = useState(EMPTY_EXCEPTION);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadTherapists = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.adminTherapists();
      setTherapists(data);
      if (!selectedTherapistId && data[0]) {
        setSelectedTherapistId(data[0].id);
      }
    } catch (err) {
      setError(err.message || "Nie udało się pobrać terapeutów.");
    } finally {
      setLoading(false);
    }
  }, [selectedTherapistId]);

  const loadSchedule = useCallback(async () => {
    if (!selectedTherapistId) return;
    try {
      const [rulesData, exceptionsData] = await Promise.all([
        api.adminAvailabilityRules(selectedTherapistId),
        api.adminAvailabilityExceptions(selectedTherapistId),
      ]);
      setRules(rulesData);
      setExceptions(exceptionsData);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać grafiku.");
    }
  }, [selectedTherapistId]);

  useEffect(() => {
    loadTherapists();
  }, [loadTherapists]);

  useEffect(() => {
    loadSchedule();
  }, [loadSchedule]);

  async function addRule(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await api.createAvailabilityRule(selectedTherapistId, {
        ...ruleForm,
        validTo: ruleForm.validTo || null,
      });
      setRuleForm(EMPTY_RULE);
      setMessage("Reguła grafiku została dodana.");
      await loadSchedule();
    } catch (err) {
      setError(err.message || "Nie udało się dodać reguły.");
    }
  }

  async function removeRule(ruleId) {
    setError("");
    setMessage("");

    try {
      await api.deleteAvailabilityRule(ruleId);
      setMessage("Reguła została usunięta.");
      await loadSchedule();
    } catch (err) {
      setError(err.message || "Nie udało się usunąć reguły.");
    }
  }

  async function addException(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      await api.createAvailabilityException(selectedTherapistId, exceptionForm);
      setExceptionForm(EMPTY_EXCEPTION);
      setMessage("Wyjątek został dodany.");
      await loadSchedule();
    } catch (err) {
      setError(err.message || "Nie udało się dodać wyjątku.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !therapists.length) return <ErrorState message={error} onRetry={loadTherapists} />;

  return (
    <section className="page-section two-column">
      <div className="stack">
        <section className="panel">
          <h1>Zarządzanie grafikami</h1>

          {error && <div className="form-error">{error}</div>}
          {message && <div className="form-success">{message}</div>}

          <label className="inline-label">
            Terapeuta
            <select value={selectedTherapistId} onChange={(e) => setSelectedTherapistId(e.target.value)}>
              {therapists.map((therapist) => (
                <option key={therapist.id} value={therapist.id}>
                  {therapist.fullName}
                </option>
              ))}
            </select>
          </label>
        </section>

        <section className="panel">
          <h2>Dodaj regułę</h2>

          <form className="review-form" onSubmit={addRule}>
            <label>
              Dzień tygodnia (1-7)
              <input
                type="number"
                min="1"
                max="7"
                value={ruleForm.weekday}
                onChange={(e) => setRuleForm((c) => ({ ...c, weekday: Number(e.target.value) }))}
              />
            </label>

            <label>
              Od
              <input
                type="time"
                value={ruleForm.startTime}
                onChange={(e) => setRuleForm((c) => ({ ...c, startTime: e.target.value }))}
              />
            </label>

            <label>
              Do
              <input
                type="time"
                value={ruleForm.endTime}
                onChange={(e) => setRuleForm((c) => ({ ...c, endTime: e.target.value }))}
              />
            </label>

            <label>
              Ważne od
              <input
                type="date"
                value={ruleForm.validFrom}
                onChange={(e) => setRuleForm((c) => ({ ...c, validFrom: e.target.value }))}
              />
            </label>

            <label>
              Ważne do
              <input
                type="date"
                value={ruleForm.validTo}
                onChange={(e) => setRuleForm((c) => ({ ...c, validTo: e.target.value }))}
              />
            </label>

            <button className="btn btn-primary" type="submit">
              Dodaj regułę
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>Dodaj wyjątek</h2>

          <form className="review-form" onSubmit={addException}>
            <label>
              Typ
              <select
                value={exceptionForm.type}
                onChange={(e) => setExceptionForm((c) => ({ ...c, type: e.target.value }))}
              >
                <option value="UNAVAILABLE">UNAVAILABLE</option>
                <option value="EXTRA_AVAILABLE">EXTRA_AVAILABLE</option>
              </select>
            </label>

            <label>
              Start
              <input
                type="datetime-local"
                value={exceptionForm.startAt}
                onChange={(e) => setExceptionForm((c) => ({ ...c, startAt: e.target.value }))}
              />
            </label>

            <label>
              Koniec
              <input
                type="datetime-local"
                value={exceptionForm.endAt}
                onChange={(e) => setExceptionForm((c) => ({ ...c, endAt: e.target.value }))}
              />
            </label>

            <label>
              Powód
              <input
                value={exceptionForm.reason}
                onChange={(e) => setExceptionForm((c) => ({ ...c, reason: e.target.value }))}
              />
            </label>

            <button className="btn btn-primary" type="submit">
              Dodaj wyjątek
            </button>
          </form>
        </section>
      </div>

      <div className="stack">
        <section className="panel">
          <h2>Reguły grafiku</h2>

          {!rules.length ? (
            <EmptyState message="Brak reguł dla wybranego terapeuty." />
          ) : (
            <div className="stack">
              {rules.map((rule) => (
                <article className="panel" key={rule.id}>
                  <h3>Dzień tygodnia: {rule.weekday}</h3>
                  <p className="muted">
                    {rule.startTime} - {rule.endTime}
                  </p>
                  <p className="muted">
                    {rule.validFrom} {rule.validTo ? `do ${rule.validTo}` : ""}
                  </p>
                  <button className="btn btn-danger" onClick={() => removeRule(rule.id)}>
                    Usuń regułę
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <h2>Wyjątki</h2>

          {!exceptions.length ? (
            <EmptyState message="Brak wyjątków dla wybranego terapeuty." />
          ) : (
            <div className="stack">
              {exceptions.map((item) => (
                <article className="panel" key={item.id}>
                  <h3>{item.type}</h3>
                  <p className="muted">
                    {item.startAt} → {item.endAt}
                  </p>
                  <p>{item.reason || "Brak powodu"}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </section>
  );
}