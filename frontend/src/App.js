import { useEffect, useState } from "react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "/api/v1";

function App() {
  const [message, setMessage] = useState("Ładowanie...");

  useEffect(() => {
    // Healthcheck używa aktywnej wersji API backendu. W Dockerze NGINX proxy
    // przekazuje ścieżkę /api do kontenera Flask, a lokalnie można ustawić
    // REACT_APP_API_URL=http://localhost:5000/api/v1.
    fetch(`${API_URL}/health`)
      .then((response) => response.json())
      .then((payload) => setMessage(payload?.data?.status || "brak statusu"))
      .catch((error) => {
        console.error("Błąd:", error);
        setMessage("Błąd połączenia z backendem");
      });
  }, []);

  return (
    <main className="app-shell">
      <section className="status-card">
        <p className="eyebrow">UAIM · gabinet psychologiczno-terapeutyczny</p>
        <h1>Frontend działa</h1>
        <p>Status backendu: <strong>{message}</strong></p>
        <p className="hint">Aktywny endpoint: {API_URL}/health</p>
      </section>
    </main>
  );
}

export default App;
