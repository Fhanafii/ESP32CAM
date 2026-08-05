import { Header } from "@/components/layout/header";
import { SummaryGrid } from "@/components/dashboard/summary-grid";

export default function HomePage() {
  return (
    <>
      <Header />

      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-6 py-8">

        <SummaryGrid />

      </main>
    </>
  );
}