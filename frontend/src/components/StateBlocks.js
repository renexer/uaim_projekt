export default function LoadingState({ message = "Ładowanie danych..." }) {
  return <div className="state state-loading" role="status">{message}</div>;
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state state-error" role="alert">
      <p>{message || "Wystąpił błąd."}</p>
      {onRetry && <button className="btn btn-outline" onClick={onRetry}>Spróbuj ponownie</button>}
    </div>
  );
}

export function EmptyState({ message }) {
  return <div className="state state-empty">{message}</div>;
}
