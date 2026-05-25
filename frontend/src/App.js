import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import RecordsPage from './pages/RecordsPage';
import ReviewPage from './pages/ReviewPage';

export default function App() {
  const [activeCompanyId, setActiveCompanyId] = useState(1);

  return (
    <Router>
      <div className="container-app">
        {/* Navigation Header */}
        <nav className="bg-breathe-primary text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-breathe-accent rounded-lg flex items-center justify-center font-bold">
                B
              </div>
              <span className="text-2xl font-bold">Breathe ESG</span>
            </div>
            
            <ul className="flex gap-6">
              <li>
                <Link to="/" className="hover:text-breathe-accent transition">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/upload" className="hover:text-breathe-accent transition">
                  Upload
                </Link>
              </li>
              <li>
                <Link to="/records" className="hover:text-breathe-accent transition">
                  Records
                </Link>
              </li>
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard companyId={activeCompanyId} />} />
            <Route path="/upload" element={<UploadPage companyId={activeCompanyId} />} />
            <Route path="/records" element={<RecordsPage companyId={activeCompanyId} />} />
            <Route path="/records/:id/review" element={<ReviewPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-gray-100 text-center py-4 mt-12 text-gray-600 text-sm">
          <p>Breathe ESG Data Ingestion & Audit Platform © 2024</p>
        </footer>
      </div>
    </Router>
  );
}
