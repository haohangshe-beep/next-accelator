"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Frame } from "@/components/site-header";
import { EmptyState, LoadingLine, StatusPill, TrackBadge } from "@/components/ui";
import { useAuth } from "@/lib/auth";
import { formatDate } from "@/lib/format";
import type { Passport } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

function routeSlug(value: string | string[] | undefined): string {
  const raw = Array.isArray(value) ? value[0] : value;
  return raw ?? "";
}

export function PassportView() {
  const params = useParams<{ slug: string }>();
  const slug = routeSlug(params.slug);
  const passport = useApi<Passport>(slug ? `/passport/${slug}` : null);
  const profile = passport.data?.profile;
  usePageTitle(profile ? `${profile.full_name} · Skills Passport` : "Skills Passport");
  const auth = useAuth();
  const [link, setLink] = useState("");
  const [copied, setCopied] = useState(false);
  const isOwner = Boolean(profile && auth.user?.slug === profile.slug);

  useEffect(() => {
    setLink(`${window.location.origin}/passport/${slug}`);
  }, [slug]);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(link || window.location.href);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <Frame>
      {passport.loading ? <LoadingLine label="Loading passport…" /> : null}
      {passport.error ? (
        <EmptyState title="Passport not found" body={passport.error} href="/skills" action="Browse skills" />
      ) : null}
      {profile && passport.data ? (
        <article className="passport">
          <header className="passport-head">
            <p className="eyebrow">Skills Passport</p>
            <h1>{profile.full_name}</h1>
            <p className="lede">{profile.headline}</p>
            {profile.bio ? <p>{profile.bio}</p> : null}
            {profile.interests.length ? (
              <div className="meta-row">
                {profile.interests.map((interest) => (
                  <TrackBadge key={interest} track={interest} />
                ))}
              </div>
            ) : null}
            <div className="copy-row">
              <label className="sr-only" htmlFor="passport-link">
                Public passport link
              </label>
              <input id="passport-link" readOnly value={link} />
              <button className="button" type="button" onClick={() => void copyLink()}>
                {copied ? "Copied" : "Copy link"}
              </button>
            </div>
          </header>
          <section className="stats" aria-label="Passport totals">
            <article className="stat">
              <p className="stat-value">{passport.data.modules.length}</p>
              <p>Modules</p>
            </article>
            <article className="stat">
              <p className="stat-value">{passport.data.missions.length}</p>
              <p>Missions</p>
            </article>
            <article className="stat">
              <p className="stat-value">{passport.data.certifications.length}</p>
              <p>Certifications</p>
            </article>
          </section>
          <section className="section-block">
            <h2>Skills modules</h2>
            {passport.data.modules.length ? (
              <ul className="plain-list">
                {passport.data.modules.map((module) => (
                  <li key={module.code}>
                    <div>
                      <TrackBadge track={module.track} />
                      <h3>
                        <Link href={`/skills/${module.code}`}>
                          {module.code} · {module.title}
                        </Link>
                      </h3>
                      <p className="meta">
                        {module.level} · {module.estimated_hours} hours · recorded {formatDate(module.completed_at)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>
                No modules recorded yet.
                {isOwner ? (
                  <>
                    {" "}
                    <Link href="/skills">Complete a module</Link> to start the passport.
                  </>
                ) : null}
              </p>
            )}
          </section>
          <section className="section-block">
            <h2>Missions</h2>
            {passport.data.missions.length ? (
              <ul className="plain-list">
                {passport.data.missions.map((mission) => (
                  <li key={mission.id}>
                    <div>
                      <div className="meta-row">
                        <TrackBadge track={mission.track} />
                        <StatusPill status={mission.status} />
                      </div>
                      <h3>
                        <Link href={`/missions/${mission.id}`}>{mission.title}</Link>
                      </h3>
                      <p className="meta">
                        {mission.organization_name} · joined {formatDate(mission.joined_at)}
                      </p>
                      {mission.deliverable_url ? (
                        <p>
                          <a href={mission.deliverable_url} target="_blank" rel="noreferrer">
                            Evidence
                          </a>
                        </p>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>
                No missions yet.
                {isOwner ? (
                  <>
                    {" "}
                    <Link href="/missions">Join a mission</Link> and submit evidence.
                  </>
                ) : null}
              </p>
            )}
          </section>
          <section className="section-block">
            <h2>Employer certifications</h2>
            {passport.data.certifications.length ? (
              <ul className="stack">
                {passport.data.certifications.map((certification) => (
                  <li key={certification.id} className="stamp">
                    <p className="kicker">Certified</p>
                    <p>{certification.statement}</p>
                    <p className="meta">
                      {certification.organization_name} · {certification.issuer_name} ·{" "}
                      {formatDate(certification.issued_at)}
                    </p>
                    <ul className="tag-row">
                      {certification.competency_tags.map((tag) => (
                        <li key={tag} className="tag">
                          {tag}
                        </li>
                      ))}
                    </ul>
                    <Link href={`/missions/${certification.mission_id}`}>Mission brief</Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No employer certifications yet.</p>
            )}
          </section>
          <section className="section-block next-paths">
            <h2>What this passport is not</h2>
            <p>Talent search and apprenticeships are not open in this version. The record above is the evidence.</p>
            <div className="actions">
              <Link className="button secondary" href="/talent">
                Talent marketplace
              </Link>
              <Link className="button secondary" href="/apprenticeships">
                Apprenticeships
              </Link>
            </div>
          </section>
        </article>
      ) : null}
    </Frame>
  );
}
