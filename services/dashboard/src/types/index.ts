export interface FraudAlert {
  transaction_id: string;
  user_id: string;
  merchant_id: string | null;
  amount: number;
  risk_score: number;
  rule_score: number;
  ml_score: number;
  decision: "ALLOW" | "MONITOR" | "CHALLENGE" | "BLOCK";
  fraud_type: string | null;
  fraud_scenario: string | null;
  rule_triggers: RuleTrigger[];
  is_fraud: boolean;
  region: string | null;
  city: string | null;
  transaction_type: string | null;
  timestamp: string;
}

export interface RuleTrigger {
  rule_id: string;
  description: string;
  score_contribution: number;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
}

export interface DashboardStats {
  total: number;
  fraud_count: number;
  fraud_rate: number;
  blocked_amount: number;
  avg_risk: number;
}

export interface MerchantRisk {
  merchant_id: string;
  total_txns: number;
  fraud_txns: number;
  avg_risk: number;
  blocked_amount: number;
}

export interface SuspiciousUser {
  user_id: string;
  risk_score: number;
}
