import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { formatDateTime } from "./pageUtils";

export default function StaffPage() {
  const [appointments, setAppointments] = useState([]);
  const [summaryById, setSummaryById] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setAppointments(await api.staffAppointments());
    } catch (err) {
      setError(err.message || "Nie udało się pobrać grafiku terapeuty.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAppointments(); }, [loadAppointments]);

  async function changeStatus(appointmentId, status) {
    setError("");
    setMessage("");
    try {
      await api.updateAppointmentStatus(appointmentId, status);
      setMessage("Status wizyty został zmieniony.");
      await loadAppointments();
    } catch (err) {
      setError(err.message || "Nie udało się zmienić statusu.");
    }
  }

  async function saveSummary(appointmentId) {
    const text = summaryById[appointmentId] || "";
    setError("");
    setMessage("");
    try {
      await api.upsertConsultationSummary(appointmentId, text);
      setMessage("Podsumowanie konsultacji zostało zapisane.");
      setSummaryById((current) => ({ ...current, [appointmentId]: "" }));
    } catch (err) {
      setError(err.message || "Nie udało się zapisać podsumowania.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !appointments.length) return <ErrorState message={error} onRetry={loadAppointments} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Terapeuta / staff</p>
          <h1>Panel wizyt</h1>
        </div>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
      {message && <div className="form-success" role="status">{message}</div>}
      {!appointments.length ? <EmptyState message="Brak wizyt w grafiku." /> : (
        <div className="stack">
          {appointments.map((appointment) => (
            <article className="panel" key={appointment.id}>
              <div className="section-heading compact-heading">
                <div>
                  <h2>{appointment.serviceName}</h2>
                  <p className="muted">{formatDateTime(appointment.startAt)} · pacjent: {appointment.patientEmail}</p>
                  <p className="muted">Terapeuta: {appointment.therapistName}</p>
                </div>
                <span className="status-pill">{appointment.status}</span>
              </div>
              <div className="button-row">
                <button className="btn btn-outline" onClick={() => changeStatus(appointment.id, "COMPLETED")}>Oznacz jako zakończoną</button>
                <button className="btn btn-light" onClick={() => changeStatus(appointment.id, "NO_SHOW")}>Nieobecność</button>
                <button className="btn btn-danger" onClick={() => changeStatus(appointment.id, "CANCELLED_BY_CLINIC")}>Odwołaj przez gabinet</button>
              </div>
              <div className="review-form">
                <label>
                  Podsumowanie konsultacji
                  <textarea value={summaryById[appointment.id] || ""} onChange={(event) => setSummaryById((current) => ({ ...current, [appointment.id]: event.target.value }))} placeholder="Wpisz krótkie podsumowanie lub zalecenia dla pacjenta" />
                </label>
                <button className="btn btn-primary" onClick={() => saveSummary(appointment.id)}>Zapisz podsumowanie</button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
