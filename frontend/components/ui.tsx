import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import type { ReactNode } from "react";
import type { Severity } from "@/lib/types";

export function SeverityBadge({ severity }: { severity: Severity | string }) {
  return (
    <span className={`badge severity-${severity.replace("í", "i")}`}>
      <i />
      {severity}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  return <span className="status-badge">{status}</span>;
}

export function Score({
  value,
  size = "normal",
}: {
  value: number;
  size?: "normal" | "large";
}) {
  return (
    <div
      className={`score score-${size}`}
      style={
        {
          "--score": `${Math.min(100, Math.max(0, value)) * 3.6}deg`,
        } as React.CSSProperties
      }
    >
      <span>
        <strong>{value.toFixed(0)}</strong>
        <small>/100</small>
      </span>
    </div>
  );
}

export function MetricCard({
  label,
  value,
  change,
  context,
  icon,
}: {
  label: string;
  value: string;
  change?: number;
  context: string;
  icon: ReactNode;
}) {
  const Trend =
    change == null ? Minus : change > 0 ? ArrowUpRight : ArrowDownRight;
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className="metric-icon">{icon}</span>
        {change != null && (
          <span className={change >= 0 ? "trend up" : "trend down"}>
            <Trend size={14} />
            {Math.abs(change).toFixed(1)}%
          </span>
        )}
      </div>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      <small>{context}</small>
    </article>
  );
}

export function EmptyState({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <div>{children}</div>
    </div>
  );
}
