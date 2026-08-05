import {
  Shield,
  ShieldCheck,
  TriangleAlert,
  ShieldAlert,
} from "lucide-react";

import { SummaryCard } from "./summary-card";

export function SummaryGrid() {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

      <SummaryCard
        title="Total Batch"
        value={604}
        icon={Shield}
        color="bg-slate-700"
      />

      <SummaryCard
        title="Normal"
        value={160}
        icon={ShieldCheck}
        color="bg-green-600"
      />

      <SummaryCard
        title="Perlu Dipantau"
        value={24}
        icon={TriangleAlert}
        color="bg-yellow-500"
      />

      <SummaryCard
        title="Mencurigakan"
        value={1}
        icon={ShieldAlert}
        color="bg-red-600"
      />

    </section>
  );
}