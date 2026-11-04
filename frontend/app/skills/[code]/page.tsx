import type { Metadata } from "next";
import { SkillDetailView } from "@/components/views/skill-detail-view";

export const metadata: Metadata = { title: "Skill module" };

export default function SkillPage() {
  return <SkillDetailView />;
}
