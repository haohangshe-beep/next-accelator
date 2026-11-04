import type { Metadata } from "next";
import { SkillsView } from "@/components/views/skills-view";

export const metadata: Metadata = { title: "Skills" };

export default function SkillsPage() {
  return <SkillsView />;
}
