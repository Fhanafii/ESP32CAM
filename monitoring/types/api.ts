export interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export interface PaginatedResponse<T> {
  success: boolean;

  page: number;

  limit: number;

  total: number;

  total_pages: number;

  count: number;

  data: T[];
}