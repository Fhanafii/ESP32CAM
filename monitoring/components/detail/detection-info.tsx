"use client";

import {
  Card,
  CardContent,
} from "@/components/ui/card";

import { DetectionDetail } from "@/types/detection-detail";

interface Props {
  detection: DetectionDetail;
}

export function DetectionInfo({
  detection,
}: Props) {

  const items = [
    [
      "Lokasi",
      "Jl.B6 gang belakang masjid Al-muhajirin RT 07/ RW 013 Kel.Pejagalan, Kec.Penjaringan, Jakarta Utara",
    ],

    [
      "Confidence",
      `${detection.avg_confidence}%`,
    ],

    [
      "Presence Ratio",
      detection.presence_ratio,
    ],

    [
      "Longest Streak",
      detection.longest_streak,
    ],

    [
      "Detected Frame",
      `${detection.detected_frames}/${detection.total_frames}`,
    ],

    [
      "WhatsApp",
      detection.whatsapp_sent ? "Terkirim" : "Tidak Terkirim",
    ],

    [
      "Created At",
      new Date(detection.created_at).toLocaleString("id-ID"),
    ],
  ];

  return (
    <Card>

      <CardContent className="space-y-4 p-6">

        {items.map(([title, value]) => (

          <div
            key={title}
            className="flex items-start justify-between gap-6"
          >

            <span className="text-muted-foreground">
              {title}
            </span>

            <span className="max-w-xs text-right font-medium">
              {value}
            </span>

          </div>

        ))}

      </CardContent>

    </Card>
  );
}