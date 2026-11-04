import type { Metadata } from "next";
import { NavigatorView } from "@/components/views/navigator-view";

export const metadata: Metadata = { title: "Career navigator" };

export default function NavigatorPage() {
  return <NavigatorView />;
}
