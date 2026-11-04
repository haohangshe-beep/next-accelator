"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Frame } from "@/components/site-header";
import { ErrorBlock, Field, PageIntro } from "@/components/ui";
import { errorMessage, safeNext } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { DEMO_ACCOUNTS, DEMO_PASSWORD } from "@/lib/demo";
import { usePageTitle } from "@/lib/use-title";

export function LoginView() {
  usePageTitle("Sign in");
  const auth = useAuth();
  const router = useRouter();
  const params = useSearchParams();
  const next = safeNext(params.get("next"));
  const [email, setEmail] = useState("learner@demo.ftos");
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function signIn(nextEmail: string, nextPassword: string) {
    setError(null);
    setPending(true);
    try {
      await auth.login(nextEmail, nextPassword);
      router.push(next);
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <Frame>
      <PageIntro
        kicker="Demo access"
        title="Sign in to FTOS"
        lede="Use a seeded account to walk the path from a module to an employer certification. The same password is written in the README."
      />
      <div className="split">
        <form
          className="card form"
          onSubmit={(event) => {
            event.preventDefault();
            void signIn(email, password);
          }}
        >
          <Field id="email" label="Email">
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </Field>
          <Field id="password" label="Password">
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </Field>
          {error ? <ErrorBlock message={error} /> : null}
          <div className="form-actions">
            <button className="button" type="submit" disabled={pending}>
              {pending ? "Signing in…" : "Sign in"}
            </button>
          </div>
        </form>
        <div className="stack">
          {DEMO_ACCOUNTS.map((account) => (
            <article key={account.email} className="card compact">
              <p className="kicker">{account.role}</p>
              <h2>{account.email}</h2>
              <p>{account.detail}</p>
              <button
                className="button secondary"
                type="button"
                disabled={pending}
                onClick={() => {
                  setEmail(account.email);
                  setPassword(DEMO_PASSWORD);
                  void signIn(account.email, DEMO_PASSWORD);
                }}
              >
                Enter as {account.role.toLowerCase()}
              </button>
            </article>
          ))}
        </div>
      </div>
    </Frame>
  );
}
