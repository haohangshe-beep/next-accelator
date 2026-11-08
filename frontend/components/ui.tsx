"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { statusLabel, trackLabel } from "@/lib/tracks";

export function TrackBadge({ track }: { track: string }) {
  return <span className={`badge track-${track}`}>{trackLabel(track)}</span>;
}

export function StatusPill({ status }: { status: string }) {
  return <span className={`pill status-${status}`}>{statusLabel(status)}</span>;
}

export function PageIntro({
  kicker,
  title,
  lede,
}: {
  kicker?: string;
  title: string;
  lede?: string;
}) {
  return (
    <header className="page-intro">
      {kicker ? <p className="eyebrow">{kicker}</p> : null}
      <h1>{title}</h1>
      {lede ? <p className="lede">{lede}</p> : null}
    </header>
  );
}

export function LoadingLine({ label = "Loading…" }: { label?: string }) {
  return <p className="muted">{label}</p>;
}

export function ErrorBlock({ message }: { message: string }) {
  return (
    <p className="banner error" role="alert">
      {message}
    </p>
  );
}

export function SuccessBlock({ message }: { message: string }) {
  return (
    <p className="banner success" role="status">
      {message}
    </p>
  );
}

export function EmptyState({
  title,
  body,
  href,
  action,
}: {
  title: string;
  body: string;
  href?: string;
  action?: string;
}) {
  return (
    <div className="empty">
      <h2>{title}</h2>
      <p>{body}</p>
      {href && action ? (
        <Link className="button" href={href}>
          {action}
        </Link>
      ) : null}
    </div>
  );
}

export function Field({
  id,
  label,
  hint,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>
        {label}
        {hint ? <span className="hint">{hint}</span> : null}
      </label>
      {children}
    </div>
  );
}

export function CodeList({ codes }: { codes: string[] }) {
  if (!codes.length) {
    return <span className="muted">None</span>;
  }
  return (
    <span className="code-list">
      {codes.map((code) => (
        <Link key={code} className="code" href={`/skills/${code}`}>
          {code}
        </Link>
      ))}
    </span>
  );
}
