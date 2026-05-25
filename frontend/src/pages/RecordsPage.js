import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { recordsAPI } from '../services/api';

export default function RecordsPage({ companyId }) {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    scope: '',
  });
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        setLoading(true);
        const params = {
          company_id: companyId,
          page: page,
          ...Object.fromEntries(
            Object.entries(filters).filter(([_, v]) => v !== '')
          ),
        };
        const res = await recordsAPI.list(params);
        setRecords(res.data.results || res.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, [companyId, page, filters]);

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'PENDING': return 'badge-pending';
      case 'SUSPICIOUS': return 'badge-suspicious';
      case 'APPROVED': return 'badge-approved';
      case 'REJECTED': return 'badge-rejected';
      default: return 'badge-pending';
    }
  };

  if (loading) return <div className="text-center py-8">Loading records...</div>;
  if (error) return <div className="alert-error">{error}</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Emission Records</h1>

      {/* Filters */}
      <div className="card p-4 mb-6 flex gap-4">
        <select
          value={filters.status}
          onChange={(e) => { setFilters({ ...filters, status: e.target.value }); setPage(1); }}
          className="form-input"
        >
          <option value="">All Status</option>
          <option value="PENDING">Pending</option>
          <option value="SUSPICIOUS">Suspicious</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>

        <select
          value={filters.scope}
          onChange={(e) => { setFilters({ ...filters, scope: e.target.value }); setPage(1); }}
          className="form-input"
        >
          <option value="">All Scopes</option>
          <option value="SCOPE_1">Scope 1 (Direct)</option>
          <option value="SCOPE_2">Scope 2 (Indirect - Energy)</option>
          <option value="SCOPE_3">Scope 3 (Indirect - Other)</option>
        </select>
      </div>

      {/* Records Table */}
      <div className="card overflow-hidden">
        <table className="table-base">
          <thead>
            <tr>
              <th>Source</th>
              <th>Scope</th>
              <th>Value</th>
              <th>CO₂e (kg)</th>
              <th>Status</th>
              <th>Created</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center py-8 text-gray-500">
                  No records found. Upload data to get started.
                </td>
              </tr>
            ) : (
              records.map(record => (
                <tr key={record.id} className="hover:bg-gray-50 cursor-pointer">
                  <td>{record.activity_type || 'SAP'}</td>
                  <td>{record.scope_category}</td>
                  <td>
                    {parseFloat(record.normalized_value || 0).toFixed(2)} {record.normalized_unit}
                  </td>
                  <td>
                    {parseFloat(record.calculated_co2e || 0).toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(record.status)}`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="text-sm text-gray-600">
                    {record.created_at ? new Date(record.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td>
                    <button
                      onClick={() => navigate(`/records/${record.id}/review`)}
                      className="text-breathe-accent hover:underline text-sm font-medium"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
