import { api } from "@/lib/axios";
import { Detection } from "@/types/detection";
import { DetectionDetail } from "@/types/detection-detail";
import { ApiResponse, PaginatedResponse } from "@/types/api";

export async function getDetections(
  params?: Record<string, unknown>
) {
  const { data } =
    await api.get<PaginatedResponse<Detection>>(
      "/api/detections",
      {
        params,
      }
    );

  return data;
}

export async function getDetection(id: string) {
  const { data } =
    await api.get<ApiResponse<DetectionDetail>>(
      `/api/detections/${id}`
    );

  return data;
}