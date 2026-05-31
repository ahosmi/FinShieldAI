import { useWebSocket } from "./hooks/useWebSocket";
import { Navbar } from "./components/layout/Navbar";
import { MetricCards } from "./components/MetricCards";
import { AlertCenter } from "./components/AlertCenter";
import { RiskAnalytics } from "./components/RiskAnalytics";
import { MerchantRiskTable } from "./components/MerchantRiskTable";
import { AIInvestigator } from "./components/AIInvestigator";

export default function App() {
  useWebSocket();   // Connect to live feed on mount

  return (
    <div className="min-h-screen bg-navy flex flex-col">
      <Navbar />

      <main className="flex-1 p-4 max-w-[1600px] mx-auto w-full space-y-4">

        {/* Row 1 — KPI Cards */}
        <MetricCards />

        {/* Row 2 — Charts */}
        <RiskAnalytics />

        {/* Row 3 — Alert Feed + Merchant Table */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="h-[420px]">
            <AlertCenter />
          </div>
          <div className="h-[420px] overflow-hidden">
            <MerchantRiskTable />
          </div>
        </div>

        {/* Row 4 — AI Investigation Panel (full width) */}
        <div className="h-[500px]">
          <AIInvestigator />
        </div>

      </main>

      <footer className="text-center text-[10px] text-slate-700 py-3 border-t border-slate-800/30">
        FinShield AI — Real-Time Fraud Intelligence · Built with Kafka · Spark · FastAPI · RAG
      </footer>
    </div>
  );
}
