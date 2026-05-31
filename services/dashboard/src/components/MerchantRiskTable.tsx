import { useEffect } from "react";
import { fetchMerchants } from "../api/client";
import { useFraudStore } from "../store/fraudStore";
import clsx from "clsx";

function riskBadge(avg: number) {
  if (avg >= 80) return "badge-block";
  if (avg >= 60) return "badge-challenge";
  if (avg >= 30) return "badge-monitor";
  return "badge-allow";
}

function fmt(n: number) {
  if (n >= 1_00_000) return `₹${(n / 1_00_000).toFixed(1)}L`;
  if (n >= 1_000)    return `₹${(n / 1_000).toFixed(1)}K`;
  return `₹${Math.round(n)}`;
}

export function MerchantRiskTable() {
  const { merchants, setMerchants } = useFraudStore();

  useEffect(() => {
    fetchMerchants(20)
      .then((d: { merchants: any[] }) => setMerchants(d.merchants ?? []))
      .catch(() => {});

    const id = setInterval(() => {
      fetchMerchants(20)
        .then((d: { merchants: any[] }) => setMerchants(d.merchants ?? []))
        .catch(() => {});
    }, 30_000);
    return () => clearInterval(id);
  }, [setMerchants]);

  return (
    <div className="card overflow-hidden">
      <h3 className="text-xs font-semibold uppercase tracking-widest text-cyan-400 mb-3">
        Merchant Risk Table
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/40 text-slate-500 uppercase text-[10px]">
              <th className="text-left pb-2 pr-4">Merchant</th>
              <th className="text-right pb-2 pr-4">Total Txns</th>
              <th className="text-right pb-2 pr-4">Fraud Txns</th>
              <th className="text-right pb-2 pr-4">Blocked</th>
              <th className="text-right pb-2">Avg Risk</th>
            </tr>
          </thead>
          <tbody>
            {merchants.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center text-slate-600 py-6">
                  No merchant data yet…
                </td>
              </tr>
            ) : (
              merchants.map((m) => (
                <tr
                  key={m.merchant_id}
                  className="border-b border-slate-800/40 hover:bg-slate-800/20 transition-colors"
                >
                  <td className="py-2 pr-4 text-slate-300 font-mono">{m.merchant_id}</td>
                  <td className="py-2 pr-4 text-right text-slate-400">{m.total_txns?.toLocaleString()}</td>
                  <td className="py-2 pr-4 text-right text-red-400">{m.fraud_txns?.toLocaleString()}</td>
                  <td className="py-2 pr-4 text-right text-yellow-400">{fmt(m.blocked_amount ?? 0)}</td>
                  <td className="py-2 text-right">
                    <span className={clsx("px-2 py-0.5 rounded-full text-[10px] font-bold", riskBadge(m.avg_risk ?? 0))}>
                      {m.avg_risk?.toFixed(1)}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
