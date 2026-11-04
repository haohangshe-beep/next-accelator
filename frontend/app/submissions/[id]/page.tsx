import type { Metadata } from "next";
import { SubmissionView } from "@/components/views/submission-view";

export const metadata: Metadata = { title: "Submission" };

export default function SubmissionPage() {
  return <SubmissionView />;
}
