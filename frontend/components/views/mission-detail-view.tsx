"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import { Frame } from "@/components/site-header";
import { CodeList, ErrorBlock, LoadingLine, PageIntro, StatusPill, SuccessBlock, TrackBadge } from "@/components/ui";
import { api, errorMessage } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { MissionDetail, Submission } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

function routeId(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw ?? "";
}

export function MissionDetailView() {
  const params = useParams<{ id: string }>();
  const id = routeId(params.id);
  const numeric = /^\d+$/.test(id);
  const missionState = useApi<MissionDetail>(numeric ? `/missions/${id}` : null);
  const mission = missionState.data;
  usePageTitle(mission?.title ?? "Mission");
  const auth = useAuth();
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function join() {
    if (!auth.token || !mission) {
      return;
    }
    setPending(true);
    setError(null);
    try {
      const next = await api<MissionDetail>(`/missions/${mission.id}/join`, { token: auth.token, method: "POST" });
      missionState.setData(next);
      setSuccess("You have joined this mission. Submit a deliverable when the evidence is ready.");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!auth.token || !mission) {
      return;
    }
    setPending(true);
    setError(null);
    setSuccess(null);
    try {
      await api<Submission>(`/missions/${mission.id}/submit`, {
        token: auth.token,
        body: { deliverable_url: url, notes },
      });
      setSuccess("Evidence submitted. It is waiting for the employer to review.");
      setUrl("");
      setNotes("");
      await missionState.reload();
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  const canSubmit =
    auth.user?.role === "learner" &&
    (mission?.membership_status === "joined" || mission?.membership_status === "changes_requested");

  return (
    <Frame>
      {!numeric ? <ErrorBlock message="That mission link is not valid." /> : null}
      {missionState.loading ? <LoadingLine label="Loading mission…" /> : null}
      {missionState.error ? <ErrorBlock message={missionState.error} /> : null}
      {mission ? (
        <>
          <PageIntro kicker={mission.organization_name} title={mission.title} lede={mission.summary} />
          <div className="meta-row">
            <TrackBadge track={mission.track} />
            <span>{mission.difficulty}</span>
            <span>{mission.deadline ? `Due ${formatDate(mission.deadline)}` : "No deadline"}</span>
            {mission.membership_status ? <StatusPill status={mission.membership_status} /> : null}
          </div>
          <section className="section-block">
            <h2>Problem</h2>
            <p>{mission.problem_statement}</p>
          </section>
          <section className="section-block">
            <h2>What to submit</h2>
            <p>{mission.deliverables}</p>
          </section>
          <section className="section-block">
            <h2>Required modules</h2>
            {mission.required_skill_codes.length ? (
              <CodeList codes={mission.required_skill_codes} />
            ) : (
              <p>No prerequisite modules.</p>
            )}
            {mission.missing_skill_codes.length ? (
              <p className="callout">
                Record {mission.missing_skill_codes.join(", ")} on your passport before you can join.
              </p>
            ) : null}
          </section>
          {error ? <ErrorBlock message={error} /> : null}
          {success ? <SuccessBlock message={success} /> : null}
          {auth.user?.role === "learner" && !mission.membership_status ? (
            <div className="form-actions">
              <button
                className="button"
                type="button"
                disabled={pending || mission.missing_skill_codes.length > 0 || mission.status !== "open"}
                onClick={() => void join()}
              >
                Join mission
              </button>
            </div>
          ) : null}
          {!auth.user ? (
            <Link className="button" href={`/login?next=/missions/${mission.id}`}>
              Sign in to join
            </Link>
          ) : null}
          {canSubmit ? (
            <form className="card form" onSubmit={(event) => void submit(event)}>
              <h2>{mission.membership_status === "changes_requested" ? "Submit a revision" : "Submit evidence"}</h2>
              {mission.my_submission?.feedback ? (
                <p className="callout">Employer note: {mission.my_submission.feedback}</p>
              ) : null}
              <div className="field">
                <label htmlFor="deliverable-url">Deliverable URL</label>
                <input
                  id="deliverable-url"
                  type="url"
                  required
                  placeholder="https://"
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="deliverable-notes">
                  Notes
                  <span className="hint">What should the reviewer look at, and what did you leave out?</span>
                </label>
                <textarea
                  id="deliverable-notes"
                  required
                  rows={5}
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                />
              </div>
              <button className="button" type="submit" disabled={pending}>
                {pending ? "Submitting…" : "Submit for review"}
              </button>
            </form>
          ) : null}
          {mission.my_submission ? (
            <section className="section-block card">
              <h2>Your evidence</h2>
              <StatusPill status={mission.my_submission.status} />
              <p>
                <a href={mission.my_submission.deliverable_url} target="_blank" rel="noreferrer">
                  {mission.my_submission.deliverable_url}
                </a>
              </p>
              <p>{mission.my_submission.notes}</p>
              <Link className="button secondary" href={`/submissions/${mission.my_submission.id}`}>
                Open submission
              </Link>
            </section>
          ) : null}
          {mission.submissions.length ? (
            <section className="section-block">
              <h2>Submissions to review</h2>
              <ul className="card-grid">
                {mission.submissions.map((submission) => (
                  <li key={submission.id} className="card compact">
                    <StatusPill status={submission.status} />
                    <h3>{submission.learner_name}</h3>
                    <p className="muted">Updated {formatDate(submission.updated_at)}</p>
                    <div className="actions">
                      <Link className="button" href={`/submissions/${submission.id}`}>
                        Review
                      </Link>
                      <Link className="button secondary" href={`/passport/${submission.learner_slug}`}>
                        Passport
                      </Link>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </>
      ) : null}
    </Frame>
  );
}
