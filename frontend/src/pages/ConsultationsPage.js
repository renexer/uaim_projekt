import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { downloadCsv } from "../utils/exportCsv";

function formatDateTime(value) {
  return new Date(value).toLocaleString("pl-PL", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function ConsultationsPage() {
  const [consultations, setConsultations] = useState([]);
  const [search, setSearch] = useState("");
  const [reviewFilter, setReviewFilter] = useState("all");

  const [ratingById, setRatingById] = useState({});
  const [commentById, setCommentById] = useState({});

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let ignore = false;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const payload = await api.consultations({ page: 1, pageSize: 100 });
        if (!ignore) {
          setConsultations(payload.items);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać historii konsultacji.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      ignore = true;
    };
  }, []);

  const filteredConsultations = useMemo(() => {
    return consultations.filter((item) => {
      const haystack = [
        item.service?.name,
        item.service?.description,
        item.therapist?.name,
        item.therapist?.title,
        item.summary?.text,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch = !search.trim() || haystack.includes(search.trim().toLowerCase());

      const matchesReview =
        reviewFilter === "all" ||
        (reviewFilter === "withReview" && item.review?.exists) ||
        (reviewFilter === "withoutReview" && !item.review?.exists);

      return matchesSearch && matchesReview;
    });
  }, [consultations, search, reviewFilter]);

  async function addReview(appointmentId) {
    setError("");
    setMessage("");

    try {
      await api.createReview(appointmentId, {
        rating: Number(ratingById[appointmentId] || 5),
        comment: commentById[appointmentId] || "",
      });

      setConsultations((current) =>
        current.map((item) =>
          item.appointmentId === appointmentId
            ? { ...item, review: { exists: true } }
            : item
        )
      );

      setMessage("Opinia została dodana.");
    } catch (err) {
      setError(err.message || "Nie udało się dodać opinii.");
    }
  }

  function exportHistory() {
    const rows = filteredConsultations.map((item) => ({
      termin: formatDateTime(item.completedAt),
      usluga: item.service?.name || "",
      terapeuta: item.therapist?.name || "",
      summary: item.summary?.text || "",
      opinia_dodana: item.review?.exists ? "tak" : "nie",
    }));

    downloadCsv("historia_konsultacji.csv", rows);
  }

  if (loading) return <LoadingState />;
  if (error && !consultations.length) {
    return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  }

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Historia</p>
          <h1>Historia konsultacji</h1>
        </div>

        <button className="btn btn-light" onClick={exportHistory}>
          Eksportuj CSV
        </button>
      </div>

      <section className="panel">
        <div className="filter-bar">
          <label className="inline-label compact">
            Szukaj
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="usługa, terapeuta, summary..."
            />
          </label>

          <label className="inline-label compact">
            Opinia
            <select value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value)}>
              <option value="all">Wszystkie</option>
              <option value="withReview">Tylko z opinią</option>
              <option value="withoutReview">Tylko bez opinii</option>
            </select>
          </label>
        </div>
      </section>

      {error && <div className="form-error">{error}</div>}
      {message && <div className="form-success">{message}</div>}

      {!filteredConsultations.length ? (
        <EmptyState message="Brak konsultacji spełniających wybrane kryteria." />
      ) : (
        <div className="stack">
          {filteredConsultations.map((consultation) => (
            <article className="panel" key={consultation.appointmentId}>
              <div className="section-heading compact-heading">
                <div>
                  <h2>{consultation.service?.name}</h2>
                  <p className="muted">
                    {formatDateTime(consultation.completedAt)} · {consultation.therapist?.name}
                  </p>
                </div>
                <span className="status-pill secondary">zakończona</span>
              </div>

              <p><strong>Opis usługi:</strong> {consultation.service?.description}</p>
              <p><strong>Podsumowanie terapeuty:</strong> {consultation.summary?.text || "Brak podsumowania."}</p>

              {consultation.review?.exists ? (
                <p className="form-success">Opinia została już dodana.</p>
              ) : (
                <div className="review-form">
                  <label>
                    Ocena
                    <select
                      value={ratingById[consultation.appointmentId] || 5}
                      onChange={(event) =>
                        setRatingById((current) => ({
                          ...current,
                          [consultation.appointmentId]: event.target.value,
                        }))
                      }
                    >
                      {[5, 4, 3, 2, 1].map((rating) => (
                        <option key={rating} value={rating}>
                          {rating}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Komentarz
                    <textarea
                      value={commentById[consultation.appointmentId] || ""}
                      onChange={(event) =>
                        setCommentById((current) => ({
                          ...current,
                          [consultation.appointmentId]: event.target.value,
                        }))
                      }
                      placeholder="Opisz swoją ocenę wizyty"
                    />
                  </label>

                  <button
                    className="btn btn-primary"
                    onClick={() => addReview(consultation.appointmentId)}
                  >
                    Dodaj opinię
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}