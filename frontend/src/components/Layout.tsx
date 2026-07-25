import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <Link to="/documents" className="brand">
            AI Document Workflow
          </Link>
          {user && <p className="muted">Signed in as {user.full_name}</p>}
        </div>
        <nav className="nav-links">
          <Link to="/documents">Documents</Link>
          {user?.role === "reviewer" && <Link to="/review">Review Queue</Link>}
          <button
            type="button"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Log out
          </button>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}