import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { formatDateTime } from "./pageUtils";

export default function AppointmentsPage() {
  const [upcoming, setUpcoming] = useState([]);
  const [allAppointments, setAllAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [message, setMessage] = useState("");

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [upcomingData, allData] = await Promise.all([
        api.myAppointments("upcoming"),
        api.myAppointments("all"),
      ]);
      setUpcoming(upcomingData);
      setAllAppointments(allData);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać wizyt.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadAppointments(); }, [loadAppointments]);

  async function cancelAppointment(appointmentId) {
    setError("");
    setMessage("");
    try {
      await api.cancelAppointment(appointmentId, cancelReason || "Odwołanie przez pacjenta");
      setMessage("Wizyta została anulowana.");
      setCancelReason("");
      await loadAppointments();
    } catch (err) {
      setError(err.message || "Nie udało się anulować wizyty.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !allAppointments.length) return <ErrorState message={error} onRetry={loadAppointments} />;

  const archived = allAppointments.filter((item) => item.status !== "BOOKED");

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Pacjent</p>
          <h1>Moje wizyty</h1>
        </div>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
      {message && <div className="form-success" role="status">{message}</div>}
      <section className="panel">
        <h2>Zaplanowane wizyty</h2>
        <label className="inline-label compact">Powód anulowania <input value={cancelReason} onChange={(event) => setCancelReason(event.target.value)} placeholder="opcjonalnie" /></label>
        {!upcoming.length ? <EmptyState message="Nie masz zaplanowanych wizyt." /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Termin</th><th>Usługa</th><th>Terapeuta</th><th>Status</th><th>Akcja</th></tr></thead>
              <tbody>
                {upcoming.map((appointment) => (
                  <tr key={appointment.id}>
                    <td>{formatDateTime(appointment.startAt)}</td>
                    <td>{appointment.serviceName}</td>
                    <td>{appointment.therapistName}</td>
                    <td><span className="status-pill">{appointment.status}</span></td>
                    <td><button className="btn btn-danger" onClick={() => cancelAppointment(appointment.id)}>Anuluj</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Odbyte i anulowane wizyty</h2>
        {!archived.length ? <EmptyState message="Brak wizyt historycznych lub anulowanych." /> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Termin</th><th>Usługa</th><th>Terapeuta</th><th>Status</th></tr></thead>
              <tbody>
                {archived.map((appointment) => (
                  <tr key={appointment.id}>
                    <td>{formatDateTime(appointment.startAt)}</td>
                    <td>{appointment.serviceName}</td>
                    <td>{appointment.therapistName}</td>
                    <td><span className="status-pill secondary">{appointment.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}
