import { useFraudStore } from "../store/fraudStore";
import { Shield, AlertTriangle, TrendingUp, Zap } from "lucide-react";

function fmt(n: number) {
  if (n >= 1_00_000) return `₹${(n / 1_00_000).toFixed(1)}L`;
  if (n >= 1_000)    return `₹${(n / 1_000).toFixed(1)}K`;
  return `₹${n.toFixed(0)}`;
}

export function MetricCards() {
  const { stats, connected } = useFraudStore();

  const cards = [
    {
      label: "Total Alerts (24h)",
      value: stats.total.toLocaleString(),
      icon: Shield,
      color: "cyber-blue",
      border: "border-cyan-500/30",
      glow: "shadow-cyan-500/10",
    },
    {
      label: "Fraud Detected",
      value: stats.fraud_count.toLocaleString(),
      icon: AlertTriangle,
      color: "cyber-red",
      border: "border-red-500/30",
      glow: "shadow-red-500/10",
    },
    {
      label: "Fraud Rate",
      value: `${stats.fraud_rate.toFixed(1)}%`,
      icon: TrendingUp,
      color: "cyber-yellow",
      border: "border-yellow-500/30",
      glow: "shadow-yellow-500/10",
    },
    {
      label: "Blocked Amount",
      value: fmt(stats.blocked_amount),
      icon: Zap,
      color: "cyber-green",
      border: "border-green-500/30",
      glow: "shadow-green-500/10",
    },
  ];

  const colorMap: Record<string, string> = {
    "cyber-blue":   "text-cyan-400",
    "cyber-red":    "text-red-400",
    "cyber-yellow": "text-yellow-400",
    "cyber-green":  "text-green-400",
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <div
            key={c.label}
            className={`card ${c.border} shadow-lg ${c.glow} flex items-center gap-3`}
          >
            <div className={`p-2 rounded-lg bg-navy-card/50`}>
              <Icon className={`w-5 h-5 ${colorMap[c.color]}`} />
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">{c.label}</p>
              <p className={`text-xl font-bold ${colorMap[c.color]}`}>{c.value}</p>
            </div>
          </div>
        );
      })}

      {/* Connection status dot */}
      <div className="col-span-2 lg:col-span-4 flex justify-end items-center gap-2 px-1">
        <span
          className={`w-2 h-2 rounded-full ${connected ? "bg-green-400 animate-pulse" : "bg-red-500"}`}
        />
        <span className="text-xs text-slate-500">
          {connected ? "Live feed connected" : "Reconnecting..."}
        </span>
      </div>
    </div>
  );
}
