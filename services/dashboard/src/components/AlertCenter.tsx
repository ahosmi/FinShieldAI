import { useFraudStore } from "../store/fraudStore";
import type { FraudAlert } from "../types";
import clsx from "clsx";

const DECISION_STYLE: Record<string, string> = {
  BLOCK:     "badge-block",
  CHALLENGE: "badge-challenge",
  MONITOR:   "badge-monitor",
  ALLOW:     "badge-allow",
};

function relTime(ts: string) {
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 60)  return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  return `${Math.floor(diff/3600)}h ago`;
}

function AlertRow({ a }: { a: FraudAlert }) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg bg-navy-card/60 border border-slate-700/40 hover:border-cyan-500/30 transition-colors animate-slide-in">
      <div className="flex justify-between items-center">
        <span className="font-mono text-[10px] text-slate-500">{a.transaction_id}</span>
        <span className={clsx("text-[10px] font-bold px-2 py-0.5 rounded-full", DECISION_STYLE[a.decision])}>
          {a.decision}
        </span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-300">{a.user_id}</span>
        <span className="text-sm font-bold text-white">
          ₹{(a.amount ?? 0).toLocaleString("en-IN")}
        </span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-[10px] text-slate-500">
          {a.fraud_scenario ?? a.fraud_type ?? "RULE_BASED"} · {a.city ?? a.region ?? "–"}
        </span>
        <span className="text-[11px] font-bold text-red-400">
          {a.risk_score?.toFixed(1)}/100
        </span>
      </div>
      <div className="text-[10px] text-slate-600">{relTime(a.timestamp)}</div>
    </div>
  );
}

export function AlertCenter() {
  const alerts = useFraudStore((s) => s.alerts);
  const fraudAlerts = alerts.filter((a) => a.decision !== "ALLOW");

  return (
    <div className="card h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-cyan-400">
          🚨 Live Alert Center
        </h2>
        <span className="text-xs text-slate-500">{fraudAlerts.length} alerts</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {fraudAlerts.length === 0 ? (
          <div className="text-center text-slate-600 text-xs mt-12">
            <div className="text-2xl mb-2">🛡️</div>
            Monitoring live stream…
          </div>
        ) : (
          fraudAlerts.slice(0, 50).map((a) => (
            <AlertRow key={a.transaction_id} a={a} />
          ))
        )}
      </div>
    </div>
  );
}
