import { apiRequest } from "./client";
import type { DocumentItem, DocumentListResponse, DocumentTextResponse, StatusHistoryItem } from "../types";

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
  uploaded_from?: string;
  uploaded_to?: string;
  sort?: string;
  page?: number;
  limit?: number;
}): Promise<DocumentListResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.status) search.set("status", params.status);
  if (params.uploaded_from) search.set("uploaded_from", params.uploaded_from);
  if (params.uploaded_to) search.set("uploaded_to", params.uploaded_to);
  if (params.sort) search.set("sort", params.sort);
  if (params.page) search.set("page", String(params.page));
  if (params.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  return apiRequest<DocumentListResponse>(`/api/documents${query ? `?${query}` : ""}`);
}

export async function getReviewQueue(): Promise<DocumentListResponse> {
  return apiRequest<DocumentListResponse>("/api/documents/review-queue");
}

export async function getDocument(documentId: string): Promise<DocumentItem> {
  return apiRequest<DocumentItem>(`/api/documents/${documentId}`);
}

export async function getDocumentText(documentId: string): Promise<DocumentTextResponse> {
  return apiRequest<DocumentTextResponse>(`/api/documents/${documentId}/text`);
}

export async function updateDocumentStatus(
  documentId: string,
  status: string,
  comment?: string
): Promise<DocumentItem> {
  return apiRequest<DocumentItem>(`/api/documents/${documentId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status, comment }),
  });
}

export async function getStatusHistory(documentId: string): Promise<StatusHistoryItem[]> {
  return apiRequest<StatusHistoryItem[]>(`/api/documents/${documentId}/history`);
}
