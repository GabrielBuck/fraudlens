import {
  Activity,
  CheckCircle2,
  DatabaseZap,
  Gauge,
  ScanSearch,
} from "lucide-react";
import { ScoreHistogram } from "@/components/overview-charts";
import { PageHeader } from "@/components/page-header";
import { MetricCard } from "@/components/ui";
import { apiGet } from "@/lib/api";
import { dateTime, number, percent } from "@/lib/format";

interface ModelRun {
  id: string;
  model_name: string;
  model_version: string;
  started_at: string;
  training_rows: number;
  scored_rows: number;
  feature_list: string[];
  parameters: Record<string, unknown>;
  metrics: {
    precision: number;
    recall: number;
    f1: number;
    precision_at_k: number;
    recall_at_k: number;
    pr_auc: number;
    confusion_matrix: number[][];
    scenario_recall: Record<string, number>;
    alert_rate: number;
    false_positive_rate: number;
    score_distribution: Array<{ bucket: string; count: number }>;
  };
}
interface Monitoring {
  drift: string;
  indicators: Array<{ name: string; value: number; status: string }>;
  disclaimer: string;
}

export default async function ModelPage() {
  const [run, monitoring] = await Promise.all([
    apiGet<ModelRun>("/api/v1/model-runs/latest"),
    apiGet<Monitoring>("/api/v1/model-monitoring"),
  ]);
  const metrics = run.metrics;
  return (
    <div className="page">
      <PageHeader
        eyebrow="MONITORAMENTO DO MODELO"
        title={`${run.model_name} · v${run.model_version}`}
        description={`Treinado em ${dateTime(run.started_at)}. Métricas exclusivamente sobre cenários e rótulos sintéticos.`}
        actions={
          <span className={`drift-badge drift-${monitoring.drift}`}>
            {monitoring.drift}
          </span>
        }
      />
      <section className="metric-grid">
        <MetricCard
          label="Precision"
          value={percent(metrics.precision * 100)}
          context="Entre alertas gerados"
          icon={<ScanSearch />}
        />
        <MetricCard
          label="Recall"
          value={percent(metrics.recall * 100)}
          context="Cenários sintéticos detectados"
          icon={<Activity />}
        />
        <MetricCard
          label="F1 sintético"
          value={metrics.f1.toFixed(3)}
          context="Equilíbrio entre precision e recall"
          icon={<Gauge />}
        />
        <MetricCard
          label="Linhas pontuadas"
          value={number(run.scored_rows)}
          context={`${run.feature_list.length} features causais`}
          icon={<DatabaseZap />}
        />
      </section>
      <section className="dashboard-grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">DISTRIBUIÇÃO</span>
              <h2>Scores de risco</h2>
            </div>
          </div>
          <ScoreHistogram data={metrics.score_distribution ?? []} />
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">MATRIZ DE CONFUSÃO</span>
              <h2>Resultado por classe</h2>
            </div>
          </div>
          <div className="confusion-matrix">
            <span />
            <b>Previsto normal</b>
            <b>Previsto alerta</b>
            <b>Real normal</b>
            <strong>{metrics.confusion_matrix?.[0]?.[0] ?? 0}</strong>
            <strong>{metrics.confusion_matrix?.[0]?.[1] ?? 0}</strong>
            <b>Real cenário</b>
            <strong>{metrics.confusion_matrix?.[1]?.[0] ?? 0}</strong>
            <strong>{metrics.confusion_matrix?.[1]?.[1] ?? 0}</strong>
          </div>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">DRIFT</span>
              <h2>Sinais de mudança</h2>
            </div>
          </div>
          <div className="indicator-list">
            {monitoring.indicators.map((indicator) => (
              <div key={indicator.name}>
                <CheckCircle2 size={17} />
                <span>
                  {indicator.name}
                  <small>{indicator.status}</small>
                </span>
                <strong>{indicator.value}</strong>
              </div>
            ))}
          </div>
          <p className="disclaimer">{monitoring.disclaimer}</p>
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">COBERTURA DOS CENÁRIOS</span>
              <h2>Recall por comportamento injetado</h2>
            </div>
          </div>
          <div className="scenario-metrics">
            {Object.entries(metrics.scenario_recall ?? {}).map(
              ([scenario, value]) => (
                <div key={scenario}>
                  <span>{scenario.replaceAll("_", " ")}</span>
                  <em>
                    <i style={{ width: `${value * 100}%` }} />
                  </em>
                  <strong>{percent(value * 100)}</strong>
                </div>
              ),
            )}
          </div>
        </article>
      </section>
      <section className="model-note">
        <strong>Como interpretar</strong>
        <p>
          O score ordena prioridades de investigação; não é probabilidade de
          fraude. Os resultados demonstram metodologia em dados sintéticos e
          exigiriam calibração, validação temporal e governança adicionais em um
          ambiente real.
        </p>
      </section>
    </div>
  );
}
