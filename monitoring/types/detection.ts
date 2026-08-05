export type DetectionStatus =
  | "Normal"
  | "Perlu Dipantau"
  | "Mencurigakan";

export interface Detection {
  id: string;
  batch_number: number;
  detected_at: string;
  total_frames: number;
  detected_frames: number;
  avg_confidence: number;
  presence_ratio: number;
  longest_streak: number;
  suspicion_score: number;
  status: DetectionStatus;
  batch_folder: string;
  thumbnail_path: string;
  video_path: string;
  whatsapp_sent: boolean;
  created_at: string;
}