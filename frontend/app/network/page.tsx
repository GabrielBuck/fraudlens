import { PageHeader } from "@/components/page-header";
import { NetworkGraph } from "@/components/network-graph";
import { apiGet } from "@/lib/api";

interface AccountList {
  items: Array<{ id: string }>;
  total: number;
}
interface NetworkData {
  nodes: Array<{ id: string; label: string; type: string; risk: number }>;
  edges: Array<{ id: string; source: string; target: string; amount: number }>;
  limited_to: number;
}

export default async function NetworkPage({
  searchParams,
}: {
  searchParams: Promise<{ account?: string }>;
}) {
  const search = await searchParams;
  const accounts = await apiGet<AccountList>("/api/v1/accounts?page_size=20");
  const selected = search.account ?? accounts.items[0]?.id;
  const network = selected
    ? await apiGet<NetworkData>(`/api/v1/accounts/${selected}/network?limit=28`)
    : { nodes: [], edges: [], limited_to: 0 };
  return (
    <div className="page">
      <PageHeader
        eyebrow="GRAFO DE RELACIONAMENTOS"
        title="Conexões sob investigação"
        description="Explore contrapartes e dispositivos ligados à conta, com destaque visual para relações de maior risco."
      />
      <form className="filters compact-filters">
        <label>
          <span>Conta central</span>
          <select name="account" defaultValue={selected}>
            {accounts.items.map((account) => (
              <option key={account.id}>{account.id}</option>
            ))}
          </select>
        </label>
        <button className="button" type="submit">
          Carregar rede
        </button>
        <span className="network-legend">
          <i className="legend-account" />
          Conta <i className="legend-counterparty" />
          Contraparte <i className="legend-device" />
          Dispositivo <i className="legend-risk" />
          Maior risco
        </span>
      </form>
      <section className="panel network-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">REDE LIMITADA</span>
            <h2>{selected ?? "Nenhuma conta disponível"}</h2>
          </div>
          <small>Até {network.limited_to} transações recentes</small>
        </div>
        {network.nodes.length ? (
          <NetworkGraph nodes={network.nodes} edges={network.edges} />
        ) : (
          <div className="empty-state">
            <strong>Sem relações para exibir</strong>
            <p>Execute o pipeline para popular o grafo.</p>
          </div>
        )}
      </section>
    </div>
  );
}
