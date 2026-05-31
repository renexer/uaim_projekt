import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import Pagination from "../components/Pagination";
import StatCard from "../components/StatCard";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

function formatDateTime(value) {
  return new Date(value).toLocaleString("pl-PL", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

const STATUS_FILTERS = [
  { value: "", label: "Wszystkie" },
  { value: "BOOKED", label: "BOOKED" },
  { value: "COMPLETED", label: "COMPLETED" },
  { value: "NO_SHOW", label: "NO_SHOW" },
  { value: "CANCELLED_BY_CLINIC", label: "CANCELLED_BY_CLINIC" },
];

export default function StaffPage() {
  const [dashboard, setDashboard] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [meta, setMeta] = useState(null);

  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [patientEmail, setPatientEmail] = useState("");
  const [patientEmailInput, setPatientEmailInput] = useState("");

  const [summaryById, setSummaryById] = useState({});

  const [loading, setLoading] = useState(true);
  const [appointmentsLoading, setAppointmentsLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setPatientEmail(patientEmailInput.trim());
      setPage(1);
    }, 300);

    return () => clearTimeout(timer);
  }, [patientEmailInput]);

  const filters = useMemo(
    () => ({
      page,
      pageSize: 10,
      status: statusFilter || undefined,
      patientEmail: patientEmail || undefined,
    }),
    [page, statusFilter, patientEmail]
  );

  useEffect(() => {
    let ignore = false;

    async function loadAll() {
      setLoading(true);
      setError("");

      try {
        const [dashboardData, appointmentsData] = await Promise.all([
          api.staffDashboard(filters),
          api.staffAppointments(filters),
        ]);

        if (!ignore) {
          setDashboard(dashboardData);
          setAppointments(appointmentsData.items);
          setMeta(appointmentsData.meta);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać panelu staff.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadAll();
    return () => {
      ignore = true;
    };
  }, [filters]);

  async function changeStatus(appointmentId, status) {
    setError("");
    setMessage("");
    setAppointmentsLoading(true);

    try {
      await api.updateAppointmentStatus(appointmentId, status);

      const [dashboardData, appointmentsData] = await Promise.all([
        api.staffDashboard(filters),
        api.staffAppointments(filters),
      ]);

      setDashboard(dashboardData);
      setAppointments(appointmentsData.items);
      setMeta(appointmentsData.meta);
      setMessage("Status wizyty został zmieniony.");
    } catch (err) {
      setError(err.message || "Nie udało się zmienić statusu.");
    } finally {
      setAppointmentsLoading(false);
    }
  }

  async function saveSummary(appointmentId) {
    setError("");
    setMessage("");

    try {
      await api.upsertConsultationSummary(appointmentId, summaryById[appointmentId] || "");
      setMessage("Podsumowanie zostało zapisane.");
      setSummaryById((current) => ({ ...current, [appointmentId]: "" }));
    } catch (err) {
      setError(err.message || "Nie udało się zapisać podsumowania.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !dashboard) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Staff</p>
          <h1>Panel wizyt i obciążenia</h1>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard label="Wszystkie" value={dashboard?.totals?.all || 0} />
        <StatCard label="Dzisiaj" value={dashboard?.totals?.today || 0} />
        <StatCard label="BOOKED" value={dashboard?.totals?.booked || 0} />
        <StatCard label="COMPLETED" value={dashboard?.totals?.completed || 0} />
        <StatCard label="NO_SHOW" value={dashboard?.totals?.noShow || 0} />
      </div>

      <section className="panel">
        <h2>Najbliższe wizyty</h2>
        {!dashboard?.upcoming?.length ? (
          <EmptyState message="Brak nadchodzących wizyt." />
        ) : (
          <div className="stack">
            {dashboard.upcoming.map((item) => (
              <article className="upcoming-card" key={item.id}>
                <strong>{formatDateTime(item.startAt)}</strong>
                <span>{item.serviceName}</span>
                <span>{item.patientEmail}</span>
                <span className="muted">{item.therapistName}</span>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="filter-bar">
          <label className="inline-label compact">
            Status
            <select value={statusFilter} onChange={(event) => { setStatusFilter(event.target.value); setPage(1); }}>
              {STATUS_FILTERS.map((option) => (
                <option key={option.value || "all"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="inline-label compact">
            Email pacjenta
            <input
              value={patientEmailInput}
              onChange={(event) => setPatientEmailInput(event.target.value)}
              placeholder="np. jan@example.com"
            />
          </label>
        </div>

        {error && <div className="form-error">{error}</div>}
        {message && <div className="form-success">{message}</div>}

        {appointmentsLoading ? (
          <LoadingState message="Aktualizacja danych..." />
        ) : !appointments.length ? (
          <EmptyState message="Brak wizyt dla wybranych filtrów." />
        ) : (
          <>
            <div className="stack">
              {appointments.map((appointment) => (
                <article className="panel" key={appointment.id}>
                  <div className="section-heading compact-heading">
                    <div>
                      <h2>{appointment.serviceName}</h2>
                      <p className="muted">
                        {formatDateTime(appointment.startAt)} · {appointment.patientEmail}
                      </p>
                    </div>
                    <span className="status-pill">{appointment.status}</span>
                  </div>

                  <p className="muted">Terapeuta: {appointment.therapistName}</p>

                  <div className="button-row">
                    <button className="btn btn-outline" onClick={() => changeStatus(appointment.id, "COMPLETED")}>
                      Zakończ wizytę
                    </button>
                    <button className="btn btn-light" onClick={() => changeStatus(appointment.id, "NO_SHOW")}>
                      No-show
                    </button>
                    <button className="btn btn-danger" onClick={() => changeStatus(appointment.id, "CANCELLED_BY_CLINIC")}>
                      Odwołaj
                    </button>
                  </div>

                  <div className="review-form">
                    <label>
                      Podsumowanie konsultacji
                      <textarea
                        value={summaryById[appointment.id] || ""}
                        onChange={(event) =>
                          setSummaryById((current) => ({
                            ...current,
                            [appointment.id]: event.target.value,
                          }))
                        }
                        placeholder="Krótki opis konsultacji, przebieg, zalecenia..."
                      />
                    </label>

                    <button className="btn btn-primary" onClick={() => saveSummary(appointment.id)}>
                      Zapisz podsumowanie
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <Pagination meta={meta} onPageChange={setPage} />
          </>
        )}
      </section>
    </section>
  );
}