export type Severity = "baixa" | "média" | "alta" | "crítica";

export interface Transaction {
  id: string;
  account_id: string;
  counterparty_id: string;
  device_id: string;
  timestamp: string;
  amount: number;
  payment_method: string;
  direction: string;
  status: string;
  ip_city: string;
  synthetic_scenario?: string | null;
}

export interface Evidence {
  rule_id: string;
  rule_name: string;
  observed_value: number;
  expected_value: string;
  description: string;
}

export interface Alert {
  id: string;
  transaction_id: string;
  account_id: string;
  created_at: string;
  risk_score: number;
  severity: Severity;
  model_score: number;
  rules_score: number;
  reason_codes: string[];
  explanation: string;
  evidence: Evidence[];
  status: string;
  transaction: Transaction;
  nearby_transactions?: Transaction[];
}

export interface Overview {
  kpis: {
    monitored_volume: number;
    transactions: number;
    alerts: number;
    critical_alerts: number;
    high_critical_alerts: number;
    alert_rate: number;
    accounts: number;
    volume_change: number;
  };
  recent_alerts: Alert[];
  updated_at: string;
}
