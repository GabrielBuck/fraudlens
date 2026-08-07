import {
  BellRing,
  Building2,
  CircleDollarSign,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";
import { AlertTable } from "@/components/alert-table";
import {
  PaymentChart,
  SeverityChart,
  TimelineChart,
} from "@/components/overview-charts";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/ui";
import { apiGet, getOverview } from "@/lib/api";
import { currency, number, percent } from "@/lib/format";

export default async function OverviewPage() {
  const [overview, timeseries, severity, methods, reasons] = await Promise.all([
    getOverview(),
    apiGet<Array<{ date: string; volume: number; alerts: number }>>(
      "/api/v1/overview/timeseries",
    ),
    apiGet<Array<{ severity: string; count: number }>>(
      "/api/v1/overview/severity",
    ),
    apiGet<Array<{ method: string; alerts: number }>>(
      "/api/v1/overview/payment-methods",
    ),
    apiGet<Array<{ reason_code: string; count: number }>>(
      "/api/v1/overview/reason-codes",
    ),
  ]);
  const { kpis } = overview;
  return (
    <div className="page">
      <PageHeader
        eyebrow="RADAR OPERACIONAL"
        title="Visão geral de risco"
        description="Uma leitura executiva do volume monitorado e dos sinais que merecem investigação."
        actions={
          <>
            <button className="filter-button">Últimos 90 dias</button>
            <span className="freshness">
              <i /> Atualizado agora
            </span>
          </>
        }
      />
      <section className="metric-grid" aria-label="Indicadores principais">
        <MetricCard
          label="Volume monitorado"
          value={currency(kpis.monitored_volume)}
          change={kpis.volume_change}
          context={`${number(kpis.transactions)} pagamentos sintéticos`}
          icon={<CircleDollarSign />}
        />
        <MetricCard
          label="Alertas abertos"
          value={number(kpis.alerts)}
          context={`${percent(kpis.alert_rate)} do volume transacional`}
          icon={<BellRing />}
        />
        <MetricCard
          label="Alta prioridade"
          value={number(kpis.high_critical_alerts)}
          context={`${number(kpis.critical_alerts)} classificados como críticos`}
          icon={<ShieldAlert />}
        />
        <MetricCard
          label="Contas monitoradas"
          value={number(kpis.accounts)}
          context="Perfis empresariais fictícios"
          icon={<Building2 />}
        />
      </section>
      <section className="dashboard-grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">EVOLUÇÃO</span>
              <h2>Volume e alertas ao longo do tempo</h2>
            </div>
            <span className="legend-line cyan">Volume</span>
            <span className="legend-line orange">Alertas</span>
          </div>
          <TimelineChart data={timeseries} />
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">PRIORIDADE</span>
              <h2>Severidade</h2>
            </div>
          </div>
          <SeverityChart data={severity} />
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">CANAIS</span>
              <h2>Anomalias por meio</h2>
            </div>
          </div>
          <PaymentChart data={methods} />
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">EXPLICABILIDADE</span>
              <h2>Principais motivos</h2>
            </div>
          </div>
          <ol className="reason-list">
            {reasons.slice(0, 5).map((reason, index) => (
              <li key={reason.reason_code}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <strong>{reason.reason_code.replaceAll("_", " ")}</strong>
                  <small>{reason.count} alertas relacionados</small>
                </div>
                <em
                  style={{
                    width: `${Math.max(8, (reason.count / (reasons[0]?.count || 1)) * 100)}%`,
                  }}
                />
              </li>
            ))}
          </ol>
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">FILA DE ANÁLISE</span>
              <h2>Alertas recentes</h2>
            </div>
            <Link href="/alerts" className="text-link">
              Ver central completa →
            </Link>
          </div>
          <AlertTable alerts={overview.recent_alerts} compact />
        </article>
      </section>
    </div>
  );
}
