import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { Score } from "@/components/ui";
import { apiGet } from "@/lib/api";
import { currency, dateTime, number } from "@/lib/format";
import type { Account, Paginated } from "@/lib/types";

type Search = { search?: string; segment?: string; page?: string };

export default async function AccountsPage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const search = await searchParams;
  const params = new URLSearchParams();
  Object.entries(search).forEach(
    ([key, value]) => value && params.set(key, value),
  );
  const data = await apiGet<Paginated<Account>>(`/api/v1/accounts?${params}`);
  return (
    <div className="page">
      <PageHeader
        eyebrow="BEHAVIORAL PROFILES"
        title="Contas monitoradas"
        description="Volume, atividade e maior prioridade observada por perfil sintético."
        actions={
          <span className="result-count">{number(data.total)} contas</span>
        }
      />
      <form className="filters" aria-label="Filtros de contas">
        <label>
          <span>Buscar conta ou cidade</span>
          <input
            name="search"
            defaultValue={search.search}
            placeholder="ACC-000001"
          />
        </label>
        <label>
          <span>Segmento</span>
          <select name="segment" defaultValue={search.segment ?? ""}>
            <option value="">Todos</option>
            <option>Micro</option>
            <option>Pequena empresa</option>
            <option>Média empresa</option>
            <option>Grande empresa</option>
          </select>
        </label>
        <button className="button" type="submit">
          Aplicar filtros
        </button>
        {(search.search || search.segment) && (
          <Link className="text-button" href="/accounts">
            Limpar
          </Link>
        )}
      </form>
      <section className="panel accounts-table-panel">
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Contas sintéticas monitoradas</caption>
            <thead>
              <tr>
                <th>Conta</th>
                <th>Perfil</th>
                <th>Atividade</th>
                <th>Volume observado</th>
                <th>Alertas</th>
                <th>Maior prioridade</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((account) => (
                <tr key={account.id}>
                  <td>
                    <Link className="id-link" href={`/accounts/${account.id}`}>
                      {account.id}
                    </Link>
                    <small>
                      {account.home_city} · {account.home_state}
                    </small>
                  </td>
                  <td>
                    {account.customer_segment}
                    <small>Risco base {account.risk_profile}</small>
                  </td>
                  <td>
                    {number(account.transaction_count)} operações
                    <small>
                      {account.last_activity
                        ? dateTime(account.last_activity)
                        : "Sem atividade"}
                    </small>
                  </td>
                  <td className="numeric">
                    {currency(account.transaction_volume)}
                  </td>
                  <td className="numeric">{number(account.alert_count)}</td>
                  <td>
                    <Score value={account.highest_priority} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
