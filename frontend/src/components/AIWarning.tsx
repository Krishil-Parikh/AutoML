import { useEffect } from 'react';
import { AlertTriangle, CheckCircle, X } from 'lucide-react';

interface AIWarningProps {
  title: string;
  recommendation: string;
  warnings: string[];
  isRecommended: boolean;
  onProceed: () => void;
  onCancel: () => void;
  loading?: boolean;
  details?: string[];
}

export default function AIWarning({
  title,
  recommendation,
  warnings,
  isRecommended,
  onProceed,
  onCancel,
  loading = false,
  details = [],
}: AIWarningProps) {
  // Close on ESC key
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) onCancel();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [loading, onCancel]);

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 p-3 sm:p-4 flex items-center justify-center"
      onClick={() => { if (!loading) onCancel(); }}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-[95vw] sm:max-w-lg max-h-[85vh] animate-scale-in flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`p-4 sm:p-6 border-b-2 ${isRecommended ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
          <div className="flex items-center gap-3">
            {isRecommended ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            )}
            <h3 className="text-lg font-bold text-slate-800">{title}</h3>
          </div>
        </div>

        <div className="p-4 sm:p-6 space-y-4 overflow-y-auto flex-1">
          {/* Recommendation */}
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">AI Recommendation:</span> {recommendation}
            </p>
          </div>

          {/* Planned Actions Details */}
          {details.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-600 uppercase">Planned Actions:</p>
              <ul className="space-y-1 max-h-40 overflow-auto pr-1">
                {details.map((d, idx) => (
                  <li key={idx} className="text-sm text-slate-700 flex gap-2">
                    <span className="text-slate-400 font-bold">•</span>
                    {d}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {warnings.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-600 uppercase">Potential Issues:</p>
              <ul className="space-y-1">
                {warnings.map((warning, idx) => (
                  <li key={idx} className="text-sm text-yellow-700 flex gap-2">
                    <span className="text-yellow-600 font-bold">•</span>
                    {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Status Badge */}
          <div className="flex justify-center">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              isRecommended
                ? 'bg-green-100 text-green-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {isRecommended ? '✓ Recommended' : '⚠️ Proceed with caution'}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="p-3 sm:p-4 bg-slate-50 border-t border-slate-200 flex gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-slate-200 text-slate-700 rounded-lg font-medium hover:bg-slate-300 transition-colors disabled:opacity-50"
          >
            <X className="w-4 h-4 inline mr-1" />
            Cancel
          </button>
          <button
            onClick={onProceed}
            disabled={loading}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all duration-300 text-white ${
              isRecommended
                ? 'bg-green-500 hover:bg-green-600'
                : 'bg-yellow-500 hover:bg-yellow-600'
            } disabled:opacity-50`}
          >
            {loading ? 'Processing…' : 'Proceed'}
          </button>
        </div>
      </div>
    </div>
  );
}
