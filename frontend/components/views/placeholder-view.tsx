"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { Frame } from "@/components/site-header";
import { ErrorBlock, Field, PageIntro, SuccessBlock } from "@/components/ui";
import { api, errorMessage } from "@/lib/api";
import type { WaitlistResult } from "@/lib/types";
import { usePageTitle } from "@/lib/use-title";

export function PlaceholderView({
  title,
  kicker,
  lede,
  body,
  topic,
}: {
  title: string;
  kicker: string;
  lede: string;
  body: string;
  topic: "talent" | "apprenticeships";
}) {
  usePageTitle(title);
  const [email, setEmail] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const result = await api<WaitlistResult>("/waitlist", {
        body: { email, topic },
      });
      setDone(
        result.already_registered
          ? `${email} is already on this list.`
          : `You're on the list. We'll use ${email} when this opens.`,
      );
      setEmail("");
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  return (
    <Frame>
      <PageIntro kicker={kicker} title={title} lede={lede} />
      <div className="card notice">
        <p className="kicker">Not in this version</p>
        <p>{body}</p>
      </div>
      <form className="card form" onSubmit={(event) => void submit(event)}>
        <Field id={`${topic}-email`} label="Work email" hint="Stored for this demo only. No matching happens yet.">
          <input
            id={`${topic}-email`}
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </Field>
        {error ? <ErrorBlock message={error} /> : null}
        {done ? <SuccessBlock message={done} /> : null}
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Saving…" : "Join the waitlist"}
        </button>
      </form>
    </Frame>
  );
}
