"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { Frame } from "@/components/site-header";
import { RequireAuth } from "@/components/require-auth";
import { ErrorBlock, LoadingLine, PageIntro, StatusPill, SuccessBlock, TrackBadge } from "@/components/ui";
import { api, errorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { ReviewResult, Role, Submission } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

const REVIEWERS: readonly Role[] = ["learner", "employer", "admin"];

function routeId(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw ?? "";
}

export function SubmissionView() {
  const params = useParams<{ id: string }>();
  const id = routeId(params.id);
  usePageTitle("Submission");
  return (
    <Frame>
      <RequireAuth roles={REVIEWERS}>
        <SubmissionBody id={id} />
      </RequireAuth>
    </Frame>
  );
}

function SubmissionBody({ id }: { id: string }) {
  const auth = useAuth();
  const numeric = /^\d+$/.test(id);
  const submissionState = useApi<Submission>(numeric && auth.token ? `/submissions/${id}` : null);
  const submission = submissionState.data;
  const [selected, setSelected] = useState<string[]>([]);
  const [custom, setCustom] = useState("");
  const [feedback, setFeedback] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  function toggle(tag: string) {
    setSelected((current) => (current.includes(tag) ? current.filter((item) => item !== tag) : [...current, tag]));
  }

  function addCustom() {
    const tag = custom.trim();
    if (tag.length < 2) {
      return;
    }
    setSelected((current) => (current.includes(tag) ? current : [...current, tag]));
    setCustom("");
  }

  async function review(action: "approve" | "request_changes") {
    if (!auth.token || !submission) {
      return;
    }
    setPending(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await api<ReviewResult>(`/submissions/${submission.id}/review`, {
        token: auth.token,
        body: {
          action,
          competency_tags: selected,
          feedback,
        },
      });
      submissionState.setData(result.submission);
      setSuccess(
        result.certification
          ? "Certification issued. It is now on the learner's Skills Passport."
          : "Changes requested. The learner can revise and submit again.",
      );
      setFeedback("");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  if (!numeric) {
    return <ErrorBlock message="That submission link is not valid." />;
  }
  if (submissionState.loading || !submission) {
    return submissionState.error ? (
      <ErrorBlock message={submissionState.error} />
    ) : (
      <LoadingLine label="Loading submission…" />
    );
  }

  const suggestions = Array.from(new Set([...submission.suggested_competencies, ...selected]));

  return (
    <>
      <PageIntro
        kicker={submission.organization_name}
        title={submission.mission_title}
        lede={`${submission.learner_name} submitted evidence on ${formatDate(submission.created_at)}.`}
      />
      <div className="meta-row">
        <TrackBadge track={submission.mission_track} />
        <StatusPill status={submission.status} />
      </div>
      <section className="card section-block">
        <h2>Evidence</h2>
        <p>
          <a href={submission.deliverable_url} target="_blank" rel="noreferrer">
            {submission.deliverable_url}
          </a>
        </p>
        <p>{submission.notes}</p>
        {submission.feedback ? <p className="callout">Reviewer note: {submission.feedback}</p> : null}
        <div className="actions">
          <Link className="button secondary" href={`/missions/${submission.mission_id}`}>
            Mission brief
          </Link>
          <Link className="button secondary" href={`/passport/${submission.learner_slug}`}>
            {submission.learner_name}'s passport
          </Link>
        </div>
      </section>
      {submission.certification ? (
        <article className="stamp">
          <p className="kicker">Certified</p>
          <p>{submission.certification.statement}</p>
          <p className="meta">
            Issued by {submission.certification.issuer_name} · {formatDate(submission.certification.issued_at)}
          </p>
          <ul className="tag-row">
            {submission.certification.competency_tags.map((tag) => (
              <li key={tag} className="tag">
                {tag}
              </li>
            ))}
          </ul>
        </article>
      ) : null}
      {submission.can_review && submission.status !== "approved" ? (
        <section className="card form">
          <h2>Certify or send it back</h2>
          <p>Choose at least one competency. The tags are what appear on the public passport.</p>
          <fieldset className="checklist">
            <legend>Competencies</legend>
            <div className="tag-row">
              {suggestions.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  className={selected.includes(tag) ? "tag on" : "tag"}
                  aria-pressed={selected.includes(tag)}
                  onClick={() => toggle(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </fieldset>
          <div className="row">
            <div className="field grow">
              <label htmlFor="custom-tag">Add a competency</label>
              <input id="custom-tag" value={custom} onChange={(event) => setCustom(event.target.value)} />
            </div>
            <button className="button secondary" type="button" onClick={addCustom}>
              Add tag
            </button>
          </div>
          {selected.length ? (
            <p className="meta">Selected: {selected.join(", ")}</p>
          ) : (
            <p className="meta">No competency selected yet.</p>
          )}
          <div className="field">
            <label htmlFor="review-feedback">
              Note to the learner
              <span className="hint">Required if you request changes. Optional when you certify.</span>
            </label>
            <textarea
              id="review-feedback"
              rows={4}
              value={feedback}
              onChange={(event) => setFeedback(event.target.value)}
            />
          </div>
          {error ? <ErrorBlock message={error} /> : null}
          <div className="form-actions">
            <button
              className="button"
              type="button"
              disabled={pending || selected.length === 0}
              onClick={() => void review("approve")}
            >
              Issue certification
            </button>
            <button
              className="button secondary"
              type="button"
              disabled={pending || feedback.trim().length < 10}
              onClick={() => void review("request_changes")}
            >
              Request changes
            </button>
          </div>
        </section>
      ) : null}
      {success ? <SuccessBlock message={success} /> : null}
      {submission.status === "changes_requested" && auth.user?.id ? (
        <p>
          <Link href={`/missions/${submission.mission_id}`}>Return to the mission to submit a revision.</Link>
        </p>
      ) : null}
    </>
  );
}
