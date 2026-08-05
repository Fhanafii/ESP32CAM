import { api } from "@/lib/axios";
import { DashboardSummary } from "@/types/dashboard";
import { ApiResponse } from "@/types/api";

export async function getDashboard(){

    const { data } =
        await api.get<ApiResponse<DashboardSummary>>("/api/dashboard");

    return data;
}