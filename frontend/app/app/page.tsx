import type { Metadata } from "next";
import { DashboardView } from "@/components/views/dashboard-view";

export const metadata: Metadata = { title: "Workspace" };

export default function WorkspacePage() {
  return <DashboardView />;
}
