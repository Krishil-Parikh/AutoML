import { useState } from 'react';
import { Loader2, Layers, ChevronRight, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { validateStepWithAI } from '../utils/ai';
import AIWarning from './AIWarning';

interface CorrelationManagerProps {
  sessionId: string;
  aiMode: boolean;
  onComplete: () => void;
}

export default function CorrelationManager({ sessionId, aiMode, onComplete }: CorrelationManagerProps) {
  const [processing, setProcessing] = useState(false);
  const [threshold, setThreshold] = useState(0.90);
  const [showAIWarning, setShowAIWarning] = useState(false);
  const [aiValidation, setAIValidation] = useState<any>(null);

  const handleAutoDrop = async () => {
    if (aiMode && !aiValidation) {
      // First, get preview of which columns will be dropped
      setProcessing(true);
      try {
        console.log(`🔍 Fetching correlation preview for threshold: ${threshold}`);
        const previewRes = await fetch(`${API_BASE_URL}/preview/correlation/${sessionId}?threshold=${threshold}`, {
          method: 'POST',
        });
        const preview = await previewRes.json();
        const columnsToDropList = preview.high_corr_cols || [];
        console.log('📋 Preview result - Columns to drop:', columnsToDropList);

        // Validate with AI, passing the actual columns that will be dropped
        console.log('🤖 Sending to AI with columns:', columnsToDropList);
        const validation = await validateStepWithAI(
          sessionId,
          'correlation',
          `Drop columns with correlation > ${threshold}`,
          columnsToDropList,
        );
        
        if (validation) {
          setAIValidation(validation);
          setShowAIWarning(true);
        }
      } catch (error) {
        console.error('Error getting correlation preview:', error);
      }
      setProcessing(false);
      return;
    }

    // Proceed with actual action
    setProcessing(true);
    setShowAIWarning(false);
    try {
      await fetch(`${API_BASE_URL}/clean/correlation`, {
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
      setAIValidation(null);
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-0">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-4 sm:p-8 border border-slate-200 animate-scale-in">
        <div className="text-center mb-6 sm:mb-8">
          <div className="inline-flex p-3 sm:p-4 bg-gradient-to-br from-violet-500 to-pink-500 rounded-2xl shadow-lg mb-3 sm:mb-4">
            <Layers className="w-8 h-8 sm:w-12 sm:h-12 text-white" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-2">Multicollinearity Check</h2>
          <p className="text-sm sm:text-base text-slate-500">Detect and handle highly correlated features</p>
        </div>

        <div className="bg-violet-50 rounded-xl p-4 sm:p-6 mb-4 sm:mb-6 border border-violet-200">
          <div className="flex items-start space-x-2 sm:space-x-3">
            <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-violet-600 flex-shrink-0 mt-0.5" />
            <div className="w-full">
              <p className="text-xs sm:text-sm text-violet-800 font-medium mb-2">About Correlation</p>
              <p className="text-xs sm:text-sm text-violet-600 mb-3 sm:mb-4">
                Features with correlation higher than the threshold are redundant and can cause model instability. The system will automatically identify and remove these features .
              </p>
              
              {/* Threshold Slider Section */}
              <div className="bg-white/50 rounded-lg p-4 border border-violet-200">
                <div className="flex justify-between items-center mb-2">
                  <label htmlFor="threshold-slider" className="text-sm text-violet-700 font-medium">
                    Correlation Threshold: {(threshold * 100).toFixed(0)}%
                  </label>
                  <span className="text-xs text-violet-500 font-medium bg-violet-100 px-2 py-1 rounded">
                    Recommended: 90%
                  </span>
                </div>
                
                <input
                  id="threshold-slider"
                  type="range"
                  min="0.5"
                  max="1.0"
                  step="0.01"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full h-2 bg-violet-200 rounded-lg appearance-none cursor-pointer accent-violet-600 hover:accent-violet-700 transition-all"
                />
                
                <div className="flex justify-between mt-2 text-xs text-violet-400">
                  <span>50% (Aggressive Removal)</span>
                  <span>100% (Keep All)</span>
                </div>
                
                <p className="text-xs text-violet-600 mt-3 border-t border-violet-100 pt-2">
                  Features with correlation &gt; {(threshold * 100).toFixed(0)}% will be dropped.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3 sm:space-y-4">
          <button
            onClick={handleAutoDrop}
            disabled={processing}
            className="w-full bg-gradient-to-r from-violet-500 to-pink-500 text-white py-3 sm:py-4 px-4 sm:px-6 rounded-xl text-sm sm:text-base font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center space-x-2"
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

        {/* AI Warning Modal */}
        {showAIWarning && aiValidation && (
          <AIWarning
            title="AI Review: Correlation Removal"
            recommendation={aiValidation.recommendation}
            warnings={aiValidation.warnings}
            isRecommended={aiValidation.is_recommended}
            loading={processing}
            onProceed={handleAutoDrop}
            onCancel={() => {
              setShowAIWarning(false);
              setAIValidation(null);
            }}
          />
        )}
      </div>
    </div>
  );
}