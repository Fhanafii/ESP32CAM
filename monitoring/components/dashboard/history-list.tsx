import { Detection } from "@/types/detection";
import { HistoryCard } from "./history-card";

interface Props {
  detections: Detection[];
  loading: boolean;
}

export function HistoryList({
  detections,
  loading,
}: Props) {

  if (loading) {
    return (
      <div className="rounded-lg border p-8 text-center">
        Loading...
      </div>
    );
  }

  if (detections.length === 0) {
    return (
      <div className="rounded-lg border p-8 text-center">
        Tidak ada data.
      </div>
    );
  }

  return (
    <div className="space-y-4">

      {detections.map((item) => (
        <HistoryCard
          key={item.id}
          detection={item}
        />
      ))}

    </div>
  );

}