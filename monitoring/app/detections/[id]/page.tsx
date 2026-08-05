"use client";

import { useParams } from "next/navigation";

import { DetectionInfo } from "@/components/detail/detection-info";
import { DetailHeader } from "@/components/detail/detail-header";
import { MediaTabs } from "@/components/detail/media-tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useDetection } from "@/hooks/useDetection";

export default function DetectionDetailPage(){

    const { id } = useParams();

    const query=

        useDetection(id as string);

    if(query.isLoading){
        return (
            <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-96 w-full" />
            </main>
        );
    }

    if(query.isError){
        return (
            <main className="mx-auto max-w-7xl px-6 py-8">
                Gagal mengambil data.
            </main>
        );
    }

    const detection=query.data?.data;

    if(!detection){
        return (
            <main className="mx-auto max-w-7xl px-6 py-8">
                Data tidak ditemukan.
            </main>
        );
    }

    return(
        <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">
            <DetailHeader detection={detection} />

            <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
                <MediaTabs detection={detection} />
                <DetectionInfo detection={detection} />
            </div>
        </main>
    );
}
