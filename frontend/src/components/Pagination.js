export default function Pagination({ meta, onPageChange }) {
  if (!meta || !meta.total || meta.total <= meta.pageSize) {
    return null;
  }

  const totalPages = Math.max(1, Math.ceil(meta.total / meta.pageSize));

  return (
    <div className="pagination">
      <button
        className="btn btn-light"
        type="button"
        onClick={() => onPageChange(meta.page - 1)}
        disabled={meta.page <= 1}
      >
        Poprzednia
      </button>

      <span className="pagination-info">
        Strona <strong>{meta.page}</strong> z <strong>{totalPages}</strong>
      </span>

      <button
        className="btn btn-light"
        type="button"
        onClick={() => onPageChange(meta.page + 1)}
        disabled={meta.page >= totalPages}
      >
        Następna
      </button>
    </div>
  );
}