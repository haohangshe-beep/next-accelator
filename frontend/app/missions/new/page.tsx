import type { Metadata } from "next";
import { MissionNewView } from "@/components/views/mission-new-view";

export const metadata: Metadata = { title: "Publish a mission" };

export default function NewMissionPage() {
  return <MissionNewView />;
}
