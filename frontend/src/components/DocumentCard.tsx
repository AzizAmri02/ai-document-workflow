import { Link } from "react-router-dom";
import type { DocumentItem } from "../types";
import { formatDate, formatFileSize } from "../utils/formatDate";
import { StatusBadge } from "./StatusBadge";

export function DocumentCard({ document }: { document: DocumentItem }) {
  return (
    <article className="card">
      <div className="card-header">
        <h3>{document.title}</h3>
        <StatusBadge status={document.status} />
      </div>
      <p className="muted">
        {document.filename} · {formatFileSize(document.file_size_bytes)} · {formatDate(document.created_at)}
      </p>
      <Link className="button-link" to={`/documents/${document.id}`}>
        View details
      </Link>
    </article>
  );
}
