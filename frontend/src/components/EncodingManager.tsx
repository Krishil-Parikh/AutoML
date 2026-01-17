import { useState, useEffect } from 'react';
import { Loader2, Settings, ChevronRight, Lightbulb, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { validateStepWithAI } from '../utils/ai';
import AIWarning from './AIWarning';

interface Suggestion {
  column: string;
  unique: number;
  suggested_action: string;
}

interface EncodingManagerProps {
  sessionId: string;
  aiMode: boolean;
  onComplete: () => void;
}

export default function EncodingManager({ sessionId, aiMode, onComplete }: EncodingManagerProps): JSX.Element | null {
  const [suggestions, setSuggestions] = useState<Record<number, Suggestion>>({});
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [plan, setPlan] = useState<Record<string, number[]>>({});
  const [customizing, setCustomizing] = useState(false);
  const [showAIWarning, setShowAIWarning] = useState(false);
  const [aiValidation, setAIValidation] = useState<any>(null);

  useEffect(() => {
    fetchSuggestions();
  }, [sessionId]);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/suggestions/encoding/${sessionId}`);
      const data = await response.json();
      setSuggestions(data);

      if (Object.keys(data).length === 0) {
        onComplete();
        return;
      }

      const initialPlan: Record<string, number[]> = {};
      Object.entries(data).forEach(([id, sug]: [string, any]) => {
        const action = sug.suggested_action;
        if (!initialPlan[action]) initialPlan[action] = [];
        initialPlan[action].push(Number(id));
      });
      setPlan(initialPlan);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleColumnAction = (colId: number, action: string) => {
    const newPlan = { ...plan };

    Object.keys(newPlan).forEach(key => {
      newPlan[key] = newPlan[key].filter(id => id !== colId);
    });

    if (!newPlan[action]) newPlan[action] = [];
    newPlan[action].push(colId);

    setPlan(newPlan);
  };

  const handleApply = async () => {
    if (aiMode && !aiValidation) {
      // Preview impact
      setProcessing(true);
      try {
        const previewRes = await fetch(
          `${API_BASE_URL}/preview/encoding/${sessionId}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(plan),
          }
        );
        const preview = await previewRes.json();
        const affectedCols = [
          ...(preview.label_encoded_columns || []),
          ...(preview.onehot_encoded_columns || []),
        ];

        // Validate with AI
        const actionDesc = `Apply encoding: ${
          plan.label_encode?.length > 0
            ? `label encode ${plan.label_encode.length} column(s)`
            : ''
        }${
          plan.label_encode?.length > 0 && plan.onehot_encode?.length > 0
            ? ' and '
            : ''
        }${
          plan.onehot_encode?.length > 0
            ? `one-hot encode ${plan.onehot_encode.length} column(s)`
            : ''
        }`;

        const validation = await validateStepWithAI(
          sessionId,
          'encoding',
          actionDesc,
          affectedCols
        );
        if (validation) {
          setAIValidation(validation);
          setShowAIWarning(true);
        }
      } catch (error) {
        console.error('Error previewing encoding:', error);
      } finally {
        setProcessing(false);
      }
      return;
    }

    // Proceed with action (if no AI or user clicked proceed) - keep modal visible
    setProcessing(true);
    try {
      await fetch(`${API_BASE_URL}/clean/encoding`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          plan,
        }),
      });
      onComplete();
    } catch (error) {
      console.error('Error applying plan:', error);
    } finally {
      setProcessing(false);
      setAIValidation(null);
      setShowAIWarning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (Object.keys(suggestions).length === 0) {
    return null;
  }

  const getActionForColumn = (colId: number) => {
    for (const [action, ids] of Object.entries(plan)) {
      if (ids.includes(colId)) return action;
    }
    return 'label';
  };

  const actionColors: Record<string, string> = {
    one_hot: 'bg-blue-100 text-blue-700 border-blue-300',
    label: 'bg-green-100 text-green-700 border-green-300',
    skip: 'bg-slate-100 text-slate-700 border-slate-300',
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-0">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-4 sm:p-8 border border-slate-200 animate-scale-in">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 sm:mb-6 gap-3 sm:gap-0">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="p-2 sm:p-3 bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl">
              <Settings className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Categorical Encoding</h2>
              <p className="text-sm text-slate-500">Convert text features to numbers</p>
            </div>
          </div>
          <button
            onClick={() => setCustomizing(!customizing)}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2"
          >
            <Lightbulb className="w-4 h-4" />
            <span>{customizing ? 'View Suggestions' : 'Customize'}</span>
          </button>
        </div>

        <div className="bg-amber-50 rounded-xl p-4 mb-6 border border-amber-200">
          <div className="flex items-start space-x-2">
            <Lightbulb className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-amber-800 font-medium mb-2">AI Suggestions Applied</p>
              <p className="text-xs text-amber-600">
                One-Hot: Low cardinality ({'<'}10 unique) • Label: High cardinality ({'>'}10 unique)
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {Object.entries(suggestions).map(([id, sug]) => {
            const colId = Number(id);
            const currentAction = getActionForColumn(colId);

            return (
              <div
                key={id}
                className="bg-slate-50 rounded-xl p-4 border-2 border-transparent hover:border-amber-200 transition-all duration-300 animate-slide-in"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-slate-800">{sug.column}</h3>
                      <span className="px-3 py-1 bg-slate-200 text-slate-700 rounded-lg text-sm font-semibold">
                        {sug.unique} unique values
                      </span>
                    </div>

                    {customizing ? (
                      <div className="flex space-x-2">
                        {['one_hot', 'label', 'skip'].map(action => (
                          <button
                            key={action}
                            onClick={() => toggleColumnAction(colId, action)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 border-2 ${
                              currentAction === action
                                ? actionColors[action] + ' scale-105 shadow-md'
                                : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                            }`}
                          >
                            {action === 'one_hot' ? 'One-Hot' : action === 'label' ? 'Label' : 'Skip'}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className={`px-3 py-1 rounded-lg text-sm font-medium ${actionColors[currentAction]}`}>
                          {currentAction === 'one_hot' ? 'One-Hot Encoding' : currentAction === 'label' ? 'Label Encoding' : 'Skip'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <button
          onClick={handleApply}
          disabled={processing}
          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center space-x-2"
        >
          {processing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Encoding...</span>
            </>
          ) : (
            <>
              <span>Apply & Continue</span>
              <ChevronRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
