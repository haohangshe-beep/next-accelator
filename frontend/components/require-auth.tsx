"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import type { ReactNode } from "react";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";
import { LoadingLine } from "@/components/ui";

export function RequireAuth({
  roles,
  children,
}: {
  roles?: readonly Role[];
  children: ReactNode;
}) {
  const auth = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const allowed = !roles || (auth.user ? roles.includes(auth.user.role) : false);

  useEffect(() => {
    if (!auth.ready) {
      return;
    }
    if (!auth.user) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
      return;
    }
    if (roles && !roles.includes(auth.user.role)) {
      router.replace("/app");
    }
  }, [auth.ready, auth.user, roles, router, pathname]);

  if (!auth.ready || !auth.user || !allowed) {
    return <LoadingLine label="Loading your workspace…" />;
  }
  return <>{children}</>;
}
