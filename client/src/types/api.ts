export interface Source {
  id: string;
  name: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface Content {
  id: string;
  source_id: string;
  title: string;
  content: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
} 