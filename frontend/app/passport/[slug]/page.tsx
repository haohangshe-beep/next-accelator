import type { Metadata } from "next";
import { PassportView } from "@/components/views/passport-view";

export const metadata: Metadata = { title: "Skills Passport" };

export default function PassportPage() {
  return <PassportView />;
}
