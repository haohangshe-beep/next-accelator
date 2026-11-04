import type { Metadata } from "next";
import { AdminModulesView } from "@/components/views/admin-modules-view";

export const metadata: Metadata = { title: "Module admin" };

export default function AdminModulesPage() {
  return <AdminModulesView />;
}
