import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../AuthContext";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { availabilityRange, formatDateTime, serviceLabel } from "./pageUtils";

export default function BookingPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [services, setServices] = useState([]);
  const [therapists, setTherapists] = useState([]);
  const [availability, setAvailability] = useState(null);
  const [loading, setLoading] = useState(true);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const serviceId = searchParams.get("serviceId") || "";
  const therapistId = searchParams.get("therapistId") || "";
  const selectedSlot = searchParams.get("slot") || "";

  const selectedService = useMemo(() => services.find((service) => service.id === serviceId), [services, serviceId]);
  const selectedTherapist = useMemo(() => therapists.find((therapist) => therapist.id === therapistId), [therapists, therapistId]);

  function updateParam(name, value) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(name, value);
    else next.delete(name);
    if (name === "serviceId") {
      next.delete("therapistId");
      next.delete("slot");
    }
    if (name === "therapistId") next.delete("slot");
    setSearchParams(next);
  }

  const loadServices = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.services();
      setServices(data);
      if (!serviceId && data[0]) {
        setSearchParams({ serviceId: data[0].id }, { replace: true });
      }
    } catch (err) {
      setError(err.message || "Nie udało się pobrać usług.");
    } finally {
      setLoading(false);
    }
  }, [serviceId, setSearchParams]);

  const loadTherapistsAndSlots = useCallback(async () => {
    if (!serviceId) return;
    setSlotsLoading(true);
    setError("");
    setMessage("");
    try {
      const therapistsData = await api.therapistsForService(serviceId);
      setTherapists(therapistsData);
      const { from, to } = availabilityRange();
      const availabilityData = await api.availability({ serviceId, therapistId: therapistId || null, from, to });
      setAvailability(availabilityData);
    } catch (err) {
      setError(err.message || "Nie udało się pobrać dostępnych terminów.");
      setAvailability(null);
    } finally {
      setSlotsLoading(false);
    }
  }, [serviceId, therapistId]);

  useEffect(() => { loadServices(); }, [loadServices]);
  useEffect(() => { loadTherapistsAndSlots(); }, [loadTherapistsAndSlots]);

  async function confirmBooking(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    if (!isAuthenticated) {
      navigate("/login", { state: { from: { pathname: "/booking" } } });
      return;
    }
    if (!serviceId || !therapistId || !selectedSlot) {
      setError("Wybierz usługę, terapeutę oraz termin.");
      return;
    }
    try {
      await api.createAppointment({ serviceId, therapistId, startAt: selectedSlot });
      setMessage("Wizyta została zarezerwowana. Potwierdzenie znajduje się w sekcji Moje wizyty.");
      const next = new URLSearchParams(searchParams);
      next.delete("slot");
      setSearchParams(next, { replace: true });
      await loadTherapistsAndSlots();
    } catch (err) {
      setError(err.message || "Nie udało się zarezerwować wizyty.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !services.length) return <ErrorState message={error} onRetry={loadServices} />;

  const items = availability?.items || [];
  const selectedItem = items.find((item) => item.therapist.id === therapistId);
  const availableSlots = selectedItem ? selectedItem.slots : items.flatMap((item) => item.slots.map((slot) => ({ ...slot, therapist: item.therapist })));

  return (
    <section className="page-section two-column booking-layout">
      <form className="panel form" onSubmit={confirmBooking}>
        <p className="eyebrow">Rezerwacja</p>
        <h1>Umów wizytę</h1>
        <label>
          Usługa
          <select value={serviceId} onChange={(event) => updateParam("serviceId", event.target.value)}>
            {services.map((service) => <option key={service.id} value={service.id}>{serviceLabel(service)}</option>)}
          </select>
        </label>
        <label>
          Terapeuta
          <select value={therapistId} onChange={(event) => updateParam("therapistId", event.target.value)}>
            <option value="">Dowolny dostępny terapeuta</option>
            {therapists.map((therapist) => <option key={therapist.id} value={therapist.id}>{therapist.fullName} — {therapist.title}</option>)}
          </select>
        </label>
        <div className="booking-summary">
          <strong>Podsumowanie</strong>
          <p>{selectedService ? selectedService.name : "Wybierz usługę"}</p>
          <p>{selectedTherapist ? selectedTherapist.fullName : "Terapeuta wybrany na podstawie slotu"}</p>
          <p>{selectedSlot ? formatDateTime(selectedSlot) : "Wybierz termin z listy"}</p>
        </div>
        {error && <div className="form-error" role="alert">{error}</div>}
        {message && <div className="form-success" role="status">{message}</div>}
        <button className="btn btn-primary" type="submit">Potwierdź rezerwację</button>
        {!isAuthenticated && <p className="muted">Do rezerwacji wymagane jest <Link to="/login">logowanie</Link>.</p>}
      </form>

      <section className="panel">
        <h2>Dostępne terminy</h2>
        {slotsLoading ? <LoadingState message="Pobieranie wolnych terminów..." /> : (
          availableSlots.length ? (
            <div className="slot-grid">
              {availableSlots.slice(0, 30).map((slot) => {
                const slotTherapist = slot.therapist || selectedItem?.therapist;
                return (
                  <button
                    type="button"
                    className={`slot-button ${selectedSlot === slot.startAt ? "selected" : ""}`}
                    key={`${slotTherapist?.id || therapistId}-${slot.startAt}`}
                    onClick={() => {
                      const next = new URLSearchParams(searchParams);
                      if (slotTherapist?.id) next.set("therapistId", slotTherapist.id);
                      next.set("slot", slot.startAt);
                      setSearchParams(next);
                    }}
                  >
                    <span>{formatDateTime(slot.startAt)}</span>
                    {slotTherapist && <small>{slotTherapist.fullName}</small>}
                  </button>
                );
              })}
            </div>
          ) : <EmptyState message="Brak dostępnych terminów w najbliższych 21 dniach." />
        )}
      </section>
    </section>
  );
}
