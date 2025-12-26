import { useState, useEffect } from 'react';
import { Loader2, Trash2, ChevronRight, Database, Info } from 'lucide-react';

interface Column {
  id: number;
  column_name: string;
  dtype: string;
  percentage_unique: number;
  percentage_missing: number;
}

interface ColumnManagerProps {
  sessionId: string;
  onComplete: () => void;
  onDataShapeChange: (shape: [number, number]) => void;
}

export default function ColumnManager({ sessionId, onComplete, onDataShapeChange }: ColumnManagerProps) {
  const [columns, setColumns] = useState<Column[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchColumns();
  }, [sessionId]);

  const fetchColumns = async () => {
    try {
      // const response = await fetch(`http://localhost:8000/info/${sessionId});
      const response = await fetch(`https://automl-1smu.onrender.com/info/${sessionId}`);
      const data = await response.json();
      setColumns(data.columns);
      onDataShapeChange(data.shape);
    } catch (error) {
      console.error('Error fetching columns:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (id: number) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedIds(newSet);
  };

  const handleDrop = async () => {
    if (selectedIds.size === 0) {
      onComplete();
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch('https://automl-1smu.onrender.com/clean/drop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          column_ids: Array.from(selectedIds),
        }),
      });
      const data = await response.json();
      setColumns(data.columns);
      setSelectedIds(new Set());
      onDataShapeChange([data.columns.length > 0 ? columns.length : 0, data.columns.length]);
    } catch (error) {
      console.error('Error dropping columns:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200 animate-scale-in">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Column Management</h2>
              <p className="text-sm text-slate-500">Select columns to drop from your dataset</p>
            </div>
          </div>
          {selectedIds.size > 0 && (
            <span className="px-4 py-2 bg-red-100 text-red-700 rounded-xl font-semibold animate-bounce-subtle">
              {selectedIds.size} selected
            </span>
          )}
        </div>

        <div className="bg-slate-50 rounded-xl p-4 mb-6 border border-slate-200">
          <div className="flex items-start space-x-2">
            <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-slate-600">
              Click on rows to select columns you want to remove. Columns with high missing values or low uniqueness might be candidates for removal.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-slate-100 to-slate-50">
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Column</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Type</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Unique %</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Missing %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {columns.map((col, idx) => (
                <tr
                  key={col.id}
                  onClick={() => toggleColumn(col.id)}
                  className={`cursor-pointer transition-all duration-300 ${
                    selectedIds.has(col.id)
                      ? 'bg-red-50 hover:bg-red-100 scale-[0.99]'
                      : idx % 2 === 0
                      ? 'bg-white hover:bg-blue-50'
                      : 'bg-slate-50/50 hover:bg-blue-50'
                  }`}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-5 h-5 rounded border-2 transition-all duration-300 flex items-center justify-center ${
                          selectedIds.has(col.id)
                            ? 'bg-red-500 border-red-500'
                            : 'border-slate-300'
                        }`}
                      >
                        {selectedIds.has(col.id) && <Trash2 className="w-3 h-3 text-white" />}
                      </div>
                      <span className="font-medium text-slate-800">{col.column_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    <span className="px-2 py-1 bg-slate-200 rounded-md font-mono text-xs">{col.dtype}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    <span className={`font-semibold ${col.percentage_unique < 1 ? 'text-orange-600' : 'text-slate-700'}`}>
                      {col.percentage_unique.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    <span className={`font-semibold ${col.percentage_missing > 50 ? 'text-red-600' : col.percentage_missing > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                      {col.percentage_missing.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex space-x-4">
          <button
            onClick={handleSkip}
            disabled={processing}
            className="flex-1 bg-slate-200 text-slate-700 py-4 px-6 rounded-xl font-semibold hover:bg-slate-300 transition-all duration-300 disabled:opacity-50"
          >
            Skip
          </button>
          <button
            onClick={handleDrop}
            disabled={processing}
            className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center space-x-2"
          >
            {processing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>{selectedIds.size > 0 ? `Drop & Continue` : 'Continue'}</span>
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
