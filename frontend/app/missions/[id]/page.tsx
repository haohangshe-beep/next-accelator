import type { Metadata } from "next";
import { MissionDetailView } from "@/components/views/mission-detail-view";

export const metadata: Metadata = { title: "Mission" };

export default function MissionPage() {
  return <MissionDetailView />;
}
