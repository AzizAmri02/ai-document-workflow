interface SearchFilterBarProps {
  query: string;
  status: string;
  onQueryChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onSearch: () => void;
}

export function SearchFilterBar({
  query,
  status,
  onQueryChange,
  onStatusChange,
  onSearch,
}: SearchFilterBarProps) {
  return (
    <div className="toolbar">
      <input
        type="search"
        placeholder="Search title or content"
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
      <button type="button" onClick={onSearch}>
        Search
      </button>
    </div>
  );
}
