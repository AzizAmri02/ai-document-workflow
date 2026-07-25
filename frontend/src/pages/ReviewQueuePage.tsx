import { useEffect, useState } from "react";
import { getReviewQueue, updateDocumentStatus } from "../api/documents";
import { DocumentCard } from "../components/DocumentCard";
import type { DocumentItem } from "../types";

export function ReviewQueuePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [comments, setComments] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getReviewQueue();
      setDocuments(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load review queue");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadQueue();
  }, []);

  const handleDecision = async (documentId: string, status: "approved" | "rejected") => {
    if (status === "rejected" && !(comments[documentId] ?? "").trim()) {
      setError("Rejection comment is required");
      return;
    }
    setError(null);
    try {
      await updateDocumentStatus(documentId, status, comments[documentId] || undefined);
      await loadQueue();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Decision failed");
    }
  };

  return (
    <div className="stack">
      <section className="panel">
        <h1>Review Queue</h1>
        {loading ? (
          <p>Loading queue...</p>
        ) : documents.length === 0 ? (
          <p className="muted">No documents waiting for review.</p>
        ) : (
          <div className="grid">
            {documents.map((document) => (
              <article key={document.id} className="card">
                <DocumentCard document={document} />
                <div className="actions">
                  <button type="button" onClick={() => void handleDecision(document.id, "approved")}>
                    Approve
                  </button>
                  <input
                    type="text"
                    placeholder="Rejection comment"
                    value={comments[document.id] ?? ""}
                    onChange={(event) =>
                      setComments((current) => ({ ...current, [document.id]: event.target.value }))
                    }
                  />
                  <button type="button" onClick={() => void handleDecision(document.id, "rejected")}>
                    Reject
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
