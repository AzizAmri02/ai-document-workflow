import { apiRequest } from "./client";
import type { DocumentItem, DocumentListResponse, DocumentTextResponse } from "../types";

export async function uploadDocument(file: File, title?: string): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);
  if (title) {
    formData.append("title", title);
  }
  return apiRequest<DocumentItem>("/api/documents/upload", { method: "POST", body: formData });
}

export async function listDocuments(params: {
  q?: string;
  status?: string;
  page?: number;
  limit?: number;
}): Promise<DocumentListResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.status) search.set("status", params.status);
  if (params.page) search.set("page", String(params.page));
  if (params.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  return apiRequest<DocumentListResponse>(`/api/documents${query ? `?${query}` : ""}`);
}

export async function getDocument(documentId: string): Promise<DocumentItem> {
  return apiRequest<DocumentItem>(`/api/documents/${documentId}`);
}

export async function getDocumentText(documentId: string): Promise<DocumentTextResponse> {
  return apiRequest<DocumentTextResponse>(`/api/documents/${documentId}/text`);
}