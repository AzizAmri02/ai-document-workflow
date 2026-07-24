import { FormEvent, useEffect, useState } from "react";
import { listDocuments, uploadDocument } from "../api/documents";
import { DocumentCard } from "../components/DocumentCard";
import { SearchFilterBar } from "../components/SearchFilterBar";
import type { DocumentItem } from "../types";

export function DocumentListPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listDocuments({ q: query || undefined, status: status || undefined });
      setDocuments(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const handleUpload = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file, title || undefined);
      setFile(null);
      setTitle("");
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="stack">
      <section className="panel">
        <h1>Documents</h1>
        <form className="upload-form" onSubmit={handleUpload}>
          <input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <input type="text" placeholder="Optional title" value={title} onChange={(event) => setTitle(event.target.value)} />
          <button type="submit" disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload PDF"}
          </button>
        </form>
      </section>

      <section className="panel">
        <SearchFilterBar
          query={query}
          status={status}
          onQueryChange={setQuery}
          onStatusChange={setStatus}
          onSearch={() => void loadDocuments()}
        />
        {loading ? (
          <p>Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="muted">No documents yet. Upload your first PDF to get started.</p>
        ) : (
          <div className="grid">
            {documents.map((document) => (
              <DocumentCard key={document.id} document={document} />
            ))}
          </div>
        )}
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}