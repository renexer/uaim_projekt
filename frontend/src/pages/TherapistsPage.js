import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";

export default function TherapistsPage() {
  const [services, setServices] = useState([]);
  const [therapists, setTherapists] = useState([]);

  const [selectedServiceId, setSelectedServiceId] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(searchInput.trim());
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  useEffect(() => {
    let ignore = false;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const [servicesData, therapistsData] = await Promise.all([
          api.services(),
          api.therapists({
            serviceId: selectedServiceId || undefined,
            q: searchQuery || undefined,
          }),
        ]);

        if (!ignore) {
          setServices(servicesData);
          setTherapists(therapistsData);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message || "Nie udało się pobrać terapeutów.");
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
  }, [selectedServiceId, searchQuery]);

  const selectedService = useMemo(
    () => services.find((item) => item.id === selectedServiceId),
    [services, selectedServiceId]
  );

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Zespół</p>
          <h1>Terapeuci i terapeutki</h1>
          <p className="muted">
            Wyszukaj specjalistę po usłudze, tytule lub opisie doświadczenia.
          </p>
        </div>
      </div>

      <section className="panel">
        <div className="filter-bar">
          <label className="inline-label compact">
            Usługa
            <select
              value={selectedServiceId}
              onChange={(event) => setSelectedServiceId(event.target.value)}
            >
              <option value="">Wszystkie</option>
              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </select>
          </label>

          <label className="inline-label compact">
            Szukaj
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="np. stres, psycholog, młodzież"
            />
          </label>
        </div>

        {selectedService ? (
          <p className="muted">
            Aktywny filtr: <strong>{selectedService.name}</strong>
          </p>
        ) : null}
      </section>

      {!therapists.length ? (
        <EmptyState message="Brak terapeutów spełniających wybrane kryteria." />
      ) : (
        <div className="card-grid">
          {therapists.map((therapist) => (
            <article className="panel therapist-card" key={therapist.id}>
              <div className="avatar large">{therapist.fullName?.slice(0, 1) || "T"}</div>

              <h2>{therapist.fullName}</h2>
              <p className="muted">{therapist.title}</p>
              <p>{therapist.bio}</p>

              <div className="card-meta">
                <span>★ {therapist.averageRating || "0.0"}</span>
                <span>{therapist.experienceYears || 0} lat doświadczenia</span>
              </div>

              <Link className="btn btn-primary" to={`/therapists/${therapist.id}`}>
                Zobacz profil i terminy
              </Link>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}