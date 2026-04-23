import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Ładowanie...");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/health")
      .then((response) => response.json())
      .then((data) => setMessage(data.status))
      .catch((error) => {
        console.error("Błąd:", error);
        setMessage("Błąd połączenia z backendem");
      });
  }, []);

  return (
    <div>
      <h1>Frontend działa</h1>
      <p>Status backendu: {message}</p>
    </div>
  );
}

export default App;