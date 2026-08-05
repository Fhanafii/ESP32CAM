"use client";

import { useQuery } from "@tanstack/react-query";
import { getDetection } from "@/services/detection";

export function useDetection(id:string){

    return useQuery({
        queryKey:["detection",id],
        queryFn:()=>getDetection(id),
        enabled:!!id,
    });

}