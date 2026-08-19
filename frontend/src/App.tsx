import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

// Pages
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { EvidencePage } from './pages/EvidencePage';
import { EvidenceDetailPage } from './pages/EvidenceDetailPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { TransactionDetailPage } from './pages/TransactionDetailPage';
import { WalletsPage } from './pages/WalletsPage';
import { WalletDetailPage } from './pages/WalletDetailPage';
import { InvestigationGraphPage } from './pages/InvestigationGraphPage';
import { AIAnalysisPage } from './pages/AIAnalysisPage';
import { ExplanationsPage } from './pages/ExplanationsPage';
import { ChainOfCustodyPage } from './pages/ChainOfCustodyPage';
import { IntegrityPage } from './pages/IntegrityPage';
import { BlockchainPage } from './pages/BlockchainPage';
import { ModelsPage } from './pages/ModelsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { AuditPage } from './pages/AuditPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-forensic-bg flex flex-col text-slate-100 selection:bg-blue-600 selection:text-white">
          <Navbar />
          <div className="flex flex-1">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-navy-900/50">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/cases" element={<CasesPage />} />
                <Route path="/cases/:id" element={<CaseDetailPage />} />
                <Route path="/evidence" element={<EvidencePage />} />
                <Route path="/evidence/:id" element={<EvidenceDetailPage />} />
                <Route path="/transactions" element={<TransactionsPage />} />
                <Route path="/transactions/:id" element={<TransactionDetailPage />} />
                <Route path="/wallets" element={<WalletsPage />} />
                <Route path="/wallets/:id" element={<WalletDetailPage />} />
                <Route path="/investigation/graph" element={<InvestigationGraphPage />} />
                <Route path="/ai-analysis" element={<AIAnalysisPage />} />
                <Route path="/explanations" element={<ExplanationsPage />} />
                <Route path="/chain-of-custody" element={<ChainOfCustodyPage />} />
                <Route path="/integrity" element={<IntegrityPage />} />
                <Route path="/blockchain" element={<BlockchainPage />} />
                <Route path="/models" element={<ModelsPage />} />
                <Route path="/evaluation" element={<EvaluationPage />} />
                <Route path="/audit" element={<AuditPage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};
