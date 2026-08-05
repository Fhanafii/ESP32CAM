import Link from "next/link";
import {
    Card,
    CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Detection } from "@/types/detection";
import { getStatusBadgeClass } from "@/lib/status";

interface Props{
    detection:Detection;
}

export function HistoryCard({
    detection,
}:Props){

    return(
        <Link href={`/detections/${detection.id}`}>

            <Card className="cursor-pointer transition hover:shadow-md">

                <CardContent className="flex items-center gap-4 p-4">

                    <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-muted">
                        No Image
                    </div>

                    <div className="flex-1">

                        <h3 className="font-semibold">
                            Batch #{detection.batch_number}
                        </h3>

                        <p className="text-sm text-muted-foreground">

                            {new Date(detection.detected_at)
                                .toLocaleString("id-ID")}
                        </p>

                        <p className="mt-2 text-sm">
                            Confidence
                            {" "}
                            {(detection.avg_confidence)}%
                        </p>
                    </div>

                    <Badge className={getStatusBadgeClass(detection.status)}>
                        {detection.status}
                    </Badge>
                </CardContent>
            </Card>
        </Link>
    );
}