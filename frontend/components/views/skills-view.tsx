"use client";

import Link from "next/link";
import { Frame } from "@/components/site-header";
import { EmptyState, ErrorBlock, LoadingLine, PageIntro, TrackBadge } from "@/components/ui";
import type { ModuleSummary } from "@/lib/types";
import { TRACKS } from "@/lib/tracks";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

export function SkillsView() {
  usePageTitle("Skills");
  const modules = useApi<ModuleSummary[]>("/modules");

  return (
    <Frame>
      <PageIntro
        kicker="Modular skills"
        title="A catalogue you can finish"
        lede="Each module is a short self-check. When you confirm it, the record is written to your Skills Passport."
      />
      {modules.loading ? <LoadingLine label="Loading modules…" /> : null}
      {modules.error ? <ErrorBlock message={modules.error} /> : null}
      {modules.data && modules.data.length === 0 ? (
        <EmptyState
          title="No modules yet"
          body="An admin can add the first module to the catalogue."
          href="/admin/modules"
          action="Open module admin"
        />
      ) : null}
      {TRACKS.map((track) => {
        const items = (modules.data ?? []).filter((module) => module.track === track.code);
        if (!items.length) {
          return null;
        }
        return (
          <section key={track.code} className="section-block">
            <div className="section-heading">
              <TrackBadge track={track.code} />
              <p>{track.summary}</p>
            </div>
            <ul className="card-grid">
              {items.map((module) => (
                <li key={module.code}>
                  <Link className={`card track-card track-${module.track}`} href={`/skills/${module.code}`}>
                    <span className="code">{module.code}</span>
                    <h2>{module.title}</h2>
                    <p>{module.summary}</p>
                    <p className="meta">
                      {module.level} · {module.estimated_hours} hours
                      {module.completed ? " · On your passport" : ""}
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </Frame>
  );
}
