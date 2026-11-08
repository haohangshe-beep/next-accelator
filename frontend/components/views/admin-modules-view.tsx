"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { Frame } from "@/components/site-header";
import { RequireAuth } from "@/components/require-auth";
import { ErrorBlock, Field, LoadingLine, PageIntro, SuccessBlock, TrackBadge } from "@/components/ui";
import { api, errorMessage, lines } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { ModuleDetail, ModuleSummary, Role } from "@/lib/types";
import { LEVELS, TRACKS } from "@/lib/tracks";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

const ADMIN: readonly Role[] = ["admin"];

type Draft = {
  code: string;
  title: string;
  track: string;
  level: string;
  summary: string;
  outcomes: string;
  hours: string;
  prerequisites: string[];
  checklist: string;
};

const EMPTY: Draft = {
  code: "",
  title: "",
  track: "AI",
  level: "Foundation",
  summary: "",
  outcomes: "",
  hours: "6",
  prerequisites: [],
  checklist: "",
};

export function AdminModulesView() {
  usePageTitle("Module admin");
  return (
    <Frame>
      <RequireAuth roles={ADMIN}>
        <AdminBody />
      </RequireAuth>
    </Frame>
  );
}

function AdminBody() {
  const auth = useAuth();
  const modules = useApi<ModuleSummary[]>("/modules");
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [editing, setEditing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function update<K extends keyof Draft>(key: K, value: Draft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function togglePrereq(code: string) {
    setDraft((current) => ({
      ...current,
      prerequisites: current.prerequisites.includes(code)
        ? current.prerequisites.filter((item) => item !== code)
        : [...current.prerequisites, code],
    }));
  }

  async function startEdit(code: string) {
    if (!auth.token) {
      return;
    }
    setError(null);
    setSuccess(null);
    try {
      const detail = await api<ModuleDetail>(`/modules/${code}`, { token: auth.token });
      setEditing(detail.code);
      setDraft({
        code: detail.code,
        title: detail.title,
        track: detail.track,
        level: detail.level,
        summary: detail.summary,
        outcomes: detail.learning_outcomes.join("\n"),
        hours: String(detail.estimated_hours),
        prerequisites: detail.prerequisites,
        checklist: detail.checklist.join("\n"),
      });
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!auth.token) {
      return;
    }
    setPending(true);
    setError(null);
    setSuccess(null);
    const payload = {
      title: draft.title,
      track: draft.track,
      level: draft.level,
      summary: draft.summary,
      learning_outcomes: lines(draft.outcomes),
      estimated_hours: Number(draft.hours),
      prerequisites: draft.prerequisites,
      checklist: lines(draft.checklist),
    };
    try {
      if (editing) {
        await api<ModuleDetail>(`/admin/modules/${editing}`, {
          method: "PUT",
          token: auth.token,
          body: payload,
        });
        setSuccess(`${editing} updated.`);
      } else {
        const created = await api<ModuleDetail>("/admin/modules", {
          token: auth.token,
          body: { ...payload, code: draft.code },
        });
        setSuccess(`${created.code} added to the catalogue.`);
      }
      setDraft(EMPTY);
      setEditing(null);
      await modules.reload();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  async function remove(code: string) {
    if (!auth.token || !window.confirm(`Remove ${code} from the catalogue?`)) {
      return;
    }
    setError(null);
    setSuccess(null);
    try {
      await api(`/admin/modules/${code}`, { method: "DELETE", token: auth.token });
      if (editing === code) {
        setEditing(null);
        setDraft(EMPTY);
      }
      setSuccess(`${code} removed.`);
      await modules.reload();
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  return (
    <>
      <PageIntro
        kicker="Admin"
        title="Skill modules"
        lede="Create the catalogue learners record onto their passports. Codes stay fixed after you save them."
      />
      <form className="card form" onSubmit={(event) => void save(event)}>
        <h2>{editing ? `Edit ${editing}` : "New module"}</h2>
        <Field id="module-code" label="Code" hint="Letters then three digits, such as AI103.">
          <input
            id="module-code"
            value={draft.code}
            onChange={(event) => update("code", event.target.value.toUpperCase())}
            disabled={editing !== null}
            required
          />
        </Field>
        <Field id="module-title" label="Title">
          <input id="module-title" value={draft.title} onChange={(event) => update("title", event.target.value)} required />
        </Field>
        <div className="split tight">
          <Field id="module-track" label="Track">
            <select id="module-track" value={draft.track} onChange={(event) => update("track", event.target.value)}>
              {TRACKS.map((track) => (
                <option key={track.code} value={track.code}>
                  {track.label}
                </option>
              ))}
            </select>
          </Field>
          <Field id="module-level" label="Level">
            <select id="module-level" value={draft.level} onChange={(event) => update("level", event.target.value)}>
              {LEVELS.map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </Field>
          <Field id="module-hours" label="Estimated hours">
            <input
              id="module-hours"
              type="number"
              min={1}
              max={80}
              value={draft.hours}
              onChange={(event) => update("hours", event.target.value)}
              required
            />
          </Field>
        </div>
        <Field id="module-summary" label="Summary">
          <textarea id="module-summary" rows={3} value={draft.summary} onChange={(event) => update("summary", event.target.value)} required />
        </Field>
        <Field id="module-outcomes" label="Learning outcomes" hint="One outcome per line.">
          <textarea
            id="module-outcomes"
            rows={4}
            value={draft.outcomes}
            onChange={(event) => update("outcomes", event.target.value)}
            required
          />
        </Field>
        <Field id="module-checklist" label="Self-check" hint="One statement per line. Learners must confirm every line.">
          <textarea
            id="module-checklist"
            rows={4}
            value={draft.checklist}
            onChange={(event) => update("checklist", event.target.value)}
            required
          />
        </Field>
        <fieldset className="checklist">
          <legend>Prerequisites</legend>
          {(modules.data ?? [])
            .filter((module) => module.code !== (editing ?? draft.code.toUpperCase()))
            .map((module) => (
              <label key={module.code} className="check">
                <input
                  type="checkbox"
                  checked={draft.prerequisites.includes(module.code)}
                  onChange={() => togglePrereq(module.code)}
                />
                <span>
                  {module.code} · {module.title}
                </span>
              </label>
            ))}
        </fieldset>
        {error ? <ErrorBlock message={error} /> : null}
        {success ? <SuccessBlock message={success} /> : null}
        <div className="form-actions">
          <button className="button" type="submit" disabled={pending}>
            {pending ? "Saving…" : editing ? `Save ${editing}` : "Add module"}
          </button>
          {editing ? (
            <button
              className="button secondary"
              type="button"
              onClick={() => {
                setEditing(null);
                setDraft(EMPTY);
              }}
            >
              Cancel edit
            </button>
          ) : null}
        </div>
      </form>
      {modules.loading ? <LoadingLine label="Loading catalogue…" /> : null}
      <ul className="stack">
        {(modules.data ?? []).map((module) => (
          <li key={module.code} className="card compact row-card">
            <div>
              <TrackBadge track={module.track} />
              <h3>
                {module.code} · {module.title}
              </h3>
              <p className="meta">
                {module.level} · {module.estimated_hours} hours
                {module.prerequisites.length ? ` · after ${module.prerequisites.join(", ")}` : ""}
              </p>
            </div>
            <div className="actions">
              <button className="button secondary" type="button" onClick={() => void startEdit(module.code)}>
                Edit
              </button>
              <button className="button danger" type="button" onClick={() => void remove(module.code)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
