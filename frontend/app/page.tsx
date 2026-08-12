import {
  ArrowRight,
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
import { apiGet, getOverview } from "@/lib/api";
import { currency, dateTime, number, parseDate, percent } from "@/lib/format";

type Search = { range?: string };

export default async function OverviewPage({
  searchParams,
}: {
  searchParams: Promise<Search>;
}) {
  const search = await searchParams;
  const range = ["30", "60", "90"].includes(search.range ?? "")
    ? search.range!
    : "90";
  const initial = await getOverview();
  const end = initial.period_end ? parseDate(initial.period_end) : null;
  const start = end
    ? new Date(end.getTime() - Number(range) * 86_400_000)
    : null;
  const query =
    start && end
      ? `?start_at=${encodeURIComponent(start.toISOString())}&end_at=${encodeURIComponent(end.toISOString())}`
      : "";
  const overview = query
    ? await apiGet<Awaited<ReturnType<typeof getOverview>>>(
        `/api/v1/overview${query}`,
      )
    : initial;
  const [timeseries, severity, methods, reasons] = await Promise.all([
    apiGet<Array<{ date: string; volume: number; alerts: number }>>(
      `/api/v1/overview/timeseries${query}`,
    ),
    apiGet<Array<{ severity: string; count: number }>>(
      `/api/v1/overview/severity${query}`,
    ),
    apiGet<Array<{ method: string; alerts: number }>>(
      `/api/v1/overview/payment-methods${query}`,
    ),
    apiGet<Array<{ reason_code: string; count: number }>>(
      `/api/v1/overview/reason-codes${query}`,
    ),
  ]);
  const { kpis } = overview;
  return (
    <div className="page overview-page">
      <PageHeader
        eyebrow="RISK OPERATIONS"
        title="Operações de risco"
        description="Atividade monitorada, pressão de alertas e fila de investigação sobre dados sintéticos."
        actions={
          <form className="range-control">
            <label htmlFor="range">Período</label>
            <select id="range" name="range" defaultValue={range}>
              <option value="30">30 dias</option>
              <option value="60">60 dias</option>
              <option value="90">90 dias</option>
            </select>
            <button type="submit">Atualizar</button>
          </form>
        }
      />
      <section className="overview-ledger" aria-label="Indicadores principais">
        <div className="ledger-primary">
          <span>VOLUME MONITORADO</span>
          <strong>{currency(kpis.monitored_volume)}</strong>
          <small>{number(kpis.transactions)} pagamentos no período</small>
        </div>
        <dl>
          <div>
            <dt>Alertas</dt>
            <dd>{number(kpis.alerts)}</dd>
            <small>{percent(kpis.alert_rate)} das operações</small>
          </div>
          <div>
            <dt>Alta / crítica</dt>
            <dd>{number(kpis.high_critical_alerts)}</dd>
            <small>{number(kpis.critical_alerts)} críticos</small>
          </div>
          <div>
            <dt>Contas</dt>
            <dd>{number(kpis.accounts)}</dd>
            <small>perfis sintéticos</small>
          </div>
          <div>
            <dt>Variação de volume</dt>
            <dd>
              {kpis.volume_change == null
                ? "—"
                : `${kpis.volume_change > 0 ? "+" : ""}${percent(kpis.volume_change)}`}
            </dd>
            <small>
              {kpis.comparison_available
                ? "janela anterior equivalente"
                : "sem janela anterior completa"}
            </small>
          </div>
        </dl>
      </section>
      <div className="freshness-line">
        <span>
          PERÍODO{" "}
          {overview.period_start ? dateTime(overview.period_start) : "—"} →{" "}
          {overview.period_end ? dateTime(overview.period_end) : "—"}
        </span>
        <span>
          SCORING {overview.updated_at ? dateTime(overview.updated_at) : "—"}
        </span>
      </div>
      <section className="operations-grid">
        <article className="panel activity-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">TRANSACTION ACTIVITY</span>
              <h2>Volume e alertas</h2>
            </div>
          </div>
          <TimelineChart data={timeseries} />
        </article>
        <article className="panel pressure-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">ALERT PRESSURE</span>
              <h2>Prioridade</h2>
            </div>
          </div>
          <SeverityChart data={severity} />
        </article>
        <article className="panel signal-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">TOP SIGNALS</span>
              <h2>Motivos recorrentes</h2>
            </div>
          </div>
          <ol className="reason-list">
            {reasons.slice(0, 6).map((reason, index) => (
              <li key={reason.reason_code}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <strong>{reason.reason_code.replaceAll("_", " ")}</strong>
                  <small>{reason.count} alertas</small>
                </div>
                <em
                  style={{
                    width: `${Math.max(6, (reason.count / (reasons[0]?.count || 1)) * 100)}%`,
                  }}
                />
              </li>
            ))}
          </ol>
        </article>
        <article className="panel channel-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">PAYMENT RAILS</span>
              <h2>Alertas por meio</h2>
            </div>
          </div>
          <PaymentChart data={methods} />
        </article>
        <article className="panel queue-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">INVESTIGATION QUEUE</span>
              <h2>Casos prioritários</h2>
            </div>
            <Link href="/alerts" className="text-link">
              Abrir fila <ArrowRight size={15} />
            </Link>
          </div>
          <AlertTable alerts={overview.recent_alerts} compact />
        </article>
      </section>
      <section className="overview-links">
        <Link href="/accounts">
          <Building2 />
          Perfis de conta
        </Link>
        <Link href="/model">
          <ShieldAlert />
          Modelo e dados
        </Link>
        <span>
          <CircleDollarSign />
          Scores ordenam investigação; não representam probabilidade.
        </span>
      </section>
    </div>
  );
}
