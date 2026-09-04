import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/AppShell";
import { TodayPage } from "./pages/Today";
import { NewAnalysisPage } from "./pages/NewAnalysis";
import { AnalysesPage } from "./pages/Analyses";
import { WorkspacePage } from "./pages/Workspace";
import { InvestigationPage } from "./pages/Investigation";
import { DashboardPage } from "./pages/Dashboard";
import { EvidencePage } from "./pages/Evidence";
import { ReportPage } from "./pages/Report";
import { DataPage } from "./pages/Data";
import { SemanticsPage } from "./pages/Semantics";
import { EvaluationPage } from "./pages/Evaluation";
import { SettingsPage } from "./pages/Settings";
import { ErrorBoundary } from "./components/ErrorBoundary";

// React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      retry: 2,
      refetchOnWindowFocus: true,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <BrowserRouter>
          <Routes>
            {/* Root redirects to Today */}
            <Route index element={<Navigate to="/today" replace />} />

            {/* Main app shell with navigation */}
            <Route element={<AppShell />}>
              {/* Today - Home page */}
              <Route path="/today" element={<TodayPage />} />

              {/* New Analysis */}
              <Route path="/analysis/new" element={<NewAnalysisPage />} />

              {/* Analyses - History list */}
              <Route path="/analyses" element={<AnalysesPage />} />

              {/* Analysis sub-pages */}
              <Route path="/analyses/:taskId" element={<WorkspacePage />} />
              <Route path="/analyses/:taskId/investigation" element={<InvestigationPage />} />
              <Route path="/analyses/:taskId/dashboard" element={<DashboardPage />} />
              <Route path="/analyses/:taskId/evidence" element={<EvidencePage />} />
              <Route path="/analyses/:taskId/report" element={<ReportPage />} />

              {/* Data */}
              <Route path="/data" element={<DataPage />} />

              {/* Semantics */}
              <Route path="/semantics" element={<SemanticsPage />} />

              {/* Evaluation */}
              <Route path="/evaluation" element={<EvaluationPage />} />

              {/* Settings */}
              <Route path="/settings" element={<SettingsPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<Navigate to="/today" replace />} />
          </Routes>
        </BrowserRouter>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App;
