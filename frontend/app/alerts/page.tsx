import Link from "next/link";
import { AlertTable } from "@/components/alert-table";
import { PageHeader } from "@/components/page-header";
import { apiGet } from "@/lib/api";
import type { Alert } from "@/lib/types";

type Search = {
  severity?: string;
  status?: string;
  search?: string;
  page?: string;
};

export default async function AlertsPage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const search = await searchParams;
  const params = new URLSearchParams();
  Object.entries(search).forEach(
    ([key, value]) => value && params.set(key, value),
  );
  const data = await apiGet<{
    items: Alert[];
    total: number;
    page: number;
    pages: number;
  }>(`/api/v1/alerts?${params}`);
  return (
    <div className="page">
      <PageHeader
        eyebrow="CENTRAL DE ALERTAS"
        title="Prioridades para investigação"
        description="Filtre, compare e aprofunde os eventos sinalizados pelo radar combinado."
        actions={
          <span className="result-count">{data.total} alertas encontrados</span>
        }
      />
      <form className="filters" aria-label="Filtros de alertas">
        <label>
          <span>Buscar</span>
          <input
            name="search"
            defaultValue={search.search}
            placeholder="Alerta, conta ou transação"
          />
        </label>
        <label>
          <span>Severidade</span>
          <select name="severity" defaultValue={search.severity ?? ""}>
            <option value="">Todas</option>
            <option value="crítica">Crítica</option>
            <option value="alta">Alta</option>
            <option value="média">Média</option>
            <option value="baixa">Baixa</option>
          </select>
        </label>
        <label>
          <span>Status</span>
          <select name="status" defaultValue={search.status ?? ""}>
            <option value="">Todos</option>
            <option value="novo">Novo</option>
            <option value="em análise">Em análise</option>
            <option value="fraude confirmada">Fraude confirmada</option>
            <option value="falso positivo">Falso positivo</option>
            <option value="encerrado">Encerrado</option>
          </select>
        </label>
        <button className="button" type="submit">
          Aplicar filtros
        </button>
        {(search.search || search.severity || search.status) && (
          <Link className="text-button" href="/alerts">
            Limpar
          </Link>
        )}
      </form>
      <section className="panel alerts-panel">
        <AlertTable alerts={data.items} />
      </section>
      {data.pages > 1 && (
        <nav className="pagination" aria-label="Paginação">
          <Link
            aria-disabled={data.page <= 1}
            href={`/alerts?${new URLSearchParams({ ...search, page: String(Math.max(1, data.page - 1)) })}`}
          >
            ← Anterior
          </Link>
          <span>
            Página {data.page} de {data.pages}
          </span>
          <Link
            aria-disabled={data.page >= data.pages}
            href={`/alerts?${new URLSearchParams({ ...search, page: String(Math.min(data.pages, data.page + 1)) })}`}
          >
            Próxima →
          </Link>
        </nav>
      )}
    </div>
  );
}
