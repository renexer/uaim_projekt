import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

function formatDateTime(value) {
  return new Date(value).toLocaleString("pl-PL", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function availabilityRange(days = 21) {
  const from = new Date();
  const to = new Date();
  to.setDate(to.getDate() + days);

  return {
    from: from.toISOString(),
    to: to.toISOString(),
  };
}

function groupSlotsByDay(slots) {
  const map = new Map();

  slots.forEach((slot) => {
    const dateKey = new Date(slot.startAt).toLocaleDateString("pl-PL", {
      weekday: "long",
      day: "2-digit",
      month: "2-digit",
    });

    if (!map.has(dateKey)) {
      map.set(dateKey, []);
    }
    map.get(dateKey).push(slot);
  });

  return Array.from(map.entries()).map(([day, values]) => ({
    day,
    slots: values,
  }));
}

export default function BookingPage() {
  const [services, setServices] = useState([]);
  const [therapists, setTherapists] = useState([]);
  const [availability, setAvailability] = useState(null);

  const [serviceId, setServiceId] = useState("");
  const [therapistId, setTherapistId] = useState("");

  const [loading, setLoading] = useState(true);
  const [availabilityLoading, setAvailabilityLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let ignore = false;

    async function loadServices() {
      setLoading(true);
      try {
        const data = await api.services();
        if (!ignore) {
          setServices(data);
          if (data[0]) {
            setServiceId(data[0].id);
          }
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać usług.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadServices();
    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    let ignore = false;

    async function loadTherapists() {
      if (!serviceId) return;

      try {
        const data = await api.therapists({ serviceId });
        if (!ignore) {
          setTherapists(data);
          setTherapistId(data[0]?.id || "");
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać terapeutów.");
        }
      }
    }

    loadTherapists();
    return () => {
      ignore = true;
    };
  }, [serviceId]);

  useEffect(() => {
    let ignore = false;

    async function loadAvailability() {
      if (!serviceId || !therapistId) return;

      setAvailabilityLoading(true);
      setError("");

      try {
        const { from, to } = availabilityRange();
        const data = await api.availability({ serviceId, therapistId, from, to });
        if (!ignore) {
          setAvailability(data);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać dostępnych terminów.");
        }
      } finally {
        if (!ignore) {
          setAvailabilityLoading(false);
        }
      }
    }

    loadAvailability();
    return () => {
      ignore = true;
    };
  }, [serviceId, therapistId]);

  const currentService = useMemo(
    () => services.find((item) => item.id === serviceId),
    [services, serviceId]
  );

  const currentTherapist = useMemo(
    () => therapists.find((item) => item.id === therapistId),
    [therapists, therapistId]
  );

  const slots = availability?.items?.[0]?.slots || [];
  const groupedSlots = groupSlotsByDay(slots);

  async function handleBooking(slot) {
    setError("");
    setMessage("");

    try {
      await api.createAppointment({
        serviceId,
        therapistId,
        startAt: slot.startAt,
      });

      setMessage("Wizyta została zarezerwowana.");
      const { from, to } = availabilityRange();
      const refreshed = await api.availability({ serviceId, therapistId, from, to });
      setAvailability(refreshed);
    } catch (err) {
      setError(err.message || "Nie udało się zarezerwować wizyty.");
    }
  }

  if (loading) return <LoadingState />;
  if (error && !services.length) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
    <section className="page-section booking-layout">
      <section className="panel booking-sidebar">
        <h1>Rezerwacja wizyty</h1>

        <label className="inline-label">
          Usługa
          <select value={serviceId} onChange={(event) => setServiceId(event.target.value)}>
            {services.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>
        </label>

        <label className="inline-label">
          Terapeuta
          <select value={therapistId} onChange={(event) => setTherapistId(event.target.value)}>
            {therapists.map((therapist) => (
              <option key={therapist.id} value={therapist.id}>
                {therapist.fullName}
              </option>
            ))}
          </select>
        </label>

        <div className="booking-summary">
          <h2>Podsumowanie wyboru</h2>
          <p><strong>Usługa:</strong> {currentService?.name || "—"}</p>
          <p><strong>Terapeuta:</strong> {currentTherapist?.fullName || "—"}</p>
          <p><strong>Czas trwania:</strong> {currentService?.durationMinutes || "—"} min</p>
          <p><strong>Cena:</strong> {currentService?.basePrice || "—"} {currentService?.currency || ""}</p>
        </div>
      </section>

      <section className="panel">
        <h2>Wolne terminy w najbliższych 21 dniach</h2>

        {error && <div className="form-error">{error}</div>}
        {message && <div className="form-success">{message}</div>}

        {availabilityLoading ? (
          <LoadingState message="Pobieranie terminów..." />
        ) : !groupedSlots.length ? (
          <EmptyState message="Brak wolnych terminów dla wybranego terapeuty i usługi." />
        ) : (
          <div className="stack">
            {groupedSlots.map((group) => (
              <article key={group.day} className="panel slot-day-card">
                <h3>{group.day}</h3>
                <div className="slot-grid">
                  {group.slots.map((slot) => (
                    <button
                      key={slot.startAt}
                      className="slot-button"
                      onClick={() => handleBooking(slot)}
                    >
                      {formatDateTime(slot.startAt)}
                    </button>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}