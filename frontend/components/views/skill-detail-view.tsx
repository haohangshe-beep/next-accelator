"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Frame } from "@/components/site-header";
import { CodeList, ErrorBlock, LoadingLine, PageIntro, SuccessBlock, TrackBadge } from "@/components/ui";
import { api, errorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { CompletionResult, ModuleDetail } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

function routeCode(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return (raw ?? "").toUpperCase();
}

export function SkillDetailView() {
  const params = useParams<{ code: string }>();
  const code = routeCode(params.code);
  usePageTitle(code || "Skill");
  const auth = useAuth();
  const moduleState = useApi<ModuleDetail>(code ? `/modules/${code}` : null);
  const [checked, setChecked] = useState<boolean[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!moduleState.data) {
      return;
    }
    setChecked(moduleState.data.checklist.map(() => moduleState.data?.completed ?? false));
  }, [moduleState.data]);

  const module = moduleState.data;

  async function complete() {
    if (!auth.token || !module) {
      return;
    }
    setPending(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await api<CompletionResult>(`/modules/${module.code}/complete`, {
        token: auth.token,
        body: { checked },
      });
      setSuccess(
        result.already_completed
          ? `${result.title} was already on your passport.`
          : `${result.title} is now on your Skills Passport.`,
      );
      await moduleState.reload();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <Frame>
      {moduleState.loading ? <LoadingLine label="Loading module…" /> : null}
      {moduleState.error ? <ErrorBlock message={moduleState.error} /> : null}
      {module ? (
        <>
          <PageIntro kicker={module.code} title={module.title} lede={module.summary} />
          <div className="meta-row">
            <TrackBadge track={module.track} />
            <span>{module.level}</span>
            <span>{module.estimated_hours} hours</span>
            {module.completed ? <span>Recorded {formatDate(module.completed_at)}</span> : null}
          </div>
          <section className="section-block">
            <h2>Learning outcomes</h2>
            <ul>
              {module.learning_outcomes.map((outcome) => (
                <li key={outcome}>{outcome}</li>
              ))}
            </ul>
          </section>
          <section className="section-block">
            <h2>Prerequisites</h2>
            {module.prerequisites.length ? (
              <CodeList codes={module.prerequisites} />
            ) : (
              <p>No prerequisites. You can record this module as soon as the self-check is honest.</p>
            )}
            {module.missing_prerequisites.length ? (
              <p className="callout">
                Complete {module.missing_prerequisites.join(", ")} before this module can be recorded.
              </p>
            ) : null}
          </section>
          <section className="section-block">
            <h2>Self-check</h2>
            <fieldset className="checklist" disabled={module.completed || pending}>
              <legend>Confirm each statement to record the module</legend>
              {module.checklist.map((item, index) => (
                <label key={item} className="check">
                  <input
                    type="checkbox"
                    checked={checked[index] ?? false}
                    onChange={(event) => {
                      const next = [...checked];
                      next[index] = event.target.checked;
                      setChecked(next);
                    }}
                  />
                  <span>{item}</span>
                </label>
              ))}
            </fieldset>
            {error ? <ErrorBlock message={error} /> : null}
            {success ? <SuccessBlock message={success} /> : null}
            <div className="form-actions">
              {auth.user?.role === "learner" ? (
                <button
                  className="button"
                  type="button"
                  disabled={
                    pending ||
                    module.completed ||
                    module.missing_prerequisites.length > 0 ||
                    checked.length !== module.checklist.length ||
                    checked.some((item) => !item)
                  }
                  onClick={() => void complete()}
                >
                  {module.completed ? "On your passport" : "Record on passport"}
                </button>
              ) : (
                <Link className="button" href={`/login?next=/skills/${module.code}`}>
                  Sign in as a learner to record this
                </Link>
              )}
              {module.completed && auth.user ? (
                <Link className="button secondary" href={`/passport/${auth.user.slug}`}>
                  View passport
                </Link>
              ) : null}
              <Link className="button secondary" href={`/missions?skill=${module.code}`}>
                Missions that require {module.code}
              </Link>
            </div>
          </section>
        </>
      ) : null}
    </Frame>
  );
}
