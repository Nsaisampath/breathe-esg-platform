import React, { useState } from 'react';
import { uploadsAPI } from '../services/api';

export default function UploadPage({ companyId }) {
  const [uploadType, setUploadType] = useState('sap');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Read file content as text
      const fileContent = await file.text();

      const formData = new FormData();
      formData.append('file_content', fileContent);
      formData.append('filename', file.name);
      formData.append('company_id', companyId);

      let response;
      if (uploadType === 'sap') {
        response = await uploadsAPI.uploadSAP(formData);
      } else if (uploadType === 'utility') {
        response = await uploadsAPI.uploadUtility(formData);
      } else if (uploadType === 'travel') {
        response = await uploadsAPI.uploadTravel(formData);
      }

      setResult(response.data);
      setFile(null);
      document.querySelector('input[type="file"]').value = '';
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Upload ESG Data</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Form */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Select Data Source</h2>
          
          <form onSubmit={handleUpload}>
            {/* Upload Type Selection */}
            <div className="mb-6">
              <label className="form-label">Data Source Type</label>
              <div className="space-y-2">
                {[
                  { id: 'sap', label: 'SAP Fuel Data', desc: 'Vehicle fuel consumption (CSV)' },
                  { id: 'utility', label: 'Utility Energy Data', desc: 'Electricity consumption (CSV)' },
                  { id: 'travel', label: 'Business Travel Data', desc: 'Flight records (JSON)' }
                ].map(option => (
                  <label key={option.id} className="flex items-center p-3 border border-gray-200 rounded cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      value={option.id}
                      checked={uploadType === option.id}
                      onChange={(e) => setUploadType(e.target.value)}
                      className="mr-3"
                    />
                    <div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-sm text-gray-600">{option.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* File Input */}
            <div className="mb-6">
              <label className="form-label">Select File</label>
              <input
                type="file"
                onChange={handleFileChange}
                accept={uploadType === 'travel' ? '.json' : '.csv'}
                className="form-input cursor-pointer"
              />
            </div>

            {/* Error Message */}
            {error && <div className="alert-error mb-4">{error}</div>}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`btn ${loading ? 'bg-gray-400' : 'btn-primary'} w-full`}
            >
              {loading ? 'Uploading...' : 'Upload File'}
            </button>
          </form>
        </div>

        {/* Upload Instructions */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Format Guide</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-sm mb-2">SAP CSV Format</h3>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
{`MANDT,WERKS,MENGE,MEINS,BUDAT
100,1000,2500,L,2024-01-15
100,1000,1500,L,2024-01-16`}
              </pre>
            </div>

            <div>
              <h3 className="font-semibold text-sm mb-2">Utility CSV Format</h3>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
{`MeterID,BillingStart,BillingEnd,kWh
M001,2024-01-01,2024-01-31,5000
M001,2024-02-01,2024-02-29,4800`}
              </pre>
            </div>

            <div>
              <h3 className="font-semibold text-sm mb-2">Travel JSON Format</h3>
              <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
{`[
  {"from_airport":"DEL","to_airport":"BLR","date":"2024-01-15"},
  {"from_airport":"BLR","to_airport":"BOM","date":"2024-01-20"}
]`}
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Result */}
      {result && (
        <div className="mt-8 card p-6 bg-green-50 border-green-200">
          <h2 className="text-lg font-semibold text-green-900 mb-4">✓ Upload Successful</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-green-700">Records Created</div>
              <div className="text-2xl font-bold text-green-900">{result.records_created}</div>
            </div>
            <div>
              <div className="text-sm text-green-700">Errors</div>
              <div className="text-2xl font-bold text-green-900">{result.errors_count}</div>
            </div>
          </div>
          {result.errors && result.errors.length > 0 && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <h3 className="font-semibold text-green-900 mb-2">Errors:</h3>
              <ul className="text-sm text-green-800 space-y-1">
                {result.errors.map((err, idx) => (
                  <li key={idx}>• {err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
