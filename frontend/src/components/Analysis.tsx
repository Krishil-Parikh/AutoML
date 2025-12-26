import { useEffect, useState } from 'react';
import { 
  BarChart3, 
  ChevronRight, 
  Image as ImageIcon, 
  Loader2, 
  CheckCircle2, 
  Circle, 
  Download,
  CheckSquare,
  XCircle
} from 'lucide-react';
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
  
  // State for multi-select univariate
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [univariatePlots, setUnivariatePlots] = useState<Record<string, string>>({});
  const [currentProcessingCol, setCurrentProcessingCol] = useState<string>('');
  
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
      } catch (e) {
        console.error('Failed to load columns', e);
      }
    })();
    return () => {
      active = false;
    };
  }, [sessionId]);

  const toggleColumnSelection = (column: string) => {
    setSelectedColumns(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column) 
        : [...prev, column]
    );
  };

  const toggleSelectAll = () => {
    if (selectedColumns.length === numericColumns.length) {
      setSelectedColumns([]);
    } else {
      setSelectedColumns([...numericColumns]);
    }
  };

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

  // --- FIX: SEQUENTIAL GENERATION ---
  const generateUnivariateBatch = async () => {
    if (selectedColumns.length === 0) return;
    setLoading(true);
    setUnivariatePlots({}); // Clear previous plots

    // We use a simple for-loop with await to ensure sequential execution.
    // This prevents the backend's Matplotlib 'plt' state from overlapping.
    for (const col of selectedColumns) {
      setCurrentProcessingCol(col); // Show user which one is loading
      try {
        const response = await fetch(`${API_BASE_URL}/plots/univariate/${sessionId}/${encodeURIComponent(col)}`);
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          // Update state immediately so user sees images pop in one by one
          setUnivariatePlots(prev => ({ ...prev, [col]: url }));
        }
      } catch (error) {
        console.error(`Error generating plot for ${col}:`, error);
      }
    }

    setCurrentProcessingCol('');
    setLoading(false);
  };

  const downloadImage = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
          {/* Correlation Heatmap Section */}
          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Correlation Heatmap</h3>
              <button
                onClick={generateHeatmap}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading && !heatmapUrl ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                <span>Generate</span>
              </button>
            </div>
            {heatmapUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-200 animate-fade-in relative group">
                <img src={heatmapUrl} alt="Correlation Heatmap" className="w-full" />
                <button
                   onClick={() => downloadImage(heatmapUrl, 'correlation_heatmap.png')}
                   className="absolute top-4 right-4 bg-white/90 p-2 rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white text-slate-700"
                >
                  <Download className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>

          {/* Univariate Analysis Section */}
          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Univariate Analysis</h3>
              <div className="flex space-x-2">
                 <button
                  onClick={toggleSelectAll}
                  disabled={loading}
                  className="px-3 py-1.5 text-sm text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  <CheckSquare className="w-4 h-4" />
                  {selectedColumns.length === numericColumns.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  onClick={generateUnivariateBatch}
                  disabled={loading || selectedColumns.length === 0}
                  className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
                >
                  {loading && currentProcessingCol ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                  <span>Generate Selected ({selectedColumns.length})</span>
                </button>
              </div>
            </div>

            {/* Column Selection Grid */}
            <div className="mb-6">
                <p className="text-sm text-slate-500 mb-3">Select columns to analyze:</p>
                <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto">
                    {numericColumns.map((col) => {
                        const isSelected = selectedColumns.includes(col);
                        return (
                            <button
                                key={col}
                                onClick={() => toggleColumnSelection(col)}
                                disabled={loading}
                                className={`
                                    flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-all duration-200 border
                                    ${isSelected 
                                        ? 'bg-indigo-50 border-indigo-200 text-indigo-700 font-medium' 
                                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                                    }
                                    ${loading ? 'opacity-50 cursor-not-allowed' : ''}
                                `}
                            >
                                {isSelected ? <CheckCircle2 className="w-4 h-4" /> : <Circle className="w-4 h-4 text-slate-300" />}
                                <span>{col}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Charts Grid */}
            {(Object.keys(univariatePlots).length > 0 || currentProcessingCol) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
                    {Object.entries(univariatePlots).map(([col, url]) => (
                        <div key={col} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                            <div className="p-3 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                <span className="font-medium text-slate-700 text-sm truncate max-w-[200px]" title={col}>{col}</span>
                                <button
                                    onClick={() => downloadImage(url, `${col}_univariate.png`)}
                                    className="text-slate-400 hover:text-indigo-600 transition-colors p-1"
                                    title="Download Chart"
                                >
                                    <Download className="w-4 h-4" />
                                </button>
                            </div>
                            <div className="p-2">
                                <img src={url} alt={`Univariate plot for ${col}`} className="w-full h-auto rounded" />
                            </div>
                        </div>
                    ))}
                    
                    {/* Placeholder for item currently loading */}
                    {loading && currentProcessingCol && (
                        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm flex items-center justify-center min-h-[300px]">
                           <div className="text-center">
                              <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mx-auto mb-2" />
                              <p className="text-sm text-slate-500">Generating {currentProcessingCol}...</p>
                           </div>
                        </div>
                    )}
                </div>
            )}
          </div>

          {/* Pairplot Section */}
          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Pairplot</h3>
              <button
                onClick={generatePairplot}
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading && !pairplotUrl ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                <span>Generate</span>
              </button>
            </div>
            {pairplotUrl && (
              <div className="rounded-lg overflow-hidden border border-slate-200 animate-fade-in relative group">
                <img src={pairplotUrl} alt="Pairplot" className="w-full" />
                 <button
                   onClick={() => downloadImage(pairplotUrl, 'pairplot.png')}
                   className="absolute top-4 right-4 bg-white/90 p-2 rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white text-slate-700"
                >
                  <Download className="w-5 h-5" />
                </button>
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