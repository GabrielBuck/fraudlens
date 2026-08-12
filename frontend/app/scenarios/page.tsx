import {
  AlarmClock,
  CopyCheck,
  Gauge,
  MapPinned,
  MoonStar,
  ShieldAlert,
  Split,
  UsersRound,
} from "lucide-react";
import { PageHeader } from "@/components/page-header";

const scenarios = [
  {
    title: "Possível tomada de conta",
    code: "account_takeover",
    icon: ShieldAlert,
    description:
      "Novo dispositivo, local incomum, falhas de acesso e PIX elevado para contraparte nova.",
    features: ["new_device", "failed_auth_30m", "distance_from_home_km"],
    rules: ["NEW_DEVICE", "FAILED_AUTH_BURST", "HIGH_AMOUNT_DEVIATION"],
  },
  {
    title: "Pico de velocidade transacional",
    code: "velocity_burst",
    icon: Gauge,
    description:
      "Múltiplas operações parecidas em poucos minutos para diferentes contrapartes.",
    features: ["tx_count_5m", "distinct_counterparties_24h"],
    rules: ["VELOCITY_5M", "VELOCITY_1H"],
  },
  {
    title: "Fracionamento",
    code: "split_payment",
    icon: Split,
    description:
      "Várias saídas menores cuja soma se torna relevante dentro de uma janela curta.",
    features: ["amount_sum_1h", "tx_count_1h"],
    rules: ["SPLIT_PAYMENT_PATTERN"],
  },
  {
    title: "Deslocamento incompatível",
    code: "impossible_travel",
    icon: MapPinned,
    description:
      "Eventos sucessivos em locais distantes, com tempo fisicamente incompatível.",
    features: ["estimated_speed_kmh", "new_country"],
    rules: ["IMPOSSIBLE_TRAVEL", "NEW_DEVICE"],
  },
  {
    title: "Duplicidade suspeita",
    code: "suspicious_duplicate",
    icon: CopyCheck,
    description:
      "Mesmo valor e contraparte repetidos rapidamente com identificadores distintos.",
    features: ["tx_count_5m", "counterparty_frequency"],
    rules: ["DUPLICATE_PATTERN"],
  },
  {
    title: "Horário e valor atípicos",
    code: "unusual_hour_amount",
    icon: MoonStar,
    description:
      "Pagamento fora da janela habitual e muito acima do histórico da conta.",
    features: ["unusual_hour", "amount_zscore"],
    rules: ["UNUSUAL_HOUR", "HIGH_AMOUNT_DEVIATION"],
  },
  {
    title: "Teste de baixo valor",
    code: "low_value_testing",
    icon: AlarmClock,
    description:
      "Tentativas pequenas, algumas negadas, seguidas por uma operação de valor maior.",
    features: ["denied_count_30m", "amount_to_mean_ratio"],
    rules: ["LOW_VALUE_TESTING"],
  },
  {
    title: "Contraparte de risco",
    code: "risky_counterparty",
    icon: UsersRound,
    description:
      "Recebedor sintético compartilhado por várias contas e concentrando anomalias.",
    features: ["counterparty_risk", "counterparty_frequency"],
    rules: ["RISKY_COUNTERPARTY"],
  },
];

export default function ScenariosPage() {
  return (
    <div className="page">
      <PageHeader
        eyebrow="VALIDATION SCENARIOS"
        title="Cobertura controlada de sinais"
        description="Oito comportamentos sintéticos exercitam features, regras e a prioridade combinada sem revelar labels na operação."
      />
      <section className="scenario-grid">
        {scenarios.map(
          (
            { title, code, icon: Icon, description, features, rules },
            index,
          ) => (
            <article className="scenario-card" key={code}>
              <header>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <Icon />
              </header>
              <h2>{title}</h2>
              <p>{description}</p>
              <div className="mini-timeline">
                <i />
                <i />
                <i className="anomaly" />
                <i className="anomaly" />
              </div>
              <dl>
                <div>
                  <dt>Features alteradas</dt>
                  <dd>
                    {features.map((item) => (
                      <code key={item}>{item}</code>
                    ))}
                  </dd>
                </div>
                <div>
                  <dt>Regras esperadas</dt>
                  <dd>
                    {rules.map((item) => (
                      <code key={item}>{item}</code>
                    ))}
                  </dd>
                </div>
              </dl>
              <small>
                Padrão demonstrativo — não implica intenção criminosa real.
              </small>
            </article>
          ),
        )}
      </section>
    </div>
  );
}
