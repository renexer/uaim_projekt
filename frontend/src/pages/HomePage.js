import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <section className="hero">
      <div className="hero-text">
        <p className="eyebrow">Gabinet psychologiczno-terapeutyczny</p>
        <h1>Spokojna Przystań — konsultacje i terapia w jednym systemie rezerwacji</h1>
        <p>
          Aplikacja pozwala pacjentom przeglądać katalog usług, sprawdzać terapeutów,
          wybierać dostępne terminy oraz zarządzać wizytami. Terapeuci mają osobny panel
          do obsługi grafiku i podsumowań konsultacji.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/register">Załóż konto pacjenta</Link>
          <Link className="btn btn-outline" to="/login">Zaloguj się</Link>
          <Link className="btn btn-light" to="/services">Zobacz usługi</Link>
        </div>
      </div>
      <div className="hero-card" aria-label="Najważniejsze funkcje">
        <h2>Co możesz zrobić?</h2>
        <ul className="feature-list">
          <li>Wybrać usługę i terapeutę.</li>
          <li>Sprawdzić dostępne sloty w kalendarzu.</li>
          <li>Zarezerwować albo anulować wizytę.</li>
          <li>Przeglądać historię konsultacji i opinie.</li>
        </ul>
      </div>
    </section>
  );
}
