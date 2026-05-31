import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { loadAllTherapists } from "./pageUtils";

export default function TherapistsPage() {
  const { serviceId } = useParams();
  const [therapists, setTherapists] = useState([]);
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadTherapists = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      if (serviceId) {
        const [serviceData, therapistsData] = await Promise.all([
          api.service(serviceId),
          api.therapistsForService(serviceId),
        ]);
        setService(serviceData);
        setTherapists(therapistsData.map((therapist) => ({ ...therapist, services: [{ id: serviceId, name: serviceData.name }] })));
      } else {
        setService(null);
        setTherapists(await loadAllTherapists(api));
      }
    } catch (err) {
      setError(err.message || "Nie udało się pobrać terapeutów.");
    } finally {
      setLoading(false);
    }
  }, [serviceId]);

  useEffect(() => {
    loadTherapists();
  }, [loadTherapists]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadTherapists} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Specjaliści</p>
          <h1>{service ? `Terapeuci: ${service.name}` : "Lista terapeutów"}</h1>
        </div>
        <Link className="btn btn-light" to="/services">Powrót do usług</Link>
      </div>
      {!therapists.length ? <EmptyState message="Brak terapeutów dla wybranych kryteriów." /> : (
        <div className="card-grid">
          {therapists.map((therapist) => {
            const primaryService = therapist.services?.[0];
            return (
              <article className="card therapist-card" key={therapist.id}>
                <div className="avatar">{therapist.fullName?.slice(0, 1) || "T"}</div>
                <div>
                  <h2>{therapist.fullName}</h2>
                  <p className="muted">{therapist.title} · {therapist.experienceYears || 0} lat doświadczenia</p>
                  <p>{therapist.bio}</p>
                  <p className="rating">★ {therapist.averageRating || "0.0"} / 5 ({therapist.reviewsCount || 0} opinii)</p>
                  <p className="muted">Usługi: {therapist.services?.map((item) => item.name).join(", ")}</p>
                  <div className="card-actions">
                    <Link className="btn btn-outline" to={`/therapists/${therapist.id}${primaryService ? `?serviceId=${primaryService.id}` : ""}`}>Szczegóły</Link>
                    {primaryService && <Link className="btn btn-primary" to={`/booking?serviceId=${primaryService.id}&therapistId=${therapist.id}`}>Wybierz termin</Link>}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
