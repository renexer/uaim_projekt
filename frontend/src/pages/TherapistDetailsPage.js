import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import Pagination from "../components/Pagination";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { availabilityRange, formatDateTime, formatMoney, loadAllTherapists } from "./pageUtils";

export default function TherapistDetailsPage() {
  const { therapistId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const selectedServiceId = searchParams.get("serviceId") || "";

  const [therapist, setTherapist] = useState(null);
  const [services, setServices] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [reviewsMeta, setReviewsMeta] = useState(null);
  const [reviewsPage, setReviewsPage] = useState(1);
  const [availability, setAvailability] = useState(null);

  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [availabilityLoading, setAvailabilityLoading] = useState(false);

  const [error, setError] = useState("");
  const [bookingError, setBookingError] = useState("");
  const [bookingSuccess, setBookingSuccess] = useState("");

  const selectedService = useMemo(
    () => services.find((service) => service.id === selectedServiceId),
    [services, selectedServiceId]
  );

  const loadBase = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [therapistData, allTherapists] = await Promise.all([
        api.therapist(therapistId),
        loadAllTherapists(api),
      ]);

      const aggregatedTherapist = allTherapists.find((item) => item.id === therapistId);
      const therapistServices = aggregatedTherapist?.services || [];

      setTherapist(therapistData);
      setServices(therapistServices);

      if (!selectedServiceId && therapistServices[0]) {
        setSearchParams({ serviceId: therapistServices[0].id }, { replace: true });
      }
    } catch (err) {
      setError(err.message || "Nie udało się pobrać danych terapeuty.");
    } finally {
      setLoading(false);
    }
  }, [therapistId, selectedServiceId, setSearchParams]);

  const loadReviews = useCallback(async () => {
    setReviewsLoading(true);
    try {
      const payload = await api.reviews(therapistId, { page: reviewsPage, pageSize: 5 });
      setReviews(payload.items);
      setReviewsMeta(payload.meta);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać opinii.");
    } finally {
      setReviewsLoading(false);
    }
  }, [therapistId, reviewsPage]);

  const loadAvailability = useCallback(async () => {
    if (!selectedServiceId) {
      setAvailability(null);
      return;
    }

    setAvailabilityLoading(true);
    setBookingError("");

    try {
      const { from, to } = availabilityRange();
      const payload = await api.availability({
        serviceId: selectedServiceId,
        therapistId,
        from,
        to,
      });
      setAvailability(payload);
    } catch (err) {
      setBookingError(err.message || "Nie udało się pobrać terminów.");
      setAvailability(null);
    } finally {
      setAvailabilityLoading(false);
    }
  }, [selectedServiceId, therapistId]);

  useEffect(() => {
    loadBase();
  }, [loadBase]);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  useEffect(() => {
    loadAvailability();
  }, [loadAvailability]);

  async function bookSlot(slot) {
    setBookingError("");
    setBookingSuccess("");

    if (!isAuthenticated) {
      navigate("/login", {
        state: {
          from: {
            pathname: location.pathname,
            search: location.search,
          },
        },
      });
      return;
    }

    try {
      await api.createAppointment({
        serviceId: selectedServiceId,
        therapistId,
        startAt: slot.startAt,
      });
      setBookingSuccess("Wizyta została zarezerwowana.");
      await loadAvailability();
    } catch (err) {
      setBookingError(err.message || "Nie udało się zarezerwować terminu.");
    }
  }

  function handleServiceChange(event) {
    const next = new URLSearchParams(searchParams);
    next.set("serviceId", event.target.value);
    setSearchParams(next);
  }

  if (loading) return <LoadingState />;
  if (error && !therapist) return <ErrorState message={error} onRetry={loadBase} />;

  const slots = availability?.items?.[0]?.slots || [];

  return (
    <section className="page-section two-column">
      <article className="panel profile-panel">
        <div className="avatar large">{therapist?.fullName?.slice(0, 1) || "T"}</div>
        <h1>{therapist?.fullName}</h1>
        <p className="muted">{therapist?.title}</p>
        <p>{therapist?.bio}</p>

        <dl className="meta-list">
          <div>
            <dt>Doświadczenie</dt>
            <dd>{therapist?.experienceYears || 0} lat</dd>
          </div>
          <div>
            <dt>Ocena</dt>
            <dd>★ {therapist?.averageRating || "0.0"} ({therapist?.reviewsCount || 0})</dd>
          </div>
        </dl>

        <Link className="btn btn-light" to="/therapists">
          Wróć do listy
        </Link>
      </article>

      <div className="stack">
        <section className="panel">
          <h2>Dostępne terminy</h2>

          {!services.length ? (
            <EmptyState message="Ten terapeuta nie ma przypisanych usług." />
          ) : (
            <>
              <label className="inline-label">
                Usługa
                <select value={selectedServiceId} onChange={handleServiceChange}>
                  {services.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name}
                    </option>
                  ))}
                </select>
              </label>

              {selectedService && (
                <p className="muted">
                  {selectedService.name} · {selectedService.durationMinutes} min ·{" "}
                  {formatMoney(selectedService.basePrice, selectedService.currency || "PLN")}
                </p>
              )}

              {bookingError && <div className="form-error" role="alert">{bookingError}</div>}
              {bookingSuccess && <div className="form-success" role="status">{bookingSuccess}</div>}

              {availabilityLoading ? (
                <LoadingState message="Pobieranie terminów..." />
              ) : slots.length ? (
                <div className="slot-grid">
                  {slots.slice(0, 18).map((slot) => (
                    <button
                      className="slot-button"
                      key={slot.startAt}
                      onClick={() => bookSlot(slot)}
                    >
                      {formatDateTime(slot.startAt)}
                    </button>
                  ))}
                </div>
              ) : (
                <EmptyState message="Brak wolnych terminów w najbliższych 21 dniach." />
              )}
            </>
          )}
        </section>

        <section className="panel">
          <h2>Opinie pacjentów</h2>

          {reviewsLoading ? (
            <LoadingState message="Pobieranie opinii..." />
          ) : !reviews.length ? (
            <EmptyState message="Ten terapeuta nie ma jeszcze opublikowanych opinii." />
          ) : (
            <>
              <div className="review-list">
                {reviews.map((review) => (
                  <article className="review" key={review.id}>
                    <strong>★ {review.rating}/5</strong>
                    <p>{review.comment || "Bez komentarza."}</p>
                    <span className="muted">{formatDateTime(review.createdAt)}</span>
                  </article>
                ))}
              </div>

              <Pagination meta={reviewsMeta} onPageChange={setReviewsPage} />
            </>
          )}
        </section>
      </div>
    </section>
  );
}