"use client";

import Image from "next/image";

import { DetectionImage } from "@/types/detection-detail";

interface Props{
    images:DetectionImage[];
    selected:number;
    onSelect:(index:number)=>void;
}

export function ImageGallery({
    images,
    selected,
    onSelect,
}:Props){

    if(images.length===0){
        return null;
    }

    return(

        <div className="mt-4 flex gap-3 overflow-x-auto">
            {
                images.map((image)=>(
                    <button
                        type="button"
                        key={image.name}
                        onClick={() => onSelect(images.indexOf(image))}
                        className={[
                            "relative h-20 w-28 flex-shrink-0 overflow-hidden rounded-lg border",
                            images.indexOf(image) === selected
                                ? "ring-2 ring-primary"
                                : "",
                        ].join(" ")}
                    >
                        <img
                            src={image.url}
                            alt={image.name}
                            className="h-full w-full object-cover"
                        />
                    </button>
                ))
            }
        </div>
    );
}
