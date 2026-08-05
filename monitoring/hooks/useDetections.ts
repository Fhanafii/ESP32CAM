"use client";

import { useQuery } from "@tanstack/react-query";
import { getDetections } from "@/services/detection";

export function useDetections(
    params?: Record<string, unknown>
){

    return useQuery({
        queryKey:["detections",params],
        queryFn:()=>getDetections(params)
    });

}