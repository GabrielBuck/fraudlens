export default function Loading() {
  return (
    <div className="page">
      <div className="skeleton hero-skeleton" />
      <div className="metric-grid">
        {Array.from({ length: 4 }).map((_, index) => (
          <div className="skeleton card-skeleton" key={index} />
        ))}
      </div>
    </div>
  );
}
