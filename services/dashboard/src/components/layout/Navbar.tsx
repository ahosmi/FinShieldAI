import { Shield } from "lucide-react";
import { useFraudStore } from "../../store/fraudStore";

export function Navbar() {
  const connected = useFraudStore((s) => s.connected);

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-cyan-500/10 bg-navy-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <Shield className="w-6 h-6 text-cyan-400" />
        <div>
          <h1 className="text-sm font-bold tracking-widest text-white uppercase">FinShield AI</h1>
          <p className="text-[10px] text-slate-500">Fraud & Risk Intelligence Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <span className="text-[10px] text-slate-500 uppercase tracking-widest hidden md:block">
          {new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata", hour12: false })} IST
        </span>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-400 animate-pulse" : "bg-red-500"}`} />
          <span className="text-[10px] text-slate-400">{connected ? "LIVE" : "OFFLINE"}</span>
        </div>
      </div>
    </header>
  );
}
