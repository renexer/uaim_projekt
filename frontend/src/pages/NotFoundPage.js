import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <section className="panel narrow">
      <h1>Nie znaleziono strony</h1>
      <p>Podany adres nie pasuje do żadnego widoku aplikacji.</p>
      <Link className="btn btn-primary" to="/">Wróć na stronę startową</Link>
    </section>
  );
}
