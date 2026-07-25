import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getDocument, getDocumentText, getStatusHistory, updateDocumentStatus } from "../api/documents";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import type { DocumentItem, DocumentTextResponse, StatusHistoryItem } from "../types";
import { formatDate } from "../utils/formatDate";

export function DocumentDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [text, setText] = useState<DocumentTextResponse | null>(null);
  const [history, setHistory] = useState<StatusHistoryItem[]>([]);
  const [comment, setComment] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [doc, docText, docHistory] = await Promise.all([
        getDocument(id),
        getDocumentText(id),
        getStatusHistory(id),
      ]);
      setDocument(doc);
      setText(docText);
      setHistory(docHistory);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load document");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [id]);

  const handleStatusChange = async (status: string) => {
    if (!id) return;
    if (status === "rejected" && !comment.trim()) {
      setError("Rejection comment is required");
      return;
    }
    setError(null);
    try {
      const updated = await updateDocumentStatus(id, status, comment || undefined);
      setDocument(updated);
      setComment("");
      const docHistory = await getStatusHistory(id);
      setHistory(docHistory);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Status update failed");
    }
  };

  if (loading) return <p>Loading document...</p>;
  if (!document) return <p className="error">{error ?? "Document not found"}</p>;

  const isOwner = user?.id === document.owner_id;
  const isReviewer = user?.role === "reviewer";

  return (
    <div className="stack">
      <Link to="/documents">← Back to documents</Link>

      <section className="panel">
        <div className="card-header">
          <h1>{document.title}</h1>
          <StatusBadge status={document.status} />
        </div>
        <p className="muted">
          {document.filename} · Updated {formatDate(document.updated_at)}
        </p>

        <div className="actions">
          {isOwner && document.status === "draft" && (
            <button type="button" onClick={() => void handleStatusChange("pending_review")}>
              Submit for review
            </button>
          )}
          {isOwner && document.status === "rejected" && (
            <>
              <button type="button" onClick={() => void handleStatusChange("draft")}>
                Move back to draft
              </button>
              <button type="button" onClick={() => void handleStatusChange("pending_review")}>
                Resubmit for review
              </button>
            </>
          )}
          {isReviewer && document.status === "pending_review" && (
            <>
              <button type="button" onClick={() => void handleStatusChange("approved")}>
                Approve
              </button>
              <input
                type="text"
                placeholder="Rejection comment"
                value={comment}
                onChange={(event) => setComment(event.target.value)}
              />
              <button type="button" onClick={() => void handleStatusChange("rejected")}>
                Reject
              </button>
            </>
          )}
        </div>
      </section>

      <section className="panel">
        <h2>Extracted text</h2>
        <pre className="text-viewer">{text?.extracted_text || "No text extracted."}</pre>
      </section>

      <section className="panel">
        <h2>Status history</h2>
        {history.length === 0 ? (
          <p className="muted">No status changes yet.</p>
        ) : (
          <ul className="result-list">
            {history.map((entry) => (
              <li key={entry.id}>
                {entry.from_status} → {entry.to_status} · {formatDate(entry.created_at)}
                {entry.comment && <p className="muted">{entry.comment}</p>}
              </li>
            ))}
          </ul>
        )}
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
