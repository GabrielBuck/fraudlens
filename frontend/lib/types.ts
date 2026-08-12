export type Severity = "baixa" | "média" | "alta" | "crítica";

export interface Transaction {
  id: string;
  account_id: string;
  counterparty_id: string;
  device_id: string;
  timestamp: string;
  amount: number;
  currency: string;
  payment_method: string;
  direction: string;
  status: string;
  merchant_category: string;
  ip_country: string;
  ip_city: string;
  latitude: number;
  longitude: number;
  description: string;
}

export interface Evidence {
  triggered: boolean;
  rule_id: string;
  rule_name: string;
  weight: number;
  severity: string;
  observed_value: number;
  expected_value: string;
  description: string;
}

export interface Feedback {
  id: string;
  alert_id: string;
  classification: string;
  comment: string;
  created_at: string;
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
  context_booster: number;
  reason_codes: string[];
  explanation: string;
  evidence: Evidence[];
  status: string;
  reviewed_at?: string | null;
  reviewer_note?: string | null;
  transaction: Transaction;
  nearby_transactions?: Transaction[];
  feedback?: Feedback[];
}

export interface DatasetManifest {
  id: string;
  schema_version: string;
  generated_at: string;
  seed: number;
  account_count: number;
  transaction_count: number;
  scenario_count: number;
  scenario_rows: number;
  period_start: string;
  period_end: string;
  dataset_hash: string;
  quality_report: {
    status: string;
    passed: number;
    failed: number;
  };
}

export interface ModelRun {
  id: string;
  model_name: string;
  model_version: string;
  seed: number;
  dataset_hash: string;
  feature_signature: string;
  code_version: string;
  started_at: string;
  completed_at: string | null;
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
  artifact_hash: string;
  status: string;
}

export interface Meta {
  name: string;
  subtitle: string;
  version: string;
  language: string;
  data_classification: string;
  disclaimer: string;
  dataset: DatasetManifest | null;
  model: ModelRun | null;
  last_scoring_at: string | null;
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
    volume_change: number | null;
    comparison_available: boolean;
  };
  recent_alerts: Alert[];
  period_start: string | null;
  period_end: string | null;
  updated_at: string | null;
}

export interface Account {
  id: string;
  created_at: string;
  customer_segment: string;
  home_city: string;
  home_state: string;
  account_age_days: number;
  usual_transaction_hour_start: number;
  usual_transaction_hour_end: number;
  average_monthly_volume: number;
  risk_profile: string;
  is_active: boolean;
  transaction_count: number;
  transaction_volume: number;
  alert_count: number;
  highest_priority: number;
  last_activity: string | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
