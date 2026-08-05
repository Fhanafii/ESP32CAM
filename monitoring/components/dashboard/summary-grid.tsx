import {
  Shield,
  ShieldCheck,
  TriangleAlert,
  ShieldAlert,
  Image,
  Send,
} from "lucide-react";

import { DashboardSummary } from "@/types/dashboard";
import { SummaryCard } from "./summary-card";

interface SummaryGridProps {
  dashboard: DashboardSummary;
}

export function SummaryGrid({
  dashboard,
}: SummaryGridProps) {

  return (

    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

      <SummaryCard
        title="Total Batch"
        value={dashboard.total_batch}
        icon={Shield}
        color="bg-slate-700"
      />

      <SummaryCard
        title="Total Deteksi"
        value={dashboard.total_detected_frames}
        icon={Image}
        color="bg-blue-600"
      />

      <SummaryCard
        title="Normal"
        value={dashboard.normal}
        icon={ShieldCheck}
        color="bg-green-600"
      />

      <SummaryCard
        title="Perlu Dipantau"
        value={dashboard.monitoring}
        icon={TriangleAlert}
        color="bg-yellow-500"
      />

      <SummaryCard
        title="Mencurigakan"
        value={dashboard.suspicious}
        icon={ShieldAlert}
        color="bg-red-600"
      />

      <SummaryCard
        title="WhatsApp"
        value={dashboard.whatsapp_sent}
        icon={Send}
        color="bg-emerald-600"
      />

    </section>
  );
}