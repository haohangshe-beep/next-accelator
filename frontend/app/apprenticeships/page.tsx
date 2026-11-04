import type { Metadata } from "next";
import { PlaceholderView } from "@/components/views/placeholder-view";

export const metadata: Metadata = { title: "Apprenticeships" };

export default function ApprenticeshipsPage() {
  return (
    <PlaceholderView
      kicker="Coming later"
      title="Apprenticeships"
      lede="Structured apprenticeships are meant to follow employer-certified missions. The matching workflow is not built yet."
      body="This page does not place anyone into an apprenticeship. Join the waitlist and the programme can write when a real placement flow exists."
      topic="apprenticeships"
    />
  );
}
