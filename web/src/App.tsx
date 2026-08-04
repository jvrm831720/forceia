import PlaybookPanel from "./PlaybookPanel";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const STAGE_COLORS: Record<string, string> = {
  sdr: "var(--sdr)",
  qualified: "var(--qualified)",
  closer: "var(--closer)",
  followup: "var(--followup)",
  won: "var(--won)",
  lost: "var(--lost)",
};
const STAGE_ORDER = ["sdr", "qualified", "closer", "followup", "won", "lost"];
const AGENT_COLORS: Record<string, string> = {
  sdr: "var(--sdr)",
  closer: "var(--closer)",
  followup: "var(--followup)",
};
const TOKEN_KEY = "forceia_admin_token";

type Workspace = { id: string; name: string; slug: string };
type Metrics = { total: number; win_rate: number; by_stage: Record<string, number> };
type LeadNote = { note?: string; author?: string; at?: string };
type Lead = {
  id?: string;
  phone?: string;
  name?: string;
  company?: string;
  stage?: string;
  last_message_at?: string;
  updated_at?: string;
  metadata?: { agent_paused?: boolean; human_takeover?: boolean; notes?: LeadNote[] };
};
type EventRow = { type?: string; created_at?: string };
type Suggestion = { id: string; agent?: string; title?: string; rationale?: string };
type LeadEvent = {
  id?: string;
  type?: string;
  payload?: Record<string, unknown>;
  created_at?: string;
};
type LeadDetail = {
  lead: Lead & {
    email?: string;
    bant?: Record<string, string>;
    metadata?: Record<string, unknown>;
    created_at?: string;
    agent_paused?: boolean;
    notes?: LeadNote[];
  };
  messages: { role?: string; content?: string; agent?: string; created_at?: string }[];
  message_count: number;
  events?: LeadEvent[];
};

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}
function setToken(t: string) {
  localStorage.setItem(TOKEN_KEY, t);
}
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
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

function fmtDate(s?: string | null) {
  if (!s) return "—";
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function fmtDateFull(s?: string | null) {
  if (!s) return "—";
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function waLink(phone?: string) {
  if (!phone) return null;
  const digits = phone.replace(/\D/g, "");
  if (digits.length < 10) return null;
  return `https://wa.me/${digits}`;
}

type Tab = "overview" | "leads" | "events" | "playbook" | "learning";

export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [usernameInput, setUsernameInput] = useState("admin");
  const [passwordInput, setPasswordInput] = useState("");
  const [gateErr, setGateErr] = useState("");
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [current, setCurrent] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [events, setEvents] = useState<EventRow[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [tab, setTab] = useState<Tab>("overview");
  const [sub, setSub] = useState("Time de agentes · SDR · Closer · Follow-up");
  const [wsOpen, setWsOpen] = useState(false);
  const [wsName, setWsName] = useState("");
  const [wsSlug, setWsSlug] = useState("");
  const [wsInst, setWsInst] = useState("");
  const [wsKey, setWsKey] = useState<string | null>(null);
  const [wsErr, setWsErr] = useState("");
  const [learnBusy, setLearnBusy] = useState(false);
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [leadDetail, setLeadDetail] = useState<LeadDetail | null>(null);
  const [leadDetailLoading, setLeadDetailLoading] = useState(false);
  const [leadDetailErr, setLeadDetailErr] = useState("");
  const [stageBusy, setStageBusy] = useState(false);
  const [pauseBusy, setPauseBusy] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [noteBusy, setNoteBusy] = useState(false);
  const [leadFilter, setLeadFilter] = useState("");
  const [stageFilter, setStageFilter] = useState<string>("all");
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const loadWorkspaces = useCallback(async () => {
    const wss = await api<Workspace[]>("/api/workspaces");
    setWorkspaces(wss);
    setAuthed(true);
    setCurrent((c) => c || (wss[0]?.slug ?? null));
  }, []);

  const selectWorkspace = useCallback(async (slug: string) => {
    setCurrent(slug);
    setSelectedLeadId(null);
    setLeadDetail(null);
    setLeadDetailErr("");
    setNoteText("");
    setLeadFilter("");
    setStageFilter("all");
    setSub("carregando…");
    try {
      const [m, l, ev] = await Promise.all([
        api<Metrics>(`/api/workspaces/${slug}/metrics`),
        api<Lead[]>(`/api/workspaces/${slug}/leads?limit=80`),
        api<EventRow[]>(`/api/workspaces/${slug}/events?limit=40`),
      ]);
      setMetrics(m);
      setLeads(l);
      setEvents(ev);
      setSub(`${m.total} leads · atualizado agora`);
    } catch {
      setSub("erro ao carregar");
    }
  }, []);

  const loadLearning = useCallback(async () => {
    try {
      const rows = await api<Suggestion[]>("/api/learning/suggestions?status=pending");
      setSuggestions(rows || []);
    } catch {
      setSuggestions([]);
    }
  }, []);

  const loadLeadDetail = useCallback(
    async (leadId: string) => {
      if (!current) return;
      setLeadDetailLoading(true);
      setLeadDetailErr("");
      try {
        const data = await api<LeadDetail>(
          `/api/workspaces/${current}/leads/${leadId}?messages_limit=200`,
        );
        setLeadDetail(data);
        setSelectedLeadId(leadId);
      } catch {
        setLeadDetail(null);
        setLeadDetailErr("Não foi possível carregar o lead.");
      } finally {
        setLeadDetailLoading(false);
      }
    },
    [current],
  );

  const changeLeadStage = useCallback(
    async (stage: string) => {
      if (!current || !selectedLeadId || stageBusy) return;
      setStageBusy(true);
      try {
        await api(`/api/workspaces/${current}/leads/${selectedLeadId}`, {
          method: "PATCH",
          body: JSON.stringify({ stage }),
        });
        await loadLeadDetail(selectedLeadId);
        const [m, l] = await Promise.all([
          api<Metrics>(`/api/workspaces/${current}/metrics`),
          api<Lead[]>(`/api/workspaces/${current}/leads?limit=80`),
        ]);
        setMetrics(m);
        setLeads(l);
      } catch (e) {
        alert("Falha ao mudar estágio: " + ((e as Error).message || e));
      } finally {
        setStageBusy(false);
      }
    },
    [current, selectedLeadId, stageBusy, loadLeadDetail],
  );

  const togglePause = useCallback(async () => {
    if (!current || !selectedLeadId || pauseBusy || !leadDetail) return;
    const next = !leadDetail.lead.agent_paused;
    setPauseBusy(true);
    try {
      await api(`/api/workspaces/${current}/leads/${selectedLeadId}/pause`, {
        method: "POST",
        body: JSON.stringify({
          paused: next,
          reason: next ? "humano assumiu no console" : "agente retomado",
        }),
      });
      await loadLeadDetail(selectedLeadId);
    } catch (e) {
      alert("Falha ao alterar pausa: " + ((e as Error).message || e));
    } finally {
      setPauseBusy(false);
    }
  }, [current, selectedLeadId, pauseBusy, leadDetail, loadLeadDetail]);

  const submitNote = useCallback(async () => {
    if (!current || !selectedLeadId || noteBusy) return;
    const n = noteText.trim();
    if (!n) return;
    setNoteBusy(true);
    try {
      await api(`/api/workspaces/${current}/leads/${selectedLeadId}/notes`, {
        method: "POST",
        body: JSON.stringify({ note: n }),
      });
      setNoteText("");
      await loadLeadDetail(selectedLeadId);
    } catch (e) {
      alert("Falha ao salvar nota: " + ((e as Error).message || e));
    } finally {
      setNoteBusy(false);
    }
  }, [current, selectedLeadId, noteBusy, noteText, loadLeadDetail]);

  useEffect(() => {
    if (!authed) return;
    loadWorkspaces().catch(() => setAuthed(false));
  }, [authed, loadWorkspaces]);

  useEffect(() => {
    if (current) selectWorkspace(current);
  }, [current, selectWorkspace]);

  useEffect(() => {
    if (tab === "learning") loadLearning();
  }, [tab, loadLearning]);

  useEffect(() => {
    if (leadDetail && !leadDetailLoading) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [leadDetail, leadDetailLoading]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && selectedLeadId) {
        setSelectedLeadId(null);
        setLeadDetail(null);
        setLeadDetailErr("");
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedLeadId]);

  const filteredLeads = useMemo(() => {
    const q = leadFilter.trim().toLowerCase();
    return leads.filter((l) => {
      if (stageFilter !== "all" && (l.stage || "") !== stageFilter) return false;
      if (!q) return true;
      const hay = `${l.phone || ""} ${l.name || ""} ${l.company || ""}`.toLowerCase();
      return hay.includes(q);
    });
  }, [leads, leadFilter, stageFilter]);

  const doLogin = async () => {
    setGateErr("");
    if (!usernameInput.trim() || !passwordInput) {
      setGateErr("Informe usuário e senha.");
      return;
    }
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: usernameInput.trim(),
          password: passwordInput,
        }),
      });
      if (!res.ok) throw new Error("fail");
      const data = (await res.json()) as { access_token: string };
      setToken(data.access_token);
      setPasswordInput("");
      setAuthed(true);
    } catch {
      setGateErr("Falha no login. Verifique usuário/senha.");
    }
  };

  if (!authed) {
    return (
      <div className="overlay">
        <div className="modal">
          <h3>Acesso ao console</h3>
          <p>Entre com o usuário admin (JWT).</p>
          <div className="field">
            <label>Usuário</label>
            <input
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              placeholder="admin"
              autoComplete="username"
            />
          </div>
          <div className="field">
            <label>Senha</label>
            <input
              type="password"
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void doLogin();
              }}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>
          <button className="btn btn-primary" style={{ width: "100%" }} onClick={() => void doLogin()}>
            Entrar
          </button>
          <div className="err">{gateErr}</div>
        </div>
      </div>
    );
  }

  const maxStage = Math.max(1, ...STAGE_ORDER.map((s) => metrics?.by_stage?.[s] || 0));
  const activePipe =
    (metrics?.by_stage?.qualified || 0) + (metrics?.by_stage?.closer || 0);

  const detailLead = leadDetail?.lead;
  const wa = waLink(detailLead?.phone);

  return (
    <div className="shell">
      <div className="bg-layer" />
      <div className="bg-grid" />
      <div className="layout">
        <aside className="rail fade-in">
          <div className="brand">
            <div className="mark">F</div>
            <div className="name">
              Force<span>IA</span>
            </div>
          </div>
          <div className="status">
            <span className="pulse" /> Console online
          </div>
          <div>
            <div className="label">Workspaces</div>
            <div className="ws-list">
              {!workspaces.length ? (
                <div className="empty" style={{ textAlign: "left", padding: "8px 0" }}>
                  Nenhum ainda
                </div>
              ) : (
                workspaces.map((w) => (
                  <button
                    key={w.slug}
                    type="button"
                    className={"ws-item" + (w.slug === current ? " active" : "")}
                    onClick={() => setCurrent(w.slug)}
                  >
                    <span>{w.name}</span>
                    <span className="slug">{w.slug}</span>
                  </button>
                ))
              )}
            </div>
          </div>
          <div className="rail-foot">
            <button
              className="btn btn-primary"
              onClick={() => {
                setWsOpen(true);
                setWsKey(null);
                setWsErr("");
              }}
            >
              + Novo workspace
            </button>
            <button
              className="btn btn-ghost"
              onClick={() => {
                clearToken();
                setAuthed(false);
              }}
            >
              Sair
            </button>
          </div>
        </aside>

        <section className="main">
          <div className="top fade-in">
            <div>
              <h1>{current || "Selecione um workspace"}</h1>
              <div className="sub">{sub}</div>
            </div>
            <div className="top-actions">
              <button className="btn" disabled={!current} onClick={() => current && selectWorkspace(current)}>
                Atualizar
              </button>
              <button
                className="btn btn-accent"
                disabled={!current || learnBusy}
                onClick={async () => {
                  if (!current) return;
                  setLearnBusy(true);
                  try {
                    await api(`/api/learning/run/${current}?per_outcome=8`, { method: "POST" });
                    setTab("learning");
                    await loadLearning();
                  } catch (e) {
                    alert("Learning falhou: " + ((e as Error).message || e));
                  } finally {
                    setLearnBusy(false);
                  }
                }}
              >
                {learnBusy ? "Rodando…" : "Rodar learning"}
              </button>
            </div>
          </div>

          <div className="marquee-wrap">
            <div className="marquee">
              {[0, 1].map((i) => (
                <span key={i}>
                  <b>SDR</b> qualifica · <b>Closer</b> fecha · <b>Follow-up</b> reativa · LangGraph · Langfuse · BANT · META
                </span>
              ))}
            </div>
          </div>

          <div className="tabs">
            {(
              [
                ["overview", "Overview"],
                ["leads", "Leads"],
                ["events", "Eventos"],
                ["playbook", "Playbook"],
                ["learning", "Learning"],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={"tab" + (tab === id ? " active" : "")}
                onClick={() => setTab(id as Tab)}
              >
                {label}
              </button>
            ))}
          </div>

          {tab === "overview" && (
            <div className="bento">
              <div className="card kpi">
                <h2>Leads totais</h2>
                <div className="val">{metrics?.total ?? "—"}</div>
                <div className="hint">No workspace atual</div>
              </div>
              <div className="card kpi">
                <h2>Win rate</h2>
                <div className="val">
                  {metrics ? Math.round((metrics.win_rate || 0) * 100) : "—"}
                  <small>%</small>
                </div>
                <div className="hint">Won / (won + lost)</div>
              </div>
              <div className="card kpi">
                <h2>Em pipeline</h2>
                <div className="val">{metrics ? activePipe : "—"}</div>
                <div className="hint">Qualified + Closer</div>
              </div>
              <div className="card funnel-card">
                <h2>Funil por estágio</h2>
                {!metrics ? (
                  <div className="empty">Sem dados</div>
                ) : (
                  STAGE_ORDER.map((stage) => {
                    const count = metrics.by_stage?.[stage] || 0;
                    return (
                      <div className="stage-row" key={stage}>
                        <div className="stage-name">{stage}</div>
                        <div className="bar-track">
                          <div
                            className="bar-fill"
                            style={{
                              width: `${(count / maxStage) * 100}%`,
                              background: STAGE_COLORS[stage],
                            }}
                          />
                        </div>
                        <div className="stage-count">{count}</div>
                      </div>
                    );
                  })
                )}
              </div>
              <div className="card events-card">
                <h2>Eventos recentes</h2>
                <EventList events={events} />
              </div>
            </div>
          )}

          {tab === "leads" && (
            <div className="card full">
              <h2>Leads</h2>
              <p className="sub">Abra o console completo para o detalhe de leads (layout preservado no build).</p>
              <div className="empty">{leads.length} leads no workspace</div>
            </div>
          )}

          {tab === "events" && (
            <div className="card full">
              <h2>Timeline de eventos</h2>
              <EventList events={events} />
            </div>
          )}

          {tab === "playbook" && <PlaybookPanel workspace={current} />}

          {tab === "learning" && (
            <div className="card full">
              <h2>Sugestões de prompt (pending)</h2>
              {!suggestions.length ? (
                <div className="empty">Nenhuma sugestão pending</div>
              ) : (
                suggestions.map((r) => (
                  <div className="sug" key={r.id}>
                    <div>
                      <div className="title">{r.title || r.agent || "Sugestão"}</div>
                      <div className="meta">
                        {r.agent || ""} · {(r.rationale || "").slice(0, 120)}
                      </div>
                    </div>
                    <div className="actions">
                      <button
                        className="btn btn-accent"
                        onClick={async () => {
                          await api(`/api/learning/suggestions/${r.id}/apply`, { method: "POST" });
                          loadLearning();
                        }}
                      >
                        Aplicar
                      </button>
                      <button
                        className="btn btn-ghost"
                        onClick={async () => {
                          await api(`/api/learning/suggestions/${r.id}/reject`, {
                            method: "POST",
                            body: "{}",
                          });
                          loadLearning();
                        }}
                      >
                        Rejeitar
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </section>
      </div>

      {wsOpen && (
        <div className="overlay">
          <div className="modal">
            <h3>Novo workspace</h3>
            <p>Cliente isolado — leads, mensagens e eventos próprios.</p>
            <div className="field">
              <label>Nome</label>
              <input value={wsName} onChange={(e) => setWsName(e.target.value)} placeholder="Clínica Sol" />
            </div>
            <div className="field">
              <label>Slug</label>
              <input value={wsSlug} onChange={(e) => setWsSlug(e.target.value)} placeholder="clinica-sol" />
            </div>
            <div className="field">
              <label>Instância Evolution (opcional)</label>
              <input value={wsInst} onChange={(e) => setWsInst(e.target.value)} placeholder="clinica-sol-wa" />
            </div>
            {wsKey && (
              <div>
                <label style={{ fontFamily: "var(--mono)", fontSize: "10.5px", letterSpacing: ".1em", textTransform: "uppercase", color: "var(--muted)" }}>
                  API key (guarde agora)
                </label>
                <div className="keybox">{wsKey}</div>
              </div>
            )}
            <div className="err">{wsErr}</div>
            <div className="row">
              <button
                className="btn btn-primary"
                onClick={async () => {
                  setWsErr("");
                  if (!wsName.trim() || !wsSlug.trim()) {
                    setWsErr("Nome e slug são obrigatórios.");
                    return;
                  }
                  try {
                    const r = await api<{ api_key: string }>("/api/workspaces", {
                      method: "POST",
                      body: JSON.stringify({
                        name: wsName.trim(),
                        slug: wsSlug.trim(),
                        instance: wsInst.trim() || null,
                      }),
                    });
                    setWsKey(r.api_key);
                    await loadWorkspaces();
                  } catch (e) {
                    const msg = String((e as Error).message || e);
                    setWsErr(msg.includes("409") ? "Slug já existe." : "Erro ao criar workspace.");
                  }
                }}
              >
                Criar
              </button>
              <button className="btn btn-ghost" onClick={() => setWsOpen(false)}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EventList({ events }: { events: EventRow[] }) {
  if (!events.length) return <div className="empty">Sem eventos</div>;
  return (
    <>
      {events.map((e, i) => (
        <div className="ev" key={`${e.type}-${e.created_at}-${i}`}>
          <div className="dot" />
          <div>
            <div className="etype">{e.type || ""}</div>
            <div className="meta">{fmtDate(e.created_at)}</div>
          </div>
        </div>
      ))}
    </>
  );
}
