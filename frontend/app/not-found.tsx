import Link from "next/link";

export default function NotFound() {
  return (
    <div className="page">
      <section className="empty-state">
        <strong>Página não encontrada</strong>
        <p>O recurso solicitado não existe ou foi removido.</p>
        <Link className="button" href="/">
          Voltar à visão geral
        </Link>
      </section>
    </div>
  );
}
