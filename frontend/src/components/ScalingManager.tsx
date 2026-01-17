import { useState, useEffect } from 'react';
import { Loader2, Sparkles, ChevronRight, Lightbulb, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Suggestion {
  column: string;
  skew: number;
  suggested_action: string;
}

interface ScalingManagerProps {
  sessionId: string;
  aiMode: boolean;
  onComplete: () => void;
}

export default function ScalingManager({ sessionId, aiMode: _aiMode, onComplete }: ScalingManagerProps) {
  const [suggestions, setSuggestions] = useState<Record<number, Suggestion>>({});
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [plan, setPlan] = useState<Record<string, number[]>>({});
  const [customizing, setCustomizing] = useState(false);

  useEffect(() => {
    fetchSuggestions();
  }, [sessionId]);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/suggestions/scaling/${sessionId}`);
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
    setProcessing(true);
    try {
      await fetch(`${API_BASE_URL}/clean/scaling`, {
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
    return 'standard';
  };

  const actionColors: Record<string, string> = {
    standard: 'bg-blue-100 text-blue-700 border-blue-300',
    minmax: 'bg-cyan-100 text-cyan-700 border-cyan-300',
    skip: 'bg-slate-100 text-slate-700 border-slate-300',
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-0">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-4 sm:p-8 border border-slate-200 animate-scale-in">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 sm:mb-6 gap-3 sm:gap-0">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="p-2 sm:p-3 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-xl">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Feature Scaling</h2>
              <p className="text-sm text-slate-500">Normalize numerical features</p>
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

        <div className="bg-cyan-50 rounded-xl p-4 mb-6 border border-cyan-200">
          <div className="flex items-start space-x-2">
            <Lightbulb className="w-5 h-5 text-cyan-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-cyan-800 font-medium mb-2">AI Suggestions Applied</p>
              <p className="text-xs text-cyan-600">
                Standard: Low skew ({'<'}1) • MinMax: High skew ({'>'}1) • All features scaled to comparable ranges
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
                className="bg-slate-50 rounded-xl p-4 border-2 border-transparent hover:border-cyan-200 transition-all duration-300 animate-slide-in"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-slate-800">{sug.column}</h3>
                      <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                        Math.abs(sug.skew) > 1 ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
                      }`}>
                        Skew: {sug.skew.toFixed(2)}
                      </span>
                    </div>

                    {customizing ? (
                      <div className="flex space-x-2">
                        {['standard', 'minmax', 'skip'].map(action => (
                          <button
                            key={action}
                            onClick={() => toggleColumnAction(colId, action)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 border-2 ${
                              currentAction === action
                                ? actionColors[action] + ' scale-105 shadow-md'
                                : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                            }`}
                          >
                            {action === 'standard' ? 'Standard' : action === 'minmax' ? 'MinMax' : 'Skip'}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <span className={`px-3 py-1 rounded-lg text-sm font-medium ${actionColors[currentAction]}`}>
                          {currentAction === 'standard' ? 'Standard Scaler' : currentAction === 'minmax' ? 'MinMax Scaler' : 'No Scaling'}
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
          className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center space-x-2"
        >
          {processing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Scaling Features...</span>
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
