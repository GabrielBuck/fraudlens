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
  min_score?: string;
  reason_code?: string;
  payment_method?: string;
  start_at?: string;
  end_at?: string;
  sort?: string;
};

export default async function AlertsPage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const search = await searchParams;
  const params = new URLSearchParams();
  Object.entries(search).forEach(([key, value]) => {
    if (!value) return;
    if (key === "start_at") params.set(key, `${value}T00:00:00Z`);
    else if (key === "end_at") params.set(key, `${value}T23:59:59Z`);
    else params.set(key, value);
  });
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
          <span>Score mínimo</span>
          <input
            name="min_score"
            type="number"
            min="0"
            max="100"
            defaultValue={search.min_score}
            placeholder="30"
          />
        </label>
        <label>
          <span>Meio</span>
          <select
            name="payment_method"
            defaultValue={search.payment_method ?? ""}
          >
            <option value="">Todos</option>
            <option>PIX</option>
            <option>TED</option>
            <option>boleto</option>
            <option>cartão</option>
            <option>transferência interna</option>
          </select>
        </label>
        <label>
          <span>Motivo</span>
          <input
            name="reason_code"
            defaultValue={search.reason_code}
            placeholder="NEW_DEVICE"
          />
        </label>
        <label>
          <span>De</span>
          <input name="start_at" type="date" defaultValue={search.start_at} />
        </label>
        <label>
          <span>Até</span>
          <input name="end_at" type="date" defaultValue={search.end_at} />
        </label>
        <label>
          <span>Ordenar</span>
          <select name="sort" defaultValue={search.sort ?? "risk_desc"}>
            <option value="risk_desc">Maior prioridade</option>
            <option value="risk_asc">Menor prioridade</option>
            <option value="newest">Mais recentes</option>
            <option value="oldest">Mais antigos</option>
          </select>
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
        {Object.values(search).some(Boolean) && (
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
