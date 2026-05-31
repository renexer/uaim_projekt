import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { formatDateTime } from "./pageUtils";

export default function ConsultationsPage() {
  const [consultations, setConsultations] = useState([]);
  const [ratingById, setRatingById] = useState({});
  const [commentById, setCommentById] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadConsultations = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setConsultations(await api.consultations());
    } catch (err) {
      setError(err.message || "Nie udało się pobrać historii konsultacji.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadConsultations(); }, [loadConsultations]);

  async function addReview(appointmentId) {
    setError("");
    setMessage("");
    try {
      await api.createReview(appointmentId, {
        rating: Number(ratingById[appointmentId] || 5),
        comment: commentById[appointmentId] || "",
      });
      setMessage("Opinia została dodana i oczekuje na publikację.");
      await loadConsultations();
    } catch (err) {
      setError(err.message || "Nie udało się dodać opinii.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !consultations.length) return <ErrorState message={error} onRetry={loadConsultations} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Historia</p>
          <h1>Historia konsultacji i opinie</h1>
        </div>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
      {message && <div className="form-success" role="status">{message}</div>}
      {!consultations.length ? <EmptyState message="Brak zakończonych konsultacji." /> : (
        <div className="stack">
          {consultations.map((consultation) => (
            <article className="panel" key={consultation.appointmentId}>
              <div className="section-heading compact-heading">
                <div>
                  <h2>{consultation.service?.name}</h2>
                  <p className="muted">{formatDateTime(consultation.completedAt)} · {consultation.therapist?.name}</p>
                </div>
                <span className="status-pill secondary">zakończona</span>
              </div>
              <p><strong>Podsumowanie terapeuty:</strong></p>
              <p>{consultation.summary?.text || "Brak podsumowania w systemie."}</p>
              {consultation.review?.exists ? (
                <p className="form-success">Opinia została już dodana.</p>
              ) : (
                <div className="review-form">
                  <label>
                    Ocena
                    <select value={ratingById[consultation.appointmentId] || 5} onChange={(event) => setRatingById((current) => ({ ...current, [consultation.appointmentId]: event.target.value }))}>
                      {[5, 4, 3, 2, 1].map((rating) => <option key={rating} value={rating}>{rating}</option>)}
                    </select>
                  </label>
                  <label>
                    Komentarz
                    <textarea value={commentById[consultation.appointmentId] || ""} onChange={(event) => setCommentById((current) => ({ ...current, [consultation.appointmentId]: event.target.value }))} placeholder="Opisz swoje wrażenia po konsultacji" />
                  </label>
                  <button className="btn btn-primary" onClick={() => addReview(consultation.appointmentId)}>Dodaj opinię</button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
