import type { Metadata } from "next";
import { Suspense } from "react";
import { MissionsView } from "@/components/views/missions-view";

export const metadata: Metadata = { title: "Missions" };

export default function MissionsPage() {
  return (
    <Suspense fallback={<p className="page muted">Loading missions…</p>}>
      <MissionsView />
    </Suspense>
  );
}
