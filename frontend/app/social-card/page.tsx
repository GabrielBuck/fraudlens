import { BrainCircuit, Database, Radar, ShieldAlert } from "lucide-react";

import { getOverview } from "@/lib/api";
import { currency, number, percent } from "@/lib/format";

export default async function SocialCardPage() {
  const { kpis, recent_alerts: alerts } = await getOverview();
  const alert = alerts[0];
  return (
    <div className="social-card" style={{ zIndex: 99 }}>
      <header>
        <div className="social-brand">
          <span>
            <Radar />
          </span>
          <div>
            <strong>FraudLens</strong>
            <small>INTELLIGENT PAYMENT ANOMALY RADAR</small>
          </div>
        </div>
        <b>100% DADOS SINTÉTICOS</b>
      </header>
      <section>
        <div className="social-copy">
          <span className="eyebrow">PAYMENT ANOMALY INVESTIGATION</span>
          <h1>
            Do pagamento ao sinal.
            <br />
            <em>Do sinal à explicação.</em>
          </h1>
          <p>
            Dados sintéticos, features causais, regras explicáveis, ML não
            supervisionado e revisão humana.
          </p>
          <div className="social-kpis">
            <div>
              <span>Volume monitorado</span>
              <strong>{currency(kpis.monitored_volume)}</strong>
            </div>
            <div>
              <span>Transações</span>
              <strong>{number(kpis.transactions)}</strong>
            </div>
            <div>
              <span>Taxa de alertas</span>
              <strong>{percent(kpis.alert_rate)}</strong>
            </div>
          </div>
        </div>
        <div className="social-radar">
          <i className="sweep" />
          <span className="radar-dot dot-one" />
          <span className="radar-dot dot-two" />
          <span className="radar-dot dot-three" />
          <div className="social-alert">
            <ShieldAlert />
            <div>
              <small>ALERTA EM DESTAQUE</small>
              <strong>
                {alert
                  ? `${alert.risk_score.toFixed(0)}/100 · ${alert.severity}`
                  : "Radar inicializando"}
              </strong>
              <span>
                {alert?.reason_codes[0]?.replaceAll("_", " ") ??
                  "Análise multivariada"}
              </span>
            </div>
          </div>
        </div>
      </section>
      <footer>
        <span>
          <Database /> FastAPI + SQLAlchemy
        </span>
        <span>
          <BrainCircuit /> Isolation Forest + regras
        </span>
        <span>Next.js + TypeScript</span>
        <strong>Prioriza investigação. Não condenação.</strong>
      </footer>
    </div>
  );
}
