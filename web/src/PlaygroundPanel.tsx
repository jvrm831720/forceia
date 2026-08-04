import { useRef, useState } from "react";

const TOKEN_KEY = "forceia_admin_token";

type HistMsg = { role: string; content: string; agent?: string };
type PlayLead = {
  name?: string;
  company?: string;
  stage?: string;
  bant?: Record<string, string>;
  bant_score?: number;
};

async function api<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY) || "";
  const res = await fetch(path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      "X-Admin-Token": token,
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export default function PlaygroundPanel({ workspace }: { workspace: string | null }) {
  const [name, setName] = useState("Ana Silva");
  const [company, setCompany] = useState("Clínica Sol");
  const [persona, setPersona] = useState("Dona de clínica, curiosa sobre preço e prazo");
  const [agent, setAgent] = useState("sdr");
  const [input, setInput] = useState("Oi, quero entender como funciona");
  const [history, setHistory] = useState<HistMsg[]>([]);
  const [lead, setLead] = useState<PlayLead | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);

  const reset = () => {
    setHistory([]);
    setLead(null);
    setErr("");
  };

  const send = async () => {
    if (!workspace || !input.trim() || busy) return;
    setBusy(true);
    setErr("");
    try {
      const res = await api<{
        reply: string;
        agent: string;
        history: HistMsg[];
        lead: PlayLead;
      }>(`/api/workspaces/${workspace}/playground`, {
        method: "POST",
        body: JSON.stringify({
          message: input.trim(),
          history,
          agent: agent || null,
          lead: {
            name,
            company,
            stage: lead?.stage || "sdr",
            persona_note: persona,
            bant: lead?.bant || {},
          },
        }),
      });
      setHistory(res.history || []);
      setLead(res.lead);
      setInput("");
      setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    } catch (e) {
      setErr((e as Error).message || "Falha no playground");
    } finally {
      setBusy(false);
    }
  };

  if (!workspace) return <div className="empty">Selecione um workspace</div>;

  return (
    <div className="product-stack">
      <div className="card full">
        <div className="panel-toolbar">
          <div>
            <h2>Playground</h2>
            <p className="panel-desc" style={{ margin: "4px 0 0" }}>
              Teste o SDR/Closer com um lead fictício — não grava no funil real.
            </p>
          </div>
          <button className="btn btn-ghost" onClick={reset}>
            Limpar conversa
          </button>
        </div>

        <div className="play-setup">
          <div className="field">
            <label>Nome do lead</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="field">
            <label>Empresa</label>
            <input value={company} onChange={(e) => setCompany(e.target.value)} />
          </div>
          <div className="field">
            <label>Agente</label>
            <select className="filter-select" value={agent} onChange={(e) => setAgent(e.target.value)}>
              <option value="sdr">SDR</option>
              <option value="closer">Closer</option>
              <option value="followup">Follow-up</option>
            </select>
          </div>
        </div>
        <div className="field">
          <label>Persona / contexto</label>
          <input value={persona} onChange={(e) => setPersona(e.target.value)} />
        </div>

        {lead && (
          <div className="play-lead-status">
            <span className="tag">{lead.stage || "sdr"}</span>
            <span>BANT score: {lead.bant_score ?? 0}</span>
            {lead.bant &&
              Object.entries(lead.bant)
                .filter(([, v]) => v)
                .map(([k, v]) => (
                  <span key={k} className="play-bant-chip">
                    {k}: {String(v).slice(0, 40)}
                  </span>
                ))}
          </div>
        )}

        <div className="chat-scroll play-chat">
          {!history.length && (
            <div className="empty">Envie a primeira mensagem como se fosse o lead.</div>
          )}
          {history.map((m, i) => {
            const isUser = m.role === "user";
            return (
              <div key={i} className={"chat-row " + (isUser ? "user" : "assistant")}>
                <div className="chat-bubble">{m.content}</div>
                <div className="chat-meta">{isUser ? "lead fictício" : m.agent || "agente"}</div>
              </div>
            );
          })}
          <div ref={endRef} />
        </div>

        {err && <div className="err">{err}</div>}

        <div className="play-compose">
          <textarea
            className="note-input"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
            placeholder="Mensagem do lead…"
          />
          <button className="btn btn-primary" disabled={busy || !input.trim()} onClick={() => void send()}>
            {busy ? "Gerando…" : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
}
