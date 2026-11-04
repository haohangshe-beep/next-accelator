"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Frame } from "@/components/site-header";
import { EmptyState, ErrorBlock, LoadingLine, PageIntro, StatusPill, TrackBadge } from "@/components/ui";
import { formatDate } from "@/lib/format";
import type { MissionSummary, ModuleSummary } from "@/lib/types";
import { TRACKS } from "@/lib/tracks";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

export function MissionsView() {
  usePageTitle("Missions");
  const params = useSearchParams();
  const router = useRouter();
  const requestedTrack = params.get("track") ?? "";
  const requestedSkill = (params.get("skill") ?? "").toUpperCase();
  const track = TRACKS.some((item) => item.code === requestedTrack) ? requestedTrack : "";
  const skill = /^[A-Z]{2,6}[0-9]{3}$/.test(requestedSkill) ? requestedSkill : "";
  const query = new URLSearchParams();
  if (track) {
    query.set("track", track);
  }
  if (skill) {
    query.set("skill", skill);
  }
  const suffix = query.toString();
  const missions = useApi<MissionSummary[]>(`/missions${suffix ? `?${suffix}` : ""}`);
  const modules = useApi<ModuleSummary[]>("/modules");

  function apply(nextTrack: string, nextSkill: string) {
    const next = new URLSearchParams();
    if (nextTrack) {
      next.set("track", nextTrack);
    }
    if (nextSkill) {
      next.set("skill", nextSkill);
    }
    const text = next.toString();
    router.replace(text ? `/missions?${text}` : "/missions");
  }

  const skillOptions = modules.data ?? [];
  const knownSkill = skillOptions.some((module) => module.code === skill);

  return (
    <Frame>
      <PageIntro
        kicker="Mission marketplace"
        title="Live briefs, not job ads"
        lede="Filter by track and by the skill a mission requires. Join when your passport covers the prerequisites, then submit a URL."
      />
      <form className="filters" onSubmit={(event) => event.preventDefault()}>
        <div className="field">
          <label htmlFor="track-filter">Track</label>
          <select
            id="track-filter"
            value={track}
            onChange={(event) => apply(event.target.value, skill)}
          >
            <option value="">All tracks</option>
            {TRACKS.map((item) => (
              <option key={item.code} value={item.code}>
                {item.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="skill-filter">Required skill</label>
          <select id="skill-filter" value={skill} onChange={(event) => apply(track, event.target.value)}>
            <option value="">Any skill</option>
            {!knownSkill && skill ? <option value={skill}>{skill}</option> : null}
            {skillOptions.map((module) => (
              <option key={module.code} value={module.code}>
                {module.code} · {module.title}
              </option>
            ))}
          </select>
        </div>
        {track || skill ? (
          <button className="button secondary" type="button" onClick={() => apply("", "")}>
            Clear filters
          </button>
        ) : null}
      </form>
      {missions.loading ? <LoadingLine label="Loading missions…" /> : null}
      {missions.error ? <ErrorBlock message={missions.error} /> : null}
      {missions.data ? (
        <p className="muted">
          {missions.data.length} {missions.data.length === 1 ? "mission" : "missions"}
        </p>
      ) : null}
      {missions.data && missions.data.length === 0 ? (
        <EmptyState
          title="No missions match"
          body="Clear the filters, or finish the module a mission asks for and check again."
          href="/skills"
          action="Browse skills"
        />
      ) : null}
      <ul className="card-grid">
        {(missions.data ?? []).map((mission) => (
          <li key={mission.id}>
            <Link className={`card track-card track-${mission.track}`} href={`/missions/${mission.id}`}>
              <div className="meta-row">
                <TrackBadge track={mission.track} />
                {mission.membership_status ? <StatusPill status={mission.membership_status} /> : null}
              </div>
              <h2>{mission.title}</h2>
              <p className="kicker">{mission.organization_name}</p>
              <p>{mission.summary}</p>
              <p className="meta">
                {mission.difficulty}
                {" · "}
                {mission.required_skill_codes.length
                  ? `Requires ${mission.required_skill_codes.join(", ")}`
                  : "No prerequisite modules"}
                {" · "}
                {mission.deadline ? `Due ${formatDate(mission.deadline)}` : "No deadline"}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </Frame>
  );
}
