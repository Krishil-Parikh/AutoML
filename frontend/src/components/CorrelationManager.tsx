import { useState } from 'react';
import { Loader2, Layers, ChevronRight, AlertTriangle } from 'lucide-react';

interface CorrelationManagerProps {
  sessionId: string;
  onComplete: () => void;
}

export default function CorrelationManager({ sessionId, onComplete }: CorrelationManagerProps) {
  const [processing, setProcessing] = useState(false);
  const [threshold] = useState(0.90);

  const handleAutoDrop = async () => {
    setProcessing(true);
    try {
      await fetch('http://localhost:8000/clean/correlation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          threshold,
          auto_drop: true,
        }),
      });
      onComplete();
    } catch (error) {
      console.error('Error handling correlation:', error);
    } finally {
      setProcessing(false);
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200 animate-scale-in">
        <div className="text-center mb-8">
          <div className="inline-flex p-4 bg-gradient-to-br from-violet-500 to-pink-500 rounded-2xl shadow-lg mb-4">
            <Layers className="w-12 h-12 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-slate-800 mb-2">Multicollinearity Check</h2>
          <p className="text-slate-500">Detect and handle highly correlated features</p>
        </div>

        <div className="bg-violet-50 rounded-xl p-6 mb-6 border border-violet-200">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-6 h-6 text-violet-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-violet-800 font-medium mb-2">About Correlation</p>
              <p className="text-sm text-violet-600 mb-3">
                Features with correlation {'>'}90% are redundant and can cause model instability. The system will automatically identify and remove highly correlated features.
              </p>
              <div className="bg-white/50 rounded-lg p-3 border border-violet-200">
                <p className="text-xs text-violet-700 font-medium mb-1">Threshold: {threshold * 100}%</p>
                <p className="text-xs text-violet-600">Features above this correlation will be dropped</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <button
            onClick={handleAutoDrop}
            disabled={processing}
            className="w-full bg-gradient-to-r from-violet-500 to-pink-500 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center space-x-2"
          >
            {processing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Checking Correlations...</span>
              </>
            ) : (
              <>
                <span>Auto-Remove Correlated Features</span>
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>

          <button
            onClick={handleSkip}
            disabled={processing}
            className="w-full bg-slate-200 text-slate-700 py-4 px-6 rounded-xl font-semibold hover:bg-slate-300 transition-all duration-300 disabled:opacity-50"
          >
            Skip This Step
          </button>
        </div>
      </div>
    </div>
  );
}
