import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recordsAPI } from '../services/api';

export default function ReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');

  useEffect(() => {
    const fetchRecord = async () => {
      try {
        setLoading(true);
        const res = await recordsAPI.detail(id);
        console.log('API response:', res.data); // Debug log
        // API wraps data in 'record' key
        setRecord(res.data.record || res.data);
      } catch (err) {
        setError(err.response?.data?.error || err.message);
        console.error('Error fetching record:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecord();
  }, [id]);

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      await recordsAPI.approve(id, {
        status: 'APPROVED',
        anomaly_notes: approvalNotes,
      });
      navigate('/records');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    try {
      setActionLoading(true);
      await recordsAPI.approve(id, {
        status: 'REJECTED',
        anomaly_notes: approvalNotes,
      });
      navigate('/records');
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">Loading record...</div>;
  if (error) return <div className="alert-error">{error}</div>;
  if (!record) return <div className="alert-error">Record not found</div>;

  // Helper function to safely format numbers
  const formatNumber = (value, decimals = 2) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    return parseFloat(value).toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Record Review</h1>
        <button onClick={() => navigate('/records')} className="btn-secondary">
          ← Back to Records
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Record Details */}
        <div className="lg:col-span-2">
          <div className="card p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Record Details</h2>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <div className="text-sm text-gray-600 font-medium">Record ID</div>
                <div className="font-mono text-lg">{record.id}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600 font-medium">Status</div>
                <div className="badge badge-pending">{record.status}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600 font-medium">Scope</div>
                <div className="font-semibold">{record.scope_category}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600 font-medium">Created</div>
                <div>{record.created_at ? new Date(record.created_at).toLocaleString() : 'N/A'}</div>
              </div>
            </div>

            {/* Original vs Normalized */}
            <div className="border-t pt-6">
              <h3 className="font-semibold mb-4">Data Transformation</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <div className="text-xs text-gray-600 font-medium mb-1">Original Value</div>
                  <div className="text-lg font-semibold">
                    {formatNumber(record.original_value, 2)} {record.original_unit || 'unit'}
                  </div>
                </div>
                <div className="bg-breathe-accent/10 p-4 rounded">
                  <div className="text-xs text-gray-600 font-medium mb-1">Normalized Value</div>
                  <div className="text-lg font-semibold">
                    {formatNumber(record.normalized_value, 2)} {record.normalized_unit || 'unit'}
                  </div>
                </div>
              </div>
            </div>

            {/* CO2e Calculation */}
            <div className="border-t pt-6 mt-6">
              <h3 className="font-semibold mb-4">CO₂e Calculation</h3>
              <div className="bg-green-50 border border-green-200 p-4 rounded">
                <div className="text-sm text-green-700 font-medium mb-1">Total CO₂e Emissions</div>
                <div className="text-3xl font-bold text-green-900">
                  {formatNumber(record.calculated_co2e, 2)} kg
                </div>
              </div>
            </div>
          </div>

          {/* Anomaly Flags */}
          {record.anomaly_notes && (
            <div className="card p-6 bg-yellow-50 border-yellow-200 mb-6">
              <h2 className="text-lg font-semibold text-yellow-900 mb-2">⚠️ Anomaly Flags</h2>
              <p className="text-yellow-800 whitespace-pre-wrap">{record.anomaly_notes}</p>
            </div>
          )}
        </div>

        {/* Review Panel */}
        <div className="lg:col-span-1">
          <div className="card p-6 sticky top-8">
            <h2 className="text-lg font-semibold mb-4">Review & Approve</h2>

            <textarea
              placeholder="Add review notes..."
              value={approvalNotes}
              onChange={(e) => setApprovalNotes(e.target.value)}
              className="form-input mb-4 h-24"
            />

            <div className="space-y-3">
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className={`btn w-full ${actionLoading ? 'bg-gray-400' : 'btn-primary'}`}
              >
                {actionLoading ? 'Processing...' : '✓ Approve'}
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading}
                className={`btn w-full ${actionLoading ? 'bg-gray-400' : 'btn-danger'}`}
              >
                {actionLoading ? 'Processing...' : '✗ Reject'}
              </button>
            </div>

            {error && <div className="alert-error mt-4 text-sm">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
