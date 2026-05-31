import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { availabilityRange, formatDateTime } from "./pageUtils";

export default function TherapistDetailsPage() {
  const { therapistId } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedServiceId = searchParams.get("serviceId") || "";
  const [therapist, setTherapist] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [services, setServices] = useState([]);
  const [availability, setAvailability] = useState(null);
  const [loading, setLoading] = useState(true);
  const [availabilityLoading, setAvailabilityLoading] = useState(false);
  const [error, setError] = useState("");
  const [bookingError, setBookingError] = useState("");
  const [bookingSuccess, setBookingSuccess] = useState("");
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const selectedService = useMemo(() => services.find((service) => service.id === selectedServiceId), [services, selectedServiceId]);

  const loadDetails = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [therapistData, reviewsData, servicesData] = await Promise.all([
        api.therapist(therapistId),
        api.reviews(therapistId),
        api.services(),
      ]);
      setTherapist(therapistData);
      setReviews(reviewsData);
      setServices(servicesData);
      if (!selectedServiceId && servicesData[0]) {
        setSearchParams({ serviceId: servicesData[0].id }, { replace: true });
      }
    } catch (err) {
      setError(err.message || "Nie udało się pobrać danych terapeuty.");
    } finally {
      setLoading(false);
    }
  }, [therapistId, selectedServiceId, setSearchParams]);

  const loadAvailability = useCallback(async () => {
    if (!selectedServiceId) return;
    setAvailabilityLoading(true);
    setBookingError("");
    const { from, to } = availabilityRange();
    try {
      setAvailability(await api.availability({ serviceId: selectedServiceId, therapistId, from, to }));
    } catch (err) {
      setBookingError(err.message || "Nie udało się pobrać terminów.");
      setAvailability(null);
    } finally {
      setAvailabilityLoading(false);
    }
  }, [selectedServiceId, therapistId]);

  useEffect(() => {
    loadDetails();
  }, [loadDetails]);

  useEffect(() => {
    loadAvailability();
  }, [loadAvailability]);

  async function bookSlot(slot) {
    setBookingError("");
    setBookingSuccess("");
    if (!isAuthenticated) {
      navigate("/login", { state: { from: { pathname: `/therapists/${therapistId}` } } });
      return;
    }
    try {
      await api.createAppointment({ serviceId: selectedServiceId, therapistId, startAt: slot.startAt });
      setBookingSuccess("Wizyta została zarezerwowana.");
      await loadAvailability();
    } catch (err) {
      setBookingError(err.message || "Nie udało się zarezerwować terminu.");
    }
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadDetails} />;

  const slots = availability?.items?.[0]?.slots || [];

  return (
    <section className="page-section two-column">
      <article className="panel profile-panel">
        <div className="avatar large">{therapist?.fullName?.slice(0, 1) || "T"}</div>
        <h1>{therapist?.fullName}</h1>
        <p className="muted">{therapist?.title}</p>
        <p>{therapist?.bio}</p>
        <dl className="meta-list">
          <div><dt>Doświadczenie</dt><dd>{therapist?.experienceYears || 0} lat</dd></div>
          <div><dt>Ocena</dt><dd>★ {therapist?.averageRating || "0.0"} ({therapist?.reviewsCount || 0})</dd></div>
        </dl>
        <Link className="btn btn-light" to="/therapists">Wróć do listy</Link>
      </article>

      <div className="stack">
        <section className="panel">
          <h2>Dostępne terminy</h2>
          <label className="inline-label">
            Usługa
            <select value={selectedServiceId} onChange={(event) => setSearchParams({ serviceId: event.target.value })}>
              {services.map((service) => <option value={service.id} key={service.id}>{service.name}</option>)}
            </select>
          </label>
          {selectedService && <p className="muted">{selectedService.durationMinutes} min · {selectedService.basePrice} {selectedService.currency}</p>}
          {bookingError && <div className="form-error" role="alert">{bookingError}</div>}
          {bookingSuccess && <div className="form-success" role="status">{bookingSuccess}</div>}
          {availabilityLoading ? <LoadingState message="Pobieranie terminów..." /> : (
            slots.length ? (
              <div className="slot-grid">
                {slots.slice(0, 18).map((slot) => (
                  <button className="slot-button" key={slot.startAt} onClick={() => bookSlot(slot)}>
                    {formatDateTime(slot.startAt)}
                  </button>
                ))}
              </div>
            ) : <EmptyState message="Brak wolnych terminów w najbliższych 21 dniach." />
          )}
        </section>

        <section className="panel">
          <h2>Opinie pacjentów</h2>
          {!reviews.length ? <EmptyState message="Ten terapeuta nie ma jeszcze opublikowanych opinii." /> : (
            <div className="review-list">
              {reviews.map((review) => (
                <article className="review" key={review.id}>
                  <strong>★ {review.rating}/5</strong>
                  <p>{review.comment || "Bez komentarza."}</p>
                  <span className="muted">{formatDateTime(review.createdAt)}</span>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
