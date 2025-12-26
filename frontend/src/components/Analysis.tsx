import { useEffect, useMemo, useState } from 'react';
import { BarChart3, ChevronRight, Image as ImageIcon, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface AnalysisProps {
  sessionId: string;
  onComplete: () => void;
}

export default function Analysis({ sessionId, onComplete }: AnalysisProps) {
  const [loading, setLoading] = useState(false);
  const [heatmapUrl, setHeatmapUrl] = useState<string>('');
  const [columns, setColumns] = useState<Array<{ id: number; column_name: string; dtype: string }>>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [univariateUrl, setUnivariateUrl] = useState<string>('');
  const [pairplotUrl, setPairplotUrl] = useState<string>('');

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/info/${sessionId}`);
        const data = await res.json();
        if (!active) return;
        const cols = (data?.columns ?? []) as Array<{ id: number; column_name: string; dtype: string }>;
        setColumns(cols);
        const nums = cols
          .filter((c) => typeof c.dtype === 'string' && /(int|float)/i.test(c.dtype))
          .map((c) => c.column_name);
        setNumericColumns(nums);
        if (nums.length && !selectedColumn) setSelectedColumn(nums[0]);
      } catch (e) {
        console.error('Failed to load columns', e);
      }
    })();
    return () => {
      active = false;
    };
  }, [sessionId]);

  const generateHeatmap = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/plots/bivariate/heatmap/${sessionId}?method=pearson`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setHeatmapUrl(url);
    } catch (error) {
      console.error('Error generating heatmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateUnivariate = async () => {
    if (!selectedColumn) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/plots/univariate/${sessionId}/${encodeURIComponent(selectedColumn)}`);
      if (!response.ok) throw new Error('Failed to generate univariate plot');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setUnivariateUrl(url);
    } catch (error) {
      console.error('Error generating univariate plot:', error);
    } finally {
      setLoading(false);
    }
  };

  const generatePairplot = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/plots/bivariate/pairplot/${sessionId}`);
      if (!response.ok) throw new Error('Failed to generate pairplot');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setPairplotUrl(url);
    } catch (error) {
      console.error('Error generating pairplot:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200 animate-scale-in">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-rose-500 to-pink-500 rounded-xl">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-800">Data Analysis</h2>
              <p className="text-sm text-slate-500">Visualize your cleaned dataset</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 mb-6">
          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Correlation Heatmap</h3>
              <button
                onClick={generateHeatmap}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <ImageIcon className="w-4 h-4" />
                    <span>Generate</span>
                  </>
                )}
              </button>
            </div>
            {heatmapUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-200 animate-fade-in">
                <img src={heatmapUrl} alt="Correlation Heatmap" className="w-full" />
              </div>
            )}
          </div>

          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Univariate Analysis</h3>
            </div>
            <div className="flex items-center gap-3 mb-4">
              <select
                value={selectedColumn}
                onChange={(e) => setSelectedColumn(e.target.value)}
                className="border border-slate-300 rounded-lg px-3 py-2 bg-white"
              >
                {numericColumns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              <button
                onClick={generateUnivariate}
                disabled={loading || !selectedColumn}
                className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <ImageIcon className="w-4 h-4" />
                    <span>Generate</span>
                  </>
                )}
              </button>
            </div>
            {univariateUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-200 animate-fade-in">
                <img src={univariateUrl} alt={`Univariate ${selectedColumn}`} className="w-full" />
              </div>
            )}
          </div>

          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Pairplot</h3>
              <button
                onClick={generatePairplot}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <ImageIcon className="w-4 h-4" />
                    <span>Generate</span>
                  </>
                )}
              </button>
            </div>
            {pairplotUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-200 animate-fade-in">
                <img src={pairplotUrl} alt="Pairplot" className="w-full" />
              </div>
            )}
          </div>
        </div>

        <button
          onClick={onComplete}
          className="w-full bg-gradient-to-r from-rose-500 to-pink-500 text-white py-4 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-2"
        >
          <span>Continue to Download</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
