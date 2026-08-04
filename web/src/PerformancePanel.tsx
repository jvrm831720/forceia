import { useCallback, useEffect, useState } from "react";

const TOKEN_KEY = "forceia_admin_token";

type PerfBlock = { total?: number; ai?: number; human?: number; ai_share?: number };
type Performance = {
  headline?: string;
  period_label?: string;
  meetings?: PerfBlock;
  qualified?: PerfBlock;
  won?: PerfBlock;
  proposals?: { total?: number; ai?: number; human?: number };
  activity?: {
    messages_processed?: number;
    handoffs?: number;
    human_takeovers?: number;
  };
  comparison?: {
    ai_vs_human_meetings?: number;
    ai_vs_human_qualified?: number;
    ai_vs_human_won?: number;
  };
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

function ShareBar({ ai = 0, human = 0 }: { ai?: number; human?: number }) {
  const total = Math.max(1, ai + human);
  const aiPct = Math.round((ai / total) * 100);
  return (
    <div className="share-bar">
      <div className="share-ai" style={{ width: `${aiPct}%` }} title={`IA ${ai}`} />
      <div className="share-human" style={{ width: `${100 - aiPct}%` }} title={`Humano ${human}`} />
    </div>
  );
}

export default function PerformancePanel({
  workspace,
  compact = false,
}: {
  workspace: string | null;
  compact?: boolean;
}) {
  const [period, setPeriod] = useState("week");
  const [data, setData] = useState<Performance | null>(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [reportPreview, setReportPreview] = useState("");
  const [reportMsg, setReportMsg] = useState("");
  const [ownerPhone, setOwnerPhone] = useState("");

  const load = useCallback(async () => {
    if (!workspace) return;
    setBusy(true);
    setErr("");
    try {
      const p = await api<Performance>(
        `/api/workspaces/${workspace}/performance?period=${period}`,
      );
      setData(p);
    } catch (e) {
      setErr((e as Error).message || "Falha ao carregar performance");
      setData(null);
    } finally {
      setBusy(false);
    }
  }, [workspace, period]);

  useEffect(() => {
    void load();
  }, [load]);

  const previewReport = async () => {
    if (!workspace) return;
    setReportMsg("");
    try {
      const r = await api<{ text?: string }>(
        `/api/workspaces/${workspace}/reports/preview?period=${period}`,
      );
      setReportPreview(r.text || "");
    } catch (e) {
      setReportMsg("Erro no preview: " + ((e as Error).message || e));
    }
  };

  const sendReport = async () => {
    if (!workspace) return;
    setReportMsg("");
    try {
      const r = await api<{ sent?: boolean; message?: string; error?: string }>(
        `/api/workspaces/${workspace}/reports/send`,
        {
          method: "POST",
          body: JSON.stringify({
            period,
            phone: ownerPhone.trim() || null,
            dry_run: false,
          }),
        },
      );
      setReportMsg(r.sent ? "Relatório enviado no WhatsApp do dono." : r.message || r.error || "Não enviado");
    } catch (e) {
      setReportMsg("Falha ao enviar: " + ((e as Error).message || e));
    }
  };

  const savePhone = async () => {
    if (!workspace || !ownerPhone.trim()) return;
    try {
      await api(`/api/workspaces/${workspace}/owner-phone`, {
        method: "PUT",
        body: JSON.stringify({ phone: ownerPhone.trim() }),
      });
      setReportMsg("Telefone do dono salvo.");
    } catch (e) {
      setReportMsg("Erro ao salvar telefone: " + ((e as Error).message || e));
    }
  };

  if (!workspace) return <div className="empty">Selecione um workspace</div>;

  if (compact && data) {
    return (
      <div className="perf-compact">
        <div className="perf-headline">{data.headline || "—"}</div>
        <div className="perf-mini-row">
          <span>
            Reuniões IA <b>{data.meetings?.ai ?? 0}</b>
          </span>
          <span>
            Humano <b>{data.meetings?.human ?? 0}</b>
          </span>
          <span>
            Qualificados IA <b>{data.qualified?.ai ?? 0}</b>
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="product-stack">
      <div className="card full">
        <div className="panel-toolbar">
          <h2>Performance do time</h2>
          <div className="toolbar-actions">
            <select
              className="filter-select"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="day">Hoje</option>
              <option value="week">Esta semana</option>
              <option value="month">Este mês</option>
            </select>
            <button className="btn" disabled={busy} onClick={() => void load()}>
              Atualizar
            </button>
          </div>
        </div>
        {err && <div className="err">{err}</div>}
        {busy && !data && <div className="empty">Carregando…</div>}
        {data && (
          <>
            <div className="headline-banner">{data.headline}</div>
            <div className="perf-grid">
              <div className="perf-card">
                <div className="perf-label">Reuniões</div>
                <div className="perf-val">{data.meetings?.total ?? 0}</div>
                <ShareBar ai={data.meetings?.ai} human={data.meetings?.human} />
                <div className="perf-split">
                  <span className="ai-tag">IA {data.meetings?.ai ?? 0}</span>
                  <span className="human-tag">Humano {data.meetings?.human ?? 0}</span>
                </div>
              </div>
              <div className="perf-card">
                <div className="perf-label">Qualificações</div>
                <div className="perf-val">{data.qualified?.total ?? 0}</div>
                <ShareBar ai={data.qualified?.ai} human={data.qualified?.human} />
                <div className="perf-split">
                  <span className="ai-tag">IA {data.qualified?.ai ?? 0}</span>
                  <span className="human-tag">Humano {data.qualified?.human ?? 0}</span>
                </div>
              </div>
              <div className="perf-card">
                <div className="perf-label">Fechamentos</div>
                <div className="perf-val">{data.won?.total ?? 0}</div>
                <ShareBar ai={data.won?.ai} human={data.won?.human} />
                <div className="perf-split">
                  <span className="ai-tag">IA {data.won?.ai ?? 0}</span>
                  <span className="human-tag">Humano {data.won?.human ?? 0}</span>
                </div>
              </div>
            </div>
            <div className="activity-row">
              <span>Msgs processadas: {data.activity?.messages_processed ?? 0}</span>
              <span>Handoffs: {data.activity?.handoffs ?? 0}</span>
              <span>Takeovers: {data.activity?.human_takeovers ?? 0}</span>
            </div>
          </>
        )}
      </div>

      <div className="card full">
        <h2>Relatório no WhatsApp do dono</h2>
        <p className="panel-desc">
          Envie o resumo da performance para o celular do dono do negócio.
        </p>
        <div className="field">
          <label>WhatsApp do dono (com DDI)</label>
          <input
            value={ownerPhone}
            onChange={(e) => setOwnerPhone(e.target.value)}
            placeholder="5511999998888"
          />
        </div>
        <div className="row">
          <button className="btn" onClick={() => void savePhone()}>
            Salvar telefone
          </button>
          <button className="btn" onClick={() => void previewReport()}>
            Preview
          </button>
          <button className="btn btn-primary" onClick={() => void sendReport()}>
            Enviar no WhatsApp
          </button>
        </div>
        {reportMsg && <div className="ops-hint" style={{ marginTop: 10 }}>{reportMsg}</div>}
        {reportPreview && (
          <pre className="report-preview">{reportPreview}</pre>
        )}
      </div>
    </div>
  );
}
