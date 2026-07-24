export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "user" | "reviewer";
}

export interface DocumentItem {
  id: string;
  owner_id: string;
  title: string;
  filename: string;
  file_size_bytes: number;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
}

export type DocumentStatus = "draft" | "pending_review" | "approved" | "rejected";

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  limit: number;
}

export interface DocumentTextResponse {
  document_id: string;
  extracted_text: string;
  page_count: number;
  extracted_at: string;
}