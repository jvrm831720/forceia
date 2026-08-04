import { useCallback, useEffect, useState } from "react";

const TOKEN_KEY = "forceia_admin_token";

type Playbook = {
  version?: number;
  company_name?: string;
  product_summary?: string;
  value_proposition?: string;
  icp?: {
    industries?: string[];
    company_sizes?: string;
    roles?: string[];
    geographies?: string;
    disqualifiers?: string[];
  };
  persona?: { buyer_titles?: string[]; pains?: string[]; goals?: string[] };
  pricing?: { model?: string; range?: string; notes?: string };
  cases?: { title?: string; result?: string; segment?: string }[];
  objections?: { objection?: string; response?: string }[];
  tone?: { style?: string; formality?: string; do?: string[]; dont?: string[] };
  faq?: { q?: string; a?: string }[];
  script_notes?: string;
  extra?: string;
};

type PlaybookCompleteness = {
  score: number;
  ready: boolean;
  checks?: Record<string, boolean>;
  sections_filled?: number;
  sections_total?: number;
};

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

async function api<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : "",
      "X-Admin-Token": token,
      ...(opts.headers || {}),
    },
  });
  if (res.status === 401) throw new Error("unauthorized");
  if (!res.ok) throw new Error((await res.text()) || String(res.status));
  return res.json() as Promise<T>;
}

function listToStr(v?: string[]) {
  return (v || []).join(", ");
}
function strToList(s: string) {
  return s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}

/** Editor do playbook comercial por workspace — injetado no system prompt dos agentes. */
export default function PlaybookPanel({ workspace }: { workspace: string | null }) {
  const [playbook, setPlaybook] = useState<Playbook | null>(null);
  const [completeness, setCompleteness] = useState<PlaybookCompleteness | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    if (!workspace) return;
    setMsg("");
    try {
      const data = await api<{ playbook: Playbook; completeness: PlaybookCompleteness }>(
        `/api/workspaces/${workspace}/playbook`,
      );
      setPlaybook(data.playbook || {});
      setCompleteness(data.completeness || null);
    } catch {
      setPlaybook({});
      setCompleteness(null);
      setMsg("Não foi possível carregar o playbook.");
    }
  }, [workspace]);

  const save = useCallback(async () => {
    if (!workspace || !playbook || busy) return;
    setBusy(true);
    setMsg("");
    try {
      const data = await api<{ playbook: Playbook; completeness: PlaybookCompleteness }>(
        `/api/workspaces/${workspace}/playbook`,
        { method: "PUT", body: JSON.stringify(playbook) },
      );
      setPlaybook(data.playbook || playbook);
      setCompleteness(data.completeness || null);
      setMsg("Playbook salvo. Os agentes já usam na próxima mensagem.");
    } catch (e) {
      setMsg("Falha ao salvar: " + ((e as Error).message || e));
    } finally {
      setBusy(false);
    }
  }, [workspace, playbook, busy]);

  useEffect(() => {
    void load();
  }, [load]);

  const score = completeness?.score ?? 0;
  const ready = completeness?.ready ?? false;
  const barColor = score >= 80 ? "var(--won)" : score >= 50 ? "var(--signal)" : "var(--lost)";

  return (
    <div className="card full playbook-card">
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
        <div>
          <h2 style={{ margin: 0 }}>Playbook comercial</h2>
          <div className="sub" style={{ marginTop: 4 }}>
            ICP, pricing, cases e tom — vira contexto obrigatório do SDR, Closer e Follow-up
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" disabled={!workspace} onClick={() => void load()}>
            Recarregar
          </button>
          <button className="btn btn-primary" disabled={!workspace || busy} onClick={() => void save()}>
            {busy ? "Salvando…" : "Salvar playbook"}
          </button>
        </div>
      </div>

      <div className="pb-score">
        <div className="pb-score-bar">
          <div className="pb-score-fill" style={{ width: `${score}%`, background: barColor }} />
        </div>
        <div className="pb-score-meta">
          <span>
            Completeness <strong>{score}</strong>/100
          </span>
          <span>{ready ? "✓ pronto para produção" : "preencha ICP + produto + pricing (≥50)"}</span>
          {completeness?.sections_filled != null && (
            <span>
              {completeness.sections_filled}/{completeness.sections_total} seções
            </span>
          )}
        </div>
      </div>
      <div className={msg.startsWith("Falha") || msg.startsWith("Não") ? "err" : "pb-ok"}>{msg}</div>

      {!playbook ? (
        <div className="empty">Carregando…</div>
      ) : (
        <div className="pb-grid">
          <div className="field">
            <label>Nome da empresa / marca</label>
            <input
              value={playbook.company_name || ""}
              onChange={(e) => setPlaybook({ ...playbook, company_name: e.target.value })}
              placeholder="Clínica Sol"
            />
          </div>
          <div className="field">
            <label>Tom — estilo</label>
            <input
              value={playbook.tone?.style || "consultivo"}
              onChange={(e) =>
                setPlaybook({ ...playbook, tone: { ...(playbook.tone || {}), style: e.target.value } })
              }
              placeholder="consultivo / direto / técnico"
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Produto / serviço (resumo)</label>
            <textarea
              className="note-input"
              rows={2}
              value={playbook.product_summary || ""}
              onChange={(e) => setPlaybook({ ...playbook, product_summary: e.target.value })}
              placeholder="O que vocês vendem, em 2–3 frases"
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Proposta de valor</label>
            <textarea
              className="note-input"
              rows={2}
              value={playbook.value_proposition || ""}
              onChange={(e) => setPlaybook({ ...playbook, value_proposition: e.target.value })}
              placeholder="Por que o cliente escolhe vocês"
            />
          </div>
          <div className="field">
            <label>ICP — setores</label>
            <input
              value={listToStr(playbook.icp?.industries)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  icp: { ...(playbook.icp || {}), industries: strToList(e.target.value) },
                })
              }
              placeholder="saúde, clínicas, odontologia"
            />
          </div>
          <div className="field">
            <label>ICP — porte</label>
            <input
              value={playbook.icp?.company_sizes || ""}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  icp: { ...(playbook.icp || {}), company_sizes: e.target.value },
                })
              }
              placeholder="10–200 funcionários"
            />
          </div>
          <div className="field">
            <label>ICP — cargos-alvo</label>
            <input
              value={listToStr(playbook.icp?.roles)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  icp: { ...(playbook.icp || {}), roles: strToList(e.target.value) },
                })
              }
              placeholder="dono, gerente comercial, CEO"
            />
          </div>
          <div className="field">
            <label>ICP — geografia</label>
            <input
              value={playbook.icp?.geographies || ""}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  icp: { ...(playbook.icp || {}), geographies: e.target.value },
                })
              }
              placeholder="Brasil, SP e RJ"
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Fora do ICP (desqualificadores)</label>
            <input
              value={listToStr(playbook.icp?.disqualifiers)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  icp: { ...(playbook.icp || {}), disqualifiers: strToList(e.target.value) },
                })
              }
              placeholder="só estudante, sem CNPJ, ticket baixo"
            />
          </div>
          <div className="field">
            <label>Persona — títulos do comprador</label>
            <input
              value={listToStr(playbook.persona?.buyer_titles)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  persona: { ...(playbook.persona || {}), buyer_titles: strToList(e.target.value) },
                })
              }
              placeholder="CEO, Head de Vendas"
            />
          </div>
          <div className="field">
            <label>Persona — dores</label>
            <input
              value={listToStr(playbook.persona?.pains)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  persona: { ...(playbook.persona || {}), pains: strToList(e.target.value) },
                })
              }
              placeholder="leads esfriando, SDR caro, follow-up manual"
            />
          </div>
          <div className="field">
            <label>Persona — objetivos</label>
            <input
              value={listToStr(playbook.persona?.goals)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  persona: { ...(playbook.persona || {}), goals: strToList(e.target.value) },
                })
              }
              placeholder="mais reuniões qualificadas, previsibilidade"
            />
          </div>
          <div className="field">
            <label>Pricing — faixa</label>
            <input
              value={playbook.pricing?.range || ""}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  pricing: { ...(playbook.pricing || {}), range: e.target.value },
                })
              }
              placeholder="R$ 997 a R$ 4.900 / mês"
            />
          </div>
          <div className="field">
            <label>Pricing — modelo</label>
            <input
              value={playbook.pricing?.model || ""}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  pricing: { ...(playbook.pricing || {}), model: e.target.value },
                })
              }
              placeholder="assinatura mensal"
            />
          </div>
          <div className="field">
            <label>Pricing — notas</label>
            <input
              value={playbook.pricing?.notes || ""}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  pricing: { ...(playbook.pricing || {}), notes: e.target.value },
                })
              }
              placeholder="piloto 14 dias no plano completo"
            />
          </div>
          <div className="field">
            <label>Formalidade</label>
            <input
              value={playbook.tone?.formality || "semi-formal"}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  tone: { ...(playbook.tone || {}), formality: e.target.value },
                })
              }
              placeholder="semi-formal / formal / informal"
            />
          </div>
          <div className="field">
            <label>Tom — faça</label>
            <input
              value={listToStr(playbook.tone?.do)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  tone: { ...(playbook.tone || {}), do: strToList(e.target.value) },
                })
              }
              placeholder="usar exemplos do setor, oferecer 2 horários"
            />
          </div>
          <div className="field">
            <label>Tom — não faça</label>
            <input
              value={listToStr(playbook.tone?.dont)}
              onChange={(e) =>
                setPlaybook({
                  ...playbook,
                  tone: { ...(playbook.tone || {}), dont: strToList(e.target.value) },
                })
              }
              placeholder="prometer ROI garantido, ser agressivo"
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Cases (um por linha: título | resultado | segmento)</label>
            <textarea
              className="note-input"
              rows={3}
              value={(playbook.cases || [])
                .map((c) => [c.title, c.result, c.segment].filter(Boolean).join(" | "))
                .join("\n")}
              onChange={(e) => {
                const cases = e.target.value
                  .split("\n")
                  .map((line) => line.trim())
                  .filter(Boolean)
                  .map((line) => {
                    const [title = "", result = "", segment = ""] = line.split("|").map((s) => s.trim());
                    return { title, result, segment };
                  });
                setPlaybook({ ...playbook, cases });
              }}
              placeholder={"Clínica XP | +40% reuniões | saúde\nAcme SaaS | ciclo -15 dias | B2B"}
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Objeções (um por linha: objeção | resposta)</label>
            <textarea
              className="note-input"
              rows={3}
              value={(playbook.objections || [])
                .map((o) => [o.objection, o.response].filter(Boolean).join(" | "))
                .join("\n")}
              onChange={(e) => {
                const objections = e.target.value
                  .split("\n")
                  .map((line) => line.trim())
                  .filter(Boolean)
                  .map((line) => {
                    const [objection = "", response = ""] = line.split("|").map((s) => s.trim());
                    return { objection, response };
                  });
                setPlaybook({ ...playbook, objections });
              }}
              placeholder={"está caro | compare com 1 SDR pleno…\njá temos time | automatizamos o follow-up"}
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>FAQ (um por linha: pergunta | resposta)</label>
            <textarea
              className="note-input"
              rows={3}
              value={(playbook.faq || []).map((f) => [f.q, f.a].filter(Boolean).join(" | ")).join("\n")}
              onChange={(e) => {
                const faq = e.target.value
                  .split("\n")
                  .map((line) => line.trim())
                  .filter(Boolean)
                  .map((line) => {
                    const [q = "", a = ""] = line.split("|").map((s) => s.trim());
                    return { q, a };
                  });
                setPlaybook({ ...playbook, faq });
              }}
              placeholder={"Integra com RD? | Sim, via webhook.\nTem piloto? | 14 dias no plano completo."}
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Notas de script / processo</label>
            <textarea
              className="note-input"
              rows={2}
              value={playbook.script_notes || ""}
              onChange={(e) => setPlaybook({ ...playbook, script_notes: e.target.value })}
              placeholder="Sempre oferecer 2 horários; qualificar BANT antes de agenda"
            />
          </div>
          <div className="field" style={{ gridColumn: "1 / -1" }}>
            <label>Contexto extra</label>
            <textarea
              className="note-input"
              rows={2}
              value={playbook.extra || ""}
              onChange={(e) => setPlaybook({ ...playbook, extra: e.target.value })}
              placeholder="Qualquer regra interna que o agente precisa respeitar"
            />
          </div>
        </div>
      )}
    </div>
  );
}
