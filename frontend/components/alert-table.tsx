import { ArrowUpRight } from "lucide-react";
import Link from "next/link";
import { currency, dateTime } from "@/lib/format";
import type { Alert } from "@/lib/types";
import { EmptyState, SeverityBadge, StatusBadge } from "./ui";

export function AlertTable({
  alerts,
  compact = false,
}: {
  alerts: Alert[];
  compact?: boolean;
}) {
  if (!alerts.length)
    return (
      <EmptyState title="Nenhum alerta encontrado">
        <p>Ajuste os filtros ou execute o pipeline para gerar alertas.</p>
      </EmptyState>
    );
  return (
    <div className="table-scroll">
      <table>
        <caption className="sr-only">
          Alertas priorizados para investigação
        </caption>
        <thead>
          <tr>
            <th>Prioridade</th>
            <th>Conta e motivo</th>
            <th>Pagamento</th>
            {!compact && <th>Status</th>}
            <th>
              <span className="sr-only">Abrir</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id}>
              <td>
                <div className="priority-cell">
                  <strong>{alert.risk_score.toFixed(0)}</strong>
                  <SeverityBadge severity={alert.severity} />
                </div>
              </td>
              <td>
                <strong>{alert.account_id}</strong>
                <small>
                  {alert.reason_codes[0]?.replaceAll("_", " ") ??
                    "Anomalia do modelo"}
                </small>
              </td>
              <td>
                <strong>{currency(alert.transaction.amount)}</strong>
                <small>
                  {alert.transaction.payment_method} ·{" "}
                  {dateTime(alert.transaction.timestamp)}
                </small>
              </td>
              {!compact && (
                <td>
                  <StatusBadge status={alert.status} />
                </td>
              )}
              <td>
                <Link
                  className="icon-button"
                  href={`/alerts/${alert.id}`}
                  aria-label={`Investigar alerta ${alert.id}`}
                >
                  <ArrowUpRight size={17} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
