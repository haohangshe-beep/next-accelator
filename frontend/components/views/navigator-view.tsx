"use client";

import Link from "next/link";
import { Frame } from "@/components/site-header";
import { RequireAuth } from "@/components/require-auth";
import { EmptyState, ErrorBlock, LoadingLine, PageIntro } from "@/components/ui";
import type { NavigatorResponse, Role } from "@/lib/types";
import { useApi } from "@/lib/use-api";
import { usePageTitle } from "@/lib/use-title";

const LEARNER: readonly Role[] = ["learner"];

export function NavigatorView() {
  usePageTitle("Career navigator");
  return (
    <Frame>
      <RequireAuth roles={LEARNER}>
        <NavigatorBody />
      </RequireAuth>
    </Frame>
  );
}

function NavigatorBody() {
  const navigator = useApi<NavigatorResponse>("/navigator");
  return (
    <>
      <PageIntro
        kicker="AI career navigator"
        title="A path, not a chatbot"
        lede="These recommendations are rules over the modules you have finished and the tracks you listed as interests. Nothing here calls a language model."
      />
      {navigator.loading ? <LoadingLine label="Building your path…" /> : null}
      {navigator.error ? <ErrorBlock message={navigator.error} /> : null}
      {navigator.data ? <p>{navigator.data.summary}</p> : null}
      {navigator.data && navigator.data.recommendations.length === 0 ? (
        <EmptyState
          title="No recommendations yet"
          body="Complete a foundation module and the navigator will suggest the next module and a mission."
          href="/skills"
          action="Browse skills"
        />
      ) : null}
      <ol className="path-list">
        {(navigator.data?.recommendations ?? []).map((item, index) => (
          <li key={item.id} className="card path-card">
            <p className="kicker">
              {String(index + 1).padStart(2, "0")} · {item.kind}
            </p>
            <h2>{item.title}</h2>
            <p>{item.reason}</p>
            <Link className="button" href={item.href}>
              {item.action_label}
            </Link>
          </li>
        ))}
      </ol>
    </>
  );
}
