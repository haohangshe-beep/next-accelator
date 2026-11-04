import type { Metadata } from "next";
import { PlaceholderView } from "@/components/views/placeholder-view";

export const metadata: Metadata = { title: "Talent marketplace" };

export default function TalentPage() {
  return (
    <PlaceholderView
      kicker="Coming later"
      title="Talent marketplace"
      lede="Employers will be able to read Skills Passports when they are hiring. That search is not part of this version."
      body="There is no candidate matching, no inbound applications, and no ranking. Leave a work email if you want to hear when passport search opens. Until then, share a passport link directly."
      topic="talent"
    />
  );
}
