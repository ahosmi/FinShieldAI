import { create } from "zustand";
import type { FraudAlert, DashboardStats, MerchantRisk } from "../types";

interface FraudStore {
  alerts: FraudAlert[];
  stats: DashboardStats;
  merchants: MerchantRisk[];
  connected: boolean;
  addAlert: (alert: FraudAlert) => void;
  setStats: (stats: Partial<DashboardStats>) => void;
  setMerchants: (merchants: MerchantRisk[]) => void;
  setConnected: (v: boolean) => void;
}

export const useFraudStore = create<FraudStore>((set) => ({
  alerts: [],
  stats: { total: 0, fraud_count: 0, fraud_rate: 0, blocked_amount: 0, avg_risk: 0 },
  merchants: [],
  connected: false,

  addAlert: (alert) =>
    set((s) => ({
      alerts: [alert, ...s.alerts].slice(0, 150),
      stats: {
        ...s.stats,
        total: s.stats.total + 1,
        fraud_count: alert.is_fraud ? s.stats.fraud_count + 1 : s.stats.fraud_count,
        blocked_amount:
          alert.decision === "BLOCK"
            ? s.stats.blocked_amount + alert.amount
            : s.stats.blocked_amount,
      },
    })),

  setStats:     (stats)     => set((s) => ({ stats: { ...s.stats, ...stats } })),
  setMerchants: (merchants) => set({ merchants }),
  setConnected: (v)         => set({ connected: v }),
}));
