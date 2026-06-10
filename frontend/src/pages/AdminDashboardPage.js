import { Link } from "react-router-dom";

export default function AdminDashboardPage() {
  return (
    <section className="page-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Administrator</p>
          <h1>Panel administracyjny</h1>
        </div>
      </div>

      <div className="card-grid">
        <Link className="panel card-link" to="/admin/services">
          <h2>Usługi</h2>
          <p>Dodawanie i edycja katalogu usług.</p>
        </Link>

        <Link className="panel card-link" to="/admin/therapists">
          <h2>Terapeuci</h2>
          <p>Tworzenie profili terapeutów i przypisywanie usług.</p>
        </Link>

        <Link className="panel card-link" to="/admin/availability">
          <h2>Grafiki</h2>
          <p>Zarządzanie regułami dostępności i wyjątkami.</p>
        </Link>
      </div>
    </section>
  );
}