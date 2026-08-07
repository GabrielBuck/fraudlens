import {
  ArrowLeft,
  BellRing,
  CalendarDays,
  CreditCard,
  Landmark,
  WalletCards,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/ui";
import { apiGet } from "@/lib/api";
import { currency, dateTime, number } from "@/lib/format";
import type { Transaction } from "@/lib/types";

interface Account {
  id: string;
  customer_segment: string;
  home_city: string;
  home_state: string;
  account_age_days: number;
  average_monthly_volume: number;
  risk_profile: string;
  transaction_count: number;
  alert_count: number;
}
interface Behavior {
  average_amount: number;
  median_amount: number;
  p95_amount: number;
  payment_methods: Array<{ method: string; count: number }>;
  common_hours: Array<{ hour: number; count: number }>;
  usual_window: [number, number];
}

export default async function AccountPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [account, behavior, timeline] = await Promise.all([
    apiGet<Account>(`/api/v1/accounts/${id}`),
    apiGet<Behavior>(`/api/v1/accounts/${id}/behavior`),
    apiGet<Array<Transaction & { alert: Record<string, unknown> | null }>>(
      `/api/v1/accounts/${id}/timeline?limit=30`,
    ),
  ]);
  const maxMethod = Math.max(
    ...behavior.payment_methods.map((item) => item.count),
    1,
  );
  return (
    <div className="page">
      <Link href="/alerts" className="back-link">
        <ArrowLeft size={16} /> Voltar aos alertas
      </Link>
      <PageHeader
        eyebrow="INVESTIGAÇÃO DE CONTA"
        title={account.id}
        description={`${account.customer_segment} · ${account.home_city}, ${account.home_state} · perfil sintético de risco ${account.risk_profile}`}
      />
      <section className="metric-grid">
        <MetricCard
          label="Volume mensal esperado"
          value={currency(account.average_monthly_volume)}
          context="Referência sintética do perfil"
          icon={<Landmark />}
        />
        <MetricCard
          label="Transações observadas"
          value={number(account.transaction_count)}
          context="Janela de demonstração"
          icon={<WalletCards />}
        />
        <MetricCard
          label="Alertas anteriores"
          value={number(account.alert_count)}
          context="Eventos acima do limiar"
          icon={<BellRing />}
        />
        <MetricCard
          label="Idade da conta"
          value={`${account.account_age_days} dias`}
          context="Histórico simulado"
          icon={<CalendarDays />}
        />
      </section>
      <section className="detail-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">COMPORTAMENTO</span>
              <h2>Perfil de valores</h2>
            </div>
          </div>
          <dl className="stat-list">
            <div>
              <dt>Média</dt>
              <dd>{currency(behavior.average_amount)}</dd>
            </div>
            <div>
              <dt>Mediana</dt>
              <dd>{currency(behavior.median_amount)}</dd>
            </div>
            <div>
              <dt>Percentil 95</dt>
              <dd>{currency(behavior.p95_amount)}</dd>
            </div>
            <div>
              <dt>Horário habitual</dt>
              <dd>
                {behavior.usual_window[0]}h–{behavior.usual_window[1]}h
              </dd>
            </div>
          </dl>
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">PREFERÊNCIAS</span>
              <h2>Meios de pagamento recorrentes</h2>
            </div>
          </div>
          <div className="method-bars">
            {behavior.payment_methods.map((item) => (
              <div key={item.method}>
                <span>
                  <CreditCard size={16} />
                  {item.method}
                  <strong>{item.count}</strong>
                </span>
                <em>
                  <i style={{ width: `${(item.count / maxMethod) * 100}%` }} />
                </em>
              </div>
            ))}
          </div>
        </article>
      </section>
      <section className="panel timeline-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">HISTÓRICO</span>
            <h2>Linha do tempo transacional</h2>
          </div>
          <Link className="text-link" href={`/network?account=${id}`}>
            Abrir grafo →
          </Link>
        </div>
        <div className="timeline">
          {timeline.map((item) => (
            <div
              key={item.id}
              className={item.alert ? "timeline-item active" : "timeline-item"}
            >
              <i />
              <time>{dateTime(item.timestamp)}</time>
              <strong>{currency(item.amount)}</strong>
              <span>
                {item.payment_method} · {item.counterparty_id}
              </span>
              {Boolean(item.alert) && <b>Alerta</b>}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
