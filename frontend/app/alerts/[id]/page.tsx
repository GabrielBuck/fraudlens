import {
  AlertTriangle,
  ArrowLeft,
  Clock3,
  Fingerprint,
  MapPin,
  MonitorSmartphone,
  Route,
  Scale,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { ReviewActions } from "@/components/review-actions";
import { Score, SeverityBadge, StatusBadge } from "@/components/ui";
import { getAlert } from "@/lib/api";
import { currency, dateTime } from "@/lib/format";

export default async function AlertDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const alert = await getAlert(id);
  const tx = alert.transaction;
  return (
    <div className="page">
      <Link href="/alerts" className="back-link">
        <ArrowLeft size={16} /> Voltar à central
      </Link>
      <PageHeader
        eyebrow={`CASO ${alert.id}`}
        title="Prioridade de investigação"
        description="Case file com evidências rastreáveis, atividade próxima e histórico de revisão."
        actions={
          <div className="header-badges">
            <SeverityBadge severity={alert.severity} />
            <StatusBadge status={alert.status} />
          </div>
        }
      />
      <section className="alert-hero">
        <Score value={alert.risk_score} size="large" />
        <div className="alert-summary">
          <span className="eyebrow">RESUMO EXECUTIVO</span>
          <h2>{alert.explanation}</h2>
          <div className="inline-facts">
            <span>
              <Clock3 size={15} />
              {dateTime(tx.timestamp)}
            </span>
            <span>
              <Fingerprint size={15} />
              {tx.id}
            </span>
            <span>
              <MapPin size={15} />
              {tx.ip_city}
            </span>
          </div>
        </div>
        <div className="hero-amount">
          <span>Valor analisado</span>
          <strong>{currency(tx.amount)}</strong>
          <small>
            {tx.payment_method} · {tx.direction}
          </small>
        </div>
      </section>
      <section className="detail-grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">COMPOSIÇÃO DO RISCO</span>
              <h2>Decomposição da prioridade</h2>
            </div>
          </div>
          <div className="score-breakdown">
            <div>
              <span>Modelo de anomalia</span>
              <strong>{alert.model_score.toFixed(1)}</strong>
              <em>
                <i style={{ width: `${alert.model_score}%` }} />
              </em>
              <small>Peso de 55% na combinação</small>
            </div>
            <span className="plus">+</span>
            <div>
              <span>Motor de regras</span>
              <strong>{alert.rules_score.toFixed(1)}</strong>
              <em>
                <i style={{ width: `${alert.rules_score}%` }} />
              </em>
              <small>Peso de 45% na combinação</small>
            </div>
            <span className="equals">=</span>
            <div>
              <span>Booster contextual</span>
              <strong>+{alert.context_booster.toFixed(1)}</strong>
              <small>Combinações específicas de sinais</small>
            </div>
            <span className="equals">=</span>
            <div className="final-score">
              <span>Prioridade final</span>
              <strong>{alert.risk_score.toFixed(1)}</strong>
              <small>Escala de investigação</small>
            </div>
          </div>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">TRANSAÇÃO</span>
              <h2>Contexto do pagamento</h2>
            </div>
          </div>
          <dl className="detail-list">
            <div>
              <dt>Conta</dt>
              <dd>
                <Link href={`/accounts/${alert.account_id}`}>
                  {alert.account_id}
                </Link>
              </dd>
            </div>
            <div>
              <dt>Contraparte</dt>
              <dd>{tx.counterparty_id}</dd>
            </div>
            <div>
              <dt>Dispositivo</dt>
              <dd>{tx.device_id}</dd>
            </div>
            <div>
              <dt>Meio</dt>
              <dd>{tx.payment_method}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{tx.status}</dd>
            </div>
            <div>
              <dt>Aberto em</dt>
              <dd>{dateTime(alert.created_at)}</dd>
            </div>
          </dl>
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">EVIDÊNCIAS</span>
              <h2>Por que este evento foi sinalizado?</h2>
            </div>
          </div>
          <div className="evidence-list">
            {alert.evidence.length ? (
              alert.evidence.map((evidence) => (
                <article key={evidence.rule_id}>
                  <span className="evidence-icon">
                    <AlertTriangle size={18} />
                  </span>
                  <div>
                    <strong>{evidence.rule_name}</strong>
                    <p>{evidence.description}</p>
                    <small>
                      Observado: {evidence.observed_value} · esperado:{" "}
                      {evidence.expected_value}
                    </small>
                  </div>
                </article>
              ))
            ) : (
              <p>
                Nenhuma regra isolada foi acionada; o desvio veio do padrão
                multivariado.
              </p>
            )}
          </div>
        </article>
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">SINAIS CONTEXTUAIS</span>
              <h2>Pontos de atenção</h2>
            </div>
          </div>
          <div className="signal-grid">
            <span>
              <MonitorSmartphone />
              Dispositivo
              <br />
              <strong>{tx.device_id}</strong>
            </span>
            <span>
              <Route />
              Localização
              <br />
              <strong>{tx.ip_city}</strong>
            </span>
            <span>
              <Scale />
              Comparação
              <br />
              <strong>
                {alert.risk_score >= 60 ? "Fora do padrão" : "Desvio moderado"}
              </strong>
            </span>
          </div>
        </article>
      </section>
      {alert.nearby_transactions && (
        <section className="panel timeline-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">LINHA DO TEMPO</span>
              <h2>Eventos próximos</h2>
            </div>
          </div>
          <div className="timeline">
            {alert.nearby_transactions.map((item) => (
              <div
                key={item.id}
                className={
                  item.id === tx.id ? "timeline-item active" : "timeline-item"
                }
              >
                <i />
                <time>{dateTime(item.timestamp)}</time>
                <strong>{currency(item.amount)}</strong>
                <span>
                  {item.payment_method} · {item.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
      <section className="panel review-history">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">REVIEW HISTORY</span>
            <h2>Decisões registradas</h2>
          </div>
        </div>
        {alert.feedback?.length ? (
          <ol>
            {alert.feedback.map((item) => (
              <li key={item.id}>
                <time>{dateTime(item.created_at)}</time>
                <strong>{item.classification}</strong>
                <p>{item.comment}</p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted-copy">
            Nenhuma revisão registrada para este caso.
          </p>
        )}
      </section>
      <ReviewActions alertId={alert.id} initialStatus={alert.status} />
    </div>
  );
}
