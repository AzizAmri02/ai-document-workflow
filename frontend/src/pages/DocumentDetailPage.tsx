import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getDocument, getDocumentText } from "../api/documents";
import { StatusBadge } from "../components/StatusBadge";
import type { DocumentItem, DocumentTextResponse } from "../types";
import { formatDate } from "../utils/formatDate";

export function DocumentDetailPage() {
  const { id } = useParams();
  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [text, setText] = useState<DocumentTextResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [doc, docText] = await Promise.all([getDocument(id), getDocumentText(id)]);
      setDocument(doc);
      setText(docText);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load document");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [id]);

  if (loading) return <p>Loading document...</p>;
  if (!document) return <p className="error">{error ?? "Document not found"}</p>;

  return (
    <div className="stack">
      <Link to="/documents">â† Back to documents</Link>

      <section className="panel">
        <div className="card-header">
          <h1>{document.title}</h1>
          <StatusBadge status={document.status} />
        </div>
        <p className="muted">
          {document.filename} Â· Updated {formatDate(document.updated_at)}
        </p>
      </section>

      <section className="panel">
        <h2>Extracted text</h2>
        <pre className="text-viewer">{text?.extracted_text || "No text extracted."}</pre>
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}