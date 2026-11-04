"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useAuth } from "@/lib/auth";

const LINKS = [
  { href: "/skills", label: "Skills" },
  { href: "/missions", label: "Missions" },
  { href: "/navigator", label: "Navigator" },
  { href: "/talent", label: "Talent" },
  { href: "/apprenticeships", label: "Apprenticeships" },
];

function isCurrent(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const auth = useAuth();

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" href="/">
          <span className="brand-mark">FTOS</span>
          <span className="brand-sub">Frontier Talent OS</span>
        </Link>
        <nav className="nav" aria-label="Primary">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              aria-current={isCurrent(pathname, link.href) ? "page" : undefined}
            >
              {link.label}
            </Link>
          ))}
          {auth.user ? (
            <Link href="/app" aria-current={isCurrent(pathname, "/app") ? "page" : undefined}>
              Workspace
            </Link>
          ) : null}
          {auth.user?.role === "learner" ? (
            <Link
              href={`/passport/${auth.user.slug}`}
              aria-current={pathname.startsWith("/passport/") ? "page" : undefined}
            >
              Passport
            </Link>
          ) : null}
          {auth.user?.role === "employer" ? (
            <Link href="/missions/new" aria-current={pathname === "/missions/new" ? "page" : undefined}>
              Publish
            </Link>
          ) : null}
          {auth.user?.role === "admin" ? (
            <Link
              href="/admin/modules"
              aria-current={isCurrent(pathname, "/admin") ? "page" : undefined}
            >
              Modules
            </Link>
          ) : null}
        </nav>
        <div className="header-actions">
          {auth.user ? (
            <button
              type="button"
              className="button secondary"
              onClick={() => {
                auth.logout();
                router.push("/");
              }}
            >
              Sign out
            </button>
          ) : (
            <Link className="button" href="/login">
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <p>
        Hong Kong Frontier Talent Operating System. Demonstration build — certifications here are
        sample records, not government credentials.
      </p>
    </footer>
  );
}

export function Frame({
  children,
  variant = "page",
}: {
  children: ReactNode;
  variant?: "page" | "home";
}) {
  return (
    <>
      <a className="skip" href="#content">
        Skip to content
      </a>
      <SiteHeader />
      <main id="content" className={variant === "home" ? "home" : "page"}>
        {children}
      </main>
      <SiteFooter />
    </>
  );
}
