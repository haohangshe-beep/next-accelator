"use client";

import Link from "next/link";
import { Frame } from "@/components/site-header";
import { RequireAuth } from "@/components/require-auth";
import { ErrorBlock, LoadingLine, PageIntro, StatusPill, TrackBadge } from "@/components/ui";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { Dashboard, NavigatorResponse } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

export function DashboardView() {
  usePageTitle("Workspace");
  return (
    <Frame>
      <RequireAuth>
        <DashboardBody />
      </RequireAuth>
    </Frame>
  );
}

function DashboardBody() {
  const auth = useAuth();
  const role = auth.user?.role ?? null;
  const home = useApi<Dashboard>(role ? "/dashboard" : null);
  const navigator = useApi<NavigatorResponse>(role === "learner" ? "/navigator" : null);

  if (home.loading || !home.data) {
    return home.error ? <ErrorBlock message={home.error} /> : <LoadingLine label="Loading your workspace…" />;
  }

  const { user, learner, employer, admin } = home.data;

  return (
    <>
      <PageIntro
        kicker={user.organization?.name ?? "Your workspace"}
        title={`Hello, ${user.full_name.split(" ")[0]}`}
        lede={user.headline}
      />
      {learner ? (
        <>
          <section className="stats" aria-label="Passport progress">
            <article className="stat">
              <p className="stat-value">{learner.completed_modules}</p>
              <p>Modules on your passport</p>
            </article>
            <article className="stat">
              <p className="stat-value">{learner.missions_joined}</p>
              <p>Missions joined</p>
            </article>
            <article className="stat">
              <p className="stat-value">{learner.certifications}</p>
              <p>Employer certifications</p>
            </article>
          </section>
          <div className="actions">
            <Link className="button" href="/skills">
              Continue skills
            </Link>
            <Link className="button secondary" href="/missions">
              Browse missions
            </Link>
            <Link className="button secondary" href={`/passport/${learner.passport_slug}`}>
              Open passport
            </Link>
          </div>
          <section className="section-block">
            <h2>Evidence in flight</h2>
            {learner.submissions.length ? (
              <ul className="card-grid">
                {learner.submissions.map((submission) => (
                  <li key={submission.id} className="card compact">
                    <StatusPill status={submission.status} />
                    <h3>
                      <Link href={`/submissions/${submission.id}`}>{submission.mission_title}</Link>
                    </h3>
                    <p className="muted">Updated {formatDate(submission.updated_at)}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>You have not submitted evidence yet. Join a mission and add a deliverable URL.</p>
            )}
          </section>
          <section className="section-block">
            <h2>Recommended next</h2>
            {navigator.error ? <ErrorBlock message={navigator.error} /> : null}
            {navigator.loading ? <LoadingLine label="Looking at your path…" /> : null}
            <ul className="card-grid">
              {(navigator.data?.recommendations ?? []).slice(0, 3).map((item) => (
                <li key={item.id} className="card compact">
                  <p className="kicker">{item.kind}</p>
                  <h3>{item.title}</h3>
                  <p>{item.reason}</p>
                  <Link className="button secondary" href={item.href}>
                    {item.action_label}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </>
      ) : null}
      {employer ? (
        <>
          <div className="actions">
            <Link className="button" href="/missions/new">
              Publish a mission
            </Link>
            <Link className="button secondary" href="/missions">
              Mission board
            </Link>
          </div>
          <section className="section-block">
            <h2>Waiting for your review</h2>
            {employer.pending_reviews.length ? (
              <ul className="card-grid">
                {employer.pending_reviews.map((review) => (
                  <li key={review.id} className="card compact">
                    <p className="kicker">Pending certification</p>
                    <h3>{review.mission_title}</h3>
                    <p>
                      {review.learner_name} · submitted {formatDate(review.submitted_at)}
                    </p>
                    <div className="actions">
                      <Link className="button" href={`/submissions/${review.id}`}>
                        Review evidence
                      </Link>
                      <Link className="button secondary" href={`/passport/${review.learner_slug}`}>
                        Passport
                      </Link>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="empty">
                <h3>No submissions are waiting</h3>
                <p>When a learner submits evidence on your mission, it will show up here for certification.</p>
              </div>
            )}
          </section>
          <section className="section-block">
            <h2>Your missions</h2>
            <ul className="card-grid">
              {employer.missions.map((mission) => (
                <li key={mission.id} className="card compact">
                  <TrackBadge track={mission.track} />
                  <h3>
                    <Link href={`/missions/${mission.id}`}>{mission.title}</Link>
                  </h3>
                  <p className="muted">
                    {mission.pending_count} pending · {mission.submission_count} submissions
                  </p>
                </li>
              ))}
            </ul>
          </section>
        </>
      ) : null}
      {admin ? (
        <>
          <section className="stats" aria-label="Catalogue counts">
            <article className="stat">
              <p className="stat-value">{admin.module_count}</p>
              <p>Skill modules</p>
            </article>
            <article className="stat">
              <p className="stat-value">{admin.mission_count}</p>
              <p>Missions</p>
            </article>
            <article className="stat">
              <p className="stat-value">{admin.user_count}</p>
              <p>Seeded users</p>
            </article>
            <article className="stat">
              <p className="stat-value">{admin.waitlist_count}</p>
              <p>Waitlist notes</p>
            </article>
          </section>
          <div className="actions">
            <Link className="button" href="/admin/modules">
              Manage modules
            </Link>
          </div>
          <p className="lede">
            Demo users and the opening catalogue are seeded when the API starts. Add a module here when the
            catalogue needs a new code.
          </p>
        </>
      ) : null}
    </>
  );
}
