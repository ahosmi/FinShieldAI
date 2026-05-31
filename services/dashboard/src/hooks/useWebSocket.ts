import { useEffect, useRef, useCallback } from "react";
import { useFraudStore } from "../store/fraudStore";

const WS_URL = (import.meta.env.VITE_WS_URL as string) || "ws://localhost:8000/ws/alerts";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { addAlert, setConnected } = useFraudStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log("[FinShield WS] Connected");
      // Keep-alive ping every 25s
      const ping = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) ws.send("ping");
        else clearInterval(ping);
      }, 25_000);
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === "FRAUD_ALERT") addAlert(msg.payload);
      } catch {
        // ignore non-JSON frames
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log("[FinShield WS] Disconnected — reconnecting in 3s");
      setTimeout(connect, 3_000);
    };

    ws.onerror = () => ws.close();
  }, [addAlert, setConnected]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);
}
