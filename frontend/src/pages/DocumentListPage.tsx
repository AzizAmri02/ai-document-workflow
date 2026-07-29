import { FormEvent, useEffect, useState } from "react";
import { listDocuments, uploadDocument } from "../api/documents";
import { DocumentCard } from "../components/DocumentCard";
import { SearchFilterBar } from "../components/SearchFilterBar";
import type { DocumentItem } from "../types";

const PAGE_SIZE = 6;

export function DocumentListPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [uploadedFrom, setUploadedFrom] = useState("");
  const [uploadedTo, setUploadedTo] = useState("");
  const [sort, setSort] = useState("created_at");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadDocuments = async (targetPage = page) => {
    setLoading(true);
    setError(null);
    try {
      const response = await listDocuments({
        q: query || undefined,
        status: status || undefined,
        uploaded_from: uploadedFrom || undefined,
        uploaded_to: uploadedTo || undefined,
        sort,
        page: targetPage,
        limit: PAGE_SIZE,
      });
      setDocuments(response.items);
      setTotal(response.total);
      setPage(response.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadDocuments(1);
  }, []);

  const handleSearch = () => {
    void loadDocuments(1);
  };

  const handleUpload = async (event: FormEvent) => {
    event.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file, title || undefined);
      setFile(null);
      setTitle("");
      await loadDocuments(1);
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
          uploadedFrom={uploadedFrom}
          uploadedTo={uploadedTo}
          sort={sort}
          onQueryChange={setQuery}
          onStatusChange={setStatus}
          onUploadedFromChange={setUploadedFrom}
          onUploadedToChange={setUploadedTo}
          onSortChange={setSort}
          onSearch={handleSearch}
        />
        {loading ? (
          <p>Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="muted">No documents match your search.</p>
        ) : (
          <>
            <p className="muted">
              Showing {documents.length} of {total} documents
            </p>
            <div className="grid">
              {documents.map((document) => (
                <DocumentCard key={document.id} document={document} />
              ))}
            </div>
            <div className="pagination">
              <button type="button" disabled={page <= 1} onClick={() => void loadDocuments(page - 1)}>
                Previous
              </button>
              <span className="muted">
                Page {page} of {totalPages}
              </span>
              <button type="button" disabled={page >= totalPages} onClick={() => void loadDocuments(page + 1)}>
                Next
              </button>
            </div>
          </>
        )}
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
