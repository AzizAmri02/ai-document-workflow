import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute, ReviewerRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./hooks/useAuth";
import { DocumentDetailPage } from "./pages/DocumentDetailPage";
import { DocumentListPage } from "./pages/DocumentListPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ReviewQueuePage } from "./pages/ReviewQueuePage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/documents" replace />} />
            <Route path="/documents" element={<DocumentListPage />} />
            <Route path="/documents/:id" element={<DocumentDetailPage />} />
            <Route element={<ReviewerRoute />}>
              <Route path="/review" element={<ReviewQueuePage />} />
            </Route>
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/documents" replace />} />
      </Routes>
    </AuthProvider>
  );
}
