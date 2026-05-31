import { useState, useRef, useEffect } from "react";
import { askAI } from "../api/client";
import { Send, Bot, User, Loader } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

const SUGGESTIONS = [
  "Why was this transaction flagged?",
  "What is refund cycling fraud?",
  "Explain mule account detection",
  "What are RBI step-up auth requirements?",
  "What is velocity abuse?",
];

export function AIInvestigator() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello, I'm your FinShield AI Fraud Analyst. Ask me about flagged transactions, fraud patterns, RBI compliance, or AML guidelines. I'll retrieve relevant case history and policy context to answer you.",
    },
  ]);
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const bottomRef               = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (q: string) => {
    if (!q.trim() || loading) return;
    const userMsg: Message = { role: "user", content: q };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await askAI(q);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, sources: res.sources?.filter(Boolean) },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "⚠️ AI service is temporarily unavailable. Ensure Ollama is running with `make pull-model`." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card h-full flex flex-col overflow-hidden">
      <div className="flex items-center gap-2 mb-3 flex-shrink-0">
        <Bot className="w-4 h-4 text-cyan-400" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-cyan-400">
          AI Investigation Assistant
        </h3>
        <span className="ml-auto text-[10px] text-slate-600">Powered by Mistral + RAG</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px]
              ${msg.role === "assistant" ? "bg-cyan-500/20 text-cyan-400" : "bg-purple-500/20 text-purple-400"}`}>
              {msg.role === "assistant" ? <Bot className="w-3 h-3" /> : <User className="w-3 h-3" />}
            </div>
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed
              ${msg.role === "assistant"
                ? "bg-slate-800/60 text-slate-200 border border-slate-700/40"
                : "bg-cyan-500/10 text-cyan-100 border border-cyan-500/20"}`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-700/40">
                  <p className="text-[10px] text-slate-500 mb-1">Sources:</p>
                  {msg.sources.map((s, si) => (
                    <span key={si} className="inline-block text-[10px] bg-slate-700/50 text-slate-400 px-1.5 py-0.5 rounded mr-1 mb-1">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-2">
            <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center">
              <Bot className="w-3 h-3 text-cyan-400" />
            </div>
            <div className="bg-slate-800/60 border border-slate-700/40 rounded-xl px-3 py-2">
              <Loader className="w-3 h-3 text-cyan-400 animate-spin" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-1.5 mb-3 flex-shrink-0">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-[10px] bg-slate-800/60 hover:bg-cyan-500/10 border border-slate-700/40 hover:border-cyan-500/30 text-slate-400 hover:text-cyan-400 px-2 py-1 rounded-full transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2 flex-shrink-0">
        <input
          className="flex-1 bg-slate-800/60 border border-slate-700/40 focus:border-cyan-500/50 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-600 outline-none transition-colors"
          placeholder="Ask about a transaction, fraud pattern, or policy…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send(input)}
        />
        <button
          onClick={() => send(input)}
          disabled={!input.trim() || loading}
          className="p-2 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 rounded-lg text-cyan-400 disabled:opacity-40 transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
