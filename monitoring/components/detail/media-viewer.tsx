"use client";

import {
    DetectionImage,
    DetectionVideo,
} from "@/types/detection-detail";

interface Props{
    images?:DetectionImage[];
    video?:DetectionVideo|null;
}

export function MediaViewer({
    images,
    video,
}:Props){

    if(video){

        return(

            <video
                controls
                className="w-full rounded-xl"
                src={video.url}
            />

        );

    }

    if(images?.length){

        return(

            <div className="relative aspect-video">

                <img

                    src={images[0].url}

                    alt="Detection"

                    className="h-full w-full rounded-xl object-cover"

                />

            </div>

        );

    }

    return(

        <div className="flex aspect-video items-center justify-center rounded-xl border">
            Tidak ada media
        </div>
    );
}
