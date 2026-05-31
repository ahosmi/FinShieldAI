import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { fetchRiskDist, fetchFraudByType } from "../api/client";

const DECISION_COLORS: Record<string, string> = {
  BLOCK:     "#ff3366",
  CHALLENGE: "#ffa500",
  MONITOR:   "#ffd700",
  ALLOW:     "#00ff88",
};

const SCENARIO_COLOR = "#00d4ff";

export function RiskAnalytics() {
  const [dist, setDist]    = useState<{ name: string; value: number }[]>([]);
  const [byType, setByType] = useState<{ name: string; count: number }[]>([]);

  useEffect(() => {
    fetchRiskDist().then((d: Record<string, number>) =>
      setDist(Object.entries(d).map(([name, value]) => ({ name, value: Number(value) })))
    ).catch(() => {});

    fetchFraudByType().then((rows: { fraud_scenario: string; count: number }[]) =>
      setByType(rows.map((r) => ({ name: r.fraud_scenario ?? "UNKNOWN", count: Number(r.count) })))
    ).catch(() => {});

    const id = setInterval(() => {
      fetchRiskDist().then((d: Record<string, number>) =>
        setDist(Object.entries(d).map(([name, value]) => ({ name, value: Number(value) })))
      ).catch(() => {});
    }, 15_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
      {/* Risk Distribution Donut */}
      <div className="card">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-cyan-400 mb-4">
          Risk Distribution (24h)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={dist}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              strokeWidth={0}
            >
              {dist.map((entry) => (
                <Cell key={entry.name} fill={DECISION_COLORS[entry.name] ?? "#64748b"} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ background: "#0f1629", border: "1px solid rgba(0,212,255,0.2)", borderRadius: 8, fontSize: 11 }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, color: "#94a3b8" }}
              formatter={(v) => v}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Fraud by Scenario Bar */}
      <div className="card">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-cyan-400 mb-4">
          Fraud by Scenario (24h)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={byType} margin={{ left: -20 }}>
            <XAxis dataKey="name" tick={{ fontSize: 9, fill: "#64748b" }} interval={0} angle={-30} textAnchor="end" height={50} />
            <YAxis tick={{ fontSize: 9, fill: "#64748b" }} />
            <Tooltip
              contentStyle={{ background: "#0f1629", border: "1px solid rgba(0,212,255,0.2)", borderRadius: 8, fontSize: 11 }}
              cursor={{ fill: "rgba(0,212,255,0.05)" }}
            />
            <Bar dataKey="count" fill={SCENARIO_COLOR} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
