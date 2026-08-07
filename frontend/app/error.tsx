"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <div className="page">
      <section className="empty-state">
        <strong>Não foi possível carregar os dados</strong>
        <p>Verifique se a API está disponível e tente novamente.</p>
        <button onClick={reset}>Tentar novamente</button>
      </section>
    </div>
  );
}
