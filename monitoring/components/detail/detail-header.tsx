"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DetectionDetail } from "@/types/detection-detail";

interface Props{
    detection:DetectionDetail;
}

export function DetailHeader({
    detection,
}:Props){

    const color=
        detection.status==="Normal"
            ?"bg-green-600"
        :detection.status==="Perlu Dipantau"
            ?"bg-yellow-500"
            :"bg-red-600";

    return(

        <div className="space-y-4">

            <Link
                href="/"
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
            >
                <ArrowLeft className="h-4 w-4" />
                Kembali
            </Link>

            <div className="flex items-center justify-between">

                <div>

                    <h1 className="text-3xl font-bold">
                        Batch #{detection.batch_number}
                    </h1>

                    <p className="text-muted-foreground">

                        {new Date(
                            detection.detected_at
                        ).toLocaleString("id-ID")}

                    </p>

                </div>

                <Badge className={color}>
                    {detection.status}
                </Badge>
            </div>
        </div>
    );
}