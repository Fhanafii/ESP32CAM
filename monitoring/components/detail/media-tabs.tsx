"use client";

import { useState } from "react";

import { Tabs,TabsContent,TabsList,TabsTrigger }
from "@/components/ui/tabs";

import { DetectionDetail } from "@/types/detection-detail";

import { MediaViewer } from "./media-viewer";
import { ImageGallery } from "./image-gallery";

interface Props{
    detection:DetectionDetail;
}


export function MediaTabs({
    detection,

}:Props){

    const [selectedImage,setSelectedImage]=useState(0);

    return(

        <Tabs
            defaultValue="images"
            className="space-y-4"
        >
            <TabsList>

                <TabsTrigger value="images">
                    Image
                </TabsTrigger>

                <TabsTrigger value="video">
                    Video
                </TabsTrigger>

            </TabsList>

            <TabsContent value="images">

                <MediaViewer
                    images={
                        detection.images[selectedImage]
                            ? [detection.images[selectedImage]]
                            : []
                    }
                />

                <ImageGallery
                    images={detection.images}
                    selected={selectedImage}
                    onSelect={setSelectedImage}
                />

            </TabsContent>

            <TabsContent value="video">

                <MediaViewer
                    video={detection.video}
                />

            </TabsContent>
        </Tabs>
    );
}
