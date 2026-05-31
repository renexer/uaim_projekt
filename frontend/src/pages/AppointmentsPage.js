import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import Pagination from "../components/Pagination";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { formatDateTime } from "./pageUtils";

const SCOPE_OPTIONS = [
  { value: "upcoming", label: "Zaplanowane" },
  { value: "all", label: "Wszystkie" },
  { value: "cancelled", label: "Anulowane" },
];

export default function AppointmentsPage() {
  const [scope, setScope] = useState("upcoming");
  const [page, setPage] = useState(1);
  const [appointments, setAppointments] = useState([]);
  const [meta, setMeta] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancelReason, setCancelReason] = useState("");
  const [message, setMessage] = useState("");

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const payload = await api.myAppointments({
        scope,
        page,
        pageSize: 10,
      });
      setAppointments(payload.items);
      setMeta(payload.meta);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać wizyt.");
    } finally {
      setLoading(false);
    }
  }, [scope, page]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  useEffect(() => {
    setPage(1);
  }, [scope]);

  async function cancelAppointment(appointmentId) {
    setError("");
    setMessage("");

    try {
      await api.cancelAppointment(
        appointmentId,
        cancelReason || "Odwołanie przez pacjenta"
      );
      setMessage("Wizyta została anulowana.");
      setCancelReason("");
      await loadAppointments();
    } catch (err) {
      setError(err.message || "Nie udało się anulować wizyty.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !appointments.length) {
    return <ErrorState message={error} onRetry={loadAppointments} />;
  }

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Pacjent</p>
          <h1>Moje wizyty</h1>
        </div>
      </div>

      <div className="panel">
        <div className="filter-bar">
          <label className="inline-label compact">
            Zakres
            <select value={scope} onChange={(event) => setScope(event.target.value)}>
              {SCOPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="inline-label compact">
            Powód anulowania
            <input
              value={cancelReason}
              onChange={(event) => setCancelReason(event.target.value)}
              placeholder="opcjonalnie"
            />
          </label>
        </div>

        {error && <div className="form-error" role="alert">{error}</div>}
        {message && <div className="form-success" role="status">{message}</div>}

        {!appointments.length ? (
          <EmptyState message="Brak wizyt dla wybranego zakresu." />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Termin</th>
                    <th>Usługa</th>
                    <th>Terapeuta</th>
                    <th>Status</th>
                    <th>Akcja</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>{formatDateTime(appointment.startAt)}</td>
                      <td>{appointment.serviceName}</td>
                      <td>{appointment.therapistName}</td>
                      <td>
                        <span className={`status-pill ${appointment.status === "BOOKED" ? "" : "secondary"}`}>
                          {appointment.status}
                        </span>
                      </td>
                      <td>
                        {appointment.status === "BOOKED" ? (
                          <button
                            className="btn btn-danger"
                            onClick={() => cancelAppointment(appointment.id)}
                          >
                            Anuluj
                          </button>
                        ) : (
                          <span className="muted">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Pagination meta={meta} onPageChange={setPage} />
          </>
        )}
      </div>
    </section>
  );
}