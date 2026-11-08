"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import { Frame } from "@/components/site-header";
import { RequireAuth } from "@/components/require-auth";
import { ErrorBlock, Field, LoadingLine, PageIntro } from "@/components/ui";
import { api, errorMessage, lines } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { MissionDetail, ModuleSummary, Role } from "@/lib/types";
import { DIFFICULTIES, TRACKS } from "@/lib/tracks";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

const EMPLOYER: readonly Role[] = ["employer"];

export function MissionNewView() {
  usePageTitle("Publish a mission");
  return (
    <Frame>
      <RequireAuth roles={EMPLOYER}>
        <MissionForm />
      </RequireAuth>
    </Frame>
  );
}

function MissionForm() {
  const auth = useAuth();
  const router = useRouter();
  const modules = useApi<ModuleSummary[]>("/modules");
  const [title, setTitle] = useState("");
  const [track, setTrack] = useState("AI");
  const [difficulty, setDifficulty] = useState("Introductory");
  const [summary, setSummary] = useState("");
  const [problem, setProblem] = useState("");
  const [deliverables, setDeliverables] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [competencies, setCompetencies] = useState("");
  const [deadline, setDeadline] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function toggleSkill(code: string) {
    setSkills((current) => (current.includes(code) ? current.filter((item) => item !== code) : [...current, code]));
  }

  async function publish(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!auth.token) {
      return;
    }
    setPending(true);
    setError(null);
    try {
      const created = await api<MissionDetail>("/missions", {
        token: auth.token,
        body: {
          title,
          track,
          difficulty,
          summary,
          problem_statement: problem,
          deliverables,
          required_skill_codes: skills,
          suggested_competencies: lines(competencies),
          deadline: deadline || null,
        },
      });
      router.push(`/missions/${created.id}`);
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <>
      <PageIntro
        kicker={auth.user?.organization?.name ?? "Employer"}
        title="Publish a mission"
        lede="Write the problem, the evidence you want, and the modules a learner must already have. It appears on the marketplace immediately."
      />
      {modules.loading ? <LoadingLine label="Loading skill codes…" /> : null}
      <form className="card form" onSubmit={(event) => void publish(event)}>
        <Field id="mission-title" label="Title">
          <input id="mission-title" value={title} onChange={(event) => setTitle(event.target.value)} required />
        </Field>
        <div className="split tight">
          <Field id="mission-track" label="Track">
            <select id="mission-track" value={track} onChange={(event) => setTrack(event.target.value)}>
              {TRACKS.map((item) => (
                <option key={item.code} value={item.code}>
                  {item.label}
                </option>
              ))}
            </select>
          </Field>
          <Field id="mission-difficulty" label="Difficulty">
            <select
              id="mission-difficulty"
              value={difficulty}
              onChange={(event) => setDifficulty(event.target.value)}
            >
              {DIFFICULTIES.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <Field id="mission-summary" label="Summary">
          <textarea id="mission-summary" rows={3} value={summary} onChange={(event) => setSummary(event.target.value)} required />
        </Field>
        <Field id="mission-problem" label="Problem statement">
          <textarea id="mission-problem" rows={5} value={problem} onChange={(event) => setProblem(event.target.value)} required />
        </Field>
        <Field id="mission-deliverables" label="Deliverables" hint="Tell the learner exactly what URL you will open.">
          <textarea
            id="mission-deliverables"
            rows={4}
            value={deliverables}
            onChange={(event) => setDeliverables(event.target.value)}
            required
          />
        </Field>
        <fieldset className="checklist">
          <legend>Required skill codes</legend>
          {(modules.data ?? []).map((module) => (
            <label key={module.code} className="check">
              <input
                type="checkbox"
                checked={skills.includes(module.code)}
                onChange={() => toggleSkill(module.code)}
              />
              <span>
                {module.code} · {module.title}
              </span>
            </label>
          ))}
        </fieldset>
        <Field id="mission-tags" label="Suggested competency tags" hint="One tag per line. You can still add others at review time.">
          <textarea
            id="mission-tags"
            rows={4}
            value={competencies}
            onChange={(event) => setCompetencies(event.target.value)}
          />
        </Field>
        <Field id="mission-deadline" label="Deadline" hint="Optional.">
          <input id="mission-deadline" type="date" value={deadline} onChange={(event) => setDeadline(event.target.value)} />
        </Field>
        {error ? <ErrorBlock message={error} /> : null}
        <div className="form-actions">
          <button className="button" type="submit" disabled={pending}>
            {pending ? "Publishing…" : "Publish mission"}
          </button>
        </div>
      </form>
    </>
  );
}
