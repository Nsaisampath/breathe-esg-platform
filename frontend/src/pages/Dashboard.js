import React, { useState, useEffect } from 'react';
import { recordsAPI } from '../services/api';

export default function Dashboard({ companyId }) {
  const [stats, setStats] = useState({
    total_records: 0,
    pending: 0,
    suspicious: 0,
    approved: 0,
    rejected: 0,
    total_co2e: '0.00',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const res = await recordsAPI.summary(companyId);
        setStats(res.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [companyId]);

  if (loading) return <div className="text-center py-8">Loading dashboard...</div>;
  if (error) return <div className="alert-error">{error}</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total Records Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Total Records</h2>
          <div className="text-4xl font-bold text-breathe-primary">
            {stats.total_records}
          </div>
        </div>

        {/* Pending Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Pending Review</h2>
          <div className="text-4xl font-bold text-yellow-600">
            {stats.pending}
          </div>
        </div>

        {/* Suspicious Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Flagged Anomalies</h2>
          <div className="text-4xl font-bold text-red-600">
            {stats.suspicious}
          </div>
        </div>

        {/* Approved Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Approved Records</h2>
          <div className="text-4xl font-bold text-green-600">
            {stats.approved}
          </div>
        </div>

        {/* Rejected Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Rejected Records</h2>
          <div className="text-4xl font-bold text-gray-600">
            {stats.rejected}
          </div>
        </div>

        {/* Total CO2e Card */}
        <div className="card p-6">
          <h2 className="text-gray-600 text-sm font-medium mb-2">Total CO₂e (kg)</h2>
          <div className="text-4xl font-bold text-breathe-accent">
            {parseFloat(stats.total_co2e).toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 card p-6">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <a href="/upload" className="btn-primary">
            Upload New Data
          </a>
          <a href="/records" className="btn-secondary">
            View All Records
          </a>
        </div>
      </div>
    </div>
  );
}
