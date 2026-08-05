"use client";

import {
Card,
CardContent,
} from "@/components/ui/card";

import { DetectionDetail } from "@/types/detection-detail";

interface Props{
    detection:DetectionDetail;
}

export function DetectionInfo({
    detection,
}:Props){

    const items=[
        ["Confidence",
        `${(detection.avg_confidence)} %`],

        ["Presence Ratio",
        detection.presence_ratio],

        ["Longest Streak",
        detection.longest_streak],

        ["Detected Frame",
        `${detection.detected_frames}/${detection.total_frames}`],

        ["WhatsApp",
        detection.whatsapp_sent?"Ya":"Tidak"],
    ];

    return(
        <Card>
            <CardContent className="space-y-4 p-6">
                {
                    items.map(([title,value])=>(

                        <div
                            key={title}
                            className="flex justify-between"
                        >

                            <span className="text-muted-foreground">
                                {title}
                            </span>

                            <span>
                                {value}
                            </span>

                        </div>
                    ))
                }
            </CardContent>
        </Card>
    );
}