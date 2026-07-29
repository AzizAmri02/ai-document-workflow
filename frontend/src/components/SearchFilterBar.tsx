interface SearchFilterBarProps {
  query: string;
  status: string;
  uploadedFrom: string;
  uploadedTo: string;
  sort: string;
  onQueryChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onUploadedFromChange: (value: string) => void;
  onUploadedToChange: (value: string) => void;
  onSortChange: (value: string) => void;
  onSearch: () => void;
}

export function SearchFilterBar({
  query,
  status,
  uploadedFrom,
  uploadedTo,
  sort,
  onQueryChange,
  onStatusChange,
  onUploadedFromChange,
  onUploadedToChange,
  onSortChange,
  onSearch,
}: SearchFilterBarProps) {
  return (
    <div className="toolbar">
      <input
        type="search"
        placeholder="Search title, filename, or content"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />
      <select value={status} onChange={(event) => onStatusChange(event.target.value)}>
        <option value="">All statuses</option>
        <option value="draft">Draft</option>
        <option value="pending_review">Pending Review</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
      </select>
      <label className="inline-field">
        From
        <input
          type="date"
          value={uploadedFrom}
          onChange={(event) => onUploadedFromChange(event.target.value)}
        />
      </label>
      <label className="inline-field">
        To
        <input type="date" value={uploadedTo} onChange={(event) => onUploadedToChange(event.target.value)} />
      </label>
      <select value={sort} onChange={(event) => onSortChange(event.target.value)}>
        <option value="created_at">Newest first</option>
        <option value="created_at_asc">Oldest first</option>
      </select>
      <button type="button" onClick={onSearch}>
        Search
      </button>
    </div>
  );
}
