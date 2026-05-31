import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import LoadingState, { EmptyState, ErrorState } from "../components/StateBlocks";
import { formatMoney } from "./pageUtils";

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadServices = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setServices(await api.services());
    } catch (err) {
      setError(err.message || "Nie udało się pobrać usług.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadServices();
  }, [loadServices]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadServices} />;

  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Katalog</p>
          <h1>Usługi gabinetu</h1>
        </div>
        <Link className="btn btn-primary" to="/booking">Umów wizytę</Link>
      </div>
      {!services.length ? <EmptyState message="Brak aktywnych usług." /> : (
        <div className="card-grid">
          {services.map((service) => (
            <article className="card" key={service.id}>
              <h2>{service.name}</h2>
              <p>{service.description}</p>
              <dl className="meta-list">
                <div><dt>Czas</dt><dd>{service.durationMinutes} min</dd></div>
                <div><dt>Cena</dt><dd>{formatMoney(service.basePrice, service.currency)}</dd></div>
              </dl>
              <div className="card-actions">
                <Link className="btn btn-outline" to={`/services/${service.id}/therapists`}>Terapeuci</Link>
                <Link className="btn btn-primary" to={`/booking?serviceId=${service.id}`}>Rezerwuj</Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
