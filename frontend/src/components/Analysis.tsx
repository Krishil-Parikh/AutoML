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
  Settings2
} from 'lucide-react';
import { API_BASE_URL } from '../config';

interface AnalysisProps {
  sessionId: string;
  onComplete: () => void;
}

// Plot type definitions
type UnivariatePlotType = 1 | 2 | 3 | 4 | 5;
type CorrelationMethod = 'pearson' | 'spearman';

const UNIVARIATE_PLOT_OPTIONS = [
  { id: 1, name: 'Histogram + Boxplot', description: 'Basic plots' },
  { id: 2, name: 'Histogram with KDE', description: 'With stats overlay' },
  { id: 3, name: 'Boxplot + Swarmplot', description: 'Distribution with points' },
  { id: 4, name: 'Violin Plot', description: 'Density visualization' },
  { id: 5, name: 'QQ Plot', description: 'Normality test' }
];

export default function Analysis({ sessionId, onComplete }: AnalysisProps) {
  const [loading, setLoading] = useState(false);
  const [heatmapUrl, setHeatmapUrl] = useState<string>('');
  const [columns, setColumns] = useState<Array<{ id: number; column_name: string; dtype: string }>>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  
  // State for multi-select univariate
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  const [univariatePlots, setUnivariatePlots] = useState<Record<string, string>>({});
  const [currentProcessingCol, setCurrentProcessingCol] = useState<string>('');
  const [selectedPlotTypes, setSelectedPlotTypes] = useState<Set<UnivariatePlotType>>(new Set<UnivariatePlotType>([1]));
  const [showPlotOptions, setShowPlotOptions] = useState(false);
  
  // Correlation options
  const [correlationMethod, setCorrelationMethod] = useState<CorrelationMethod>('pearson');
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

  const togglePlotType = (plotId: UnivariatePlotType) => {
    setSelectedPlotTypes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(plotId)) {
        newSet.delete(plotId);
      } else {
        newSet.add(plotId);
      }
      return newSet;
    });
  };

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
      const response = await fetch(`${API_BASE_URL}/plots/bivariate/heatmap/${sessionId}?method=${correlationMethod}`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setHeatmapUrl(url);
    } catch (error) {
      console.error('Error generating heatmap:', error);
    } finally {
      setLoading(false);
    }
  };

  // --- FIX: SEQUENTIAL GENERATION WITH PLOT TYPES ---
  const generateUnivariateBatch = async () => {
    if (selectedColumns.length === 0) return;
    setLoading(true);
    setUnivariatePlots({}); // Clear previous plots

    // Build comma-separated list of plot types
    const plotTypeList = Array.from(selectedPlotTypes).sort().join(',');

    // We use a simple for-loop with await to ensure sequential execution.
    // This prevents the backend's Matplotlib 'plt' state from overlapping.
    for (const col of selectedColumns) {
      setCurrentProcessingCol(col); // Show user which one is loading
      try {
        const url = `${API_BASE_URL}/plots/univariate/${sessionId}/${encodeURIComponent(col)}?plot_types=${plotTypeList}`;
        const response = await fetch(url);
        if (response.ok) {
          const blob = await response.blob();
          const objUrl = URL.createObjectURL(blob);
          // Update state immediately so user sees images pop in one by one
          setUnivariatePlots(prev => ({ ...prev, [col]: objUrl }));
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
    <div className="max-w-6xl mx-auto px-4 sm:px-0">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-4 sm:p-8 border border-slate-200 animate-scale-in">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 sm:mb-6 gap-3 sm:gap-0">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="p-2 sm:p-3 bg-gradient-to-br from-rose-500 to-pink-500 rounded-xl">
              <BarChart3 className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-800">Data Analysis</h2>
              <p className="text-xs sm:text-sm text-slate-500">Visualize your cleaned dataset</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:gap-6 mb-4 sm:mb-6">
          {/* Correlation Heatmap Section */}
          <div className="bg-slate-50 rounded-xl p-4 sm:p-6 border border-slate-200">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3 sm:gap-0">
              <h3 className="text-base sm:text-lg font-semibold text-slate-800">Correlation Heatmap</h3>
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
                <div className="flex space-x-2">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name="correlation"
                      value="pearson"
                      checked={correlationMethod === 'pearson'}
                      onChange={(e) => setCorrelationMethod(e.target.value as CorrelationMethod)}
                      disabled={loading}
                      className="w-4 h-4 cursor-pointer disabled:opacity-50"
                    />
                    <span className="text-xs sm:text-sm text-slate-700">Pearson</span>
                  </label>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name="correlation"
                      value="spearman"
                      checked={correlationMethod === 'spearman'}
                      onChange={(e) => setCorrelationMethod(e.target.value as CorrelationMethod)}
                      disabled={loading}
                      className="w-4 h-4 cursor-pointer disabled:opacity-50"
                    />
                    <span className="text-xs sm:text-sm text-slate-700">Spearman</span>
                  </label>
                </div>
                <button
                  onClick={generateHeatmap}
                  disabled={loading}
                  className="w-full sm:w-auto px-4 py-2 bg-gradient-to-r from-rose-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center justify-center space-x-2 text-sm sm:text-base"
                >
                  {loading && !heatmapUrl ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                  <span>Generate</span>
                </button>
              </div>
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
          <div className="bg-slate-50 rounded-xl p-4 sm:p-6 border border-slate-200">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3 sm:gap-0">
              <h3 className="text-base sm:text-lg font-semibold text-slate-800">Univariate Analysis</h3>
              <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2 w-full sm:w-auto">
                <button
                  onClick={toggleSelectAll}
                  disabled={loading}
                  className="w-full sm:w-auto px-3 py-1.5 text-xs sm:text-sm text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <CheckSquare className="w-4 h-4" />
                  {selectedColumns.length === numericColumns.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  onClick={generateUnivariateBatch}
                  disabled={loading || selectedColumns.length === 0}
                  className="w-full sm:w-auto px-4 py-2 bg-gradient-to-r from-indigo-500 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center justify-center space-x-2 text-sm sm:text-base"
                >
                  {loading && currentProcessingCol ? <Loader2 className="w-4 h-4 animate-spin" /> : <ImageIcon className="w-4 h-4" />}
                  <span>Generate Selected ({selectedColumns.length})</span>
                </button>
              </div>
            </div>

            {/* Plot Type Selection */}
            <div className="mb-4 sm:mb-6">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs sm:text-sm text-slate-500 font-medium">Plot Types:</p>
                <button
                  onClick={() => setShowPlotOptions(!showPlotOptions)}
                  className="flex items-center space-x-1 text-xs text-indigo-600 hover:text-indigo-700 transition-colors"
                >
                  <Settings2 className="w-3 h-3" />
                  <span>{showPlotOptions ? 'Hide' : 'Show'} Options</span>
                </button>
              </div>
              
              {showPlotOptions && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4 p-3 bg-white rounded-lg border border-slate-200 animate-fade-in">
                  {UNIVARIATE_PLOT_OPTIONS.map((opt) => (
                    <label key={opt.id} className="flex items-start space-x-3 p-2 hover:bg-indigo-50 rounded-lg cursor-pointer transition-colors">
                      <input
                        type="checkbox"
                        checked={selectedPlotTypes.has(opt.id as UnivariatePlotType)}
                        onChange={() => togglePlotType(opt.id as UnivariatePlotType)}
                        disabled={loading}
                        className="w-4 h-4 mt-0.5 cursor-pointer disabled:opacity-50"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-700">{opt.name}</p>
                        <p className="text-xs text-slate-500">{opt.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              )}

              {!showPlotOptions && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {Array.from(selectedPlotTypes).sort().map((id) => {
                    const opt = UNIVARIATE_PLOT_OPTIONS.find(o => o.id === id);
                    return opt ? (
                      <span key={id} className="inline-flex items-center space-x-1 px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full">
                        <span>{opt.name}</span>
                      </span>
                    ) : null;
                  })}
                </div>
              )}
            </div>

            {/* Column Selection Grid */}
            <div className="mb-4 sm:mb-6">
                <p className="text-xs sm:text-sm text-slate-500 mb-3">Select columns to analyze:</p>
                <div className="flex flex-wrap gap-2 max-h-32 sm:max-h-40 overflow-y-auto">
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
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 animate-fade-in">
                    {Object.entries(univariatePlots).map(([col, url]) => (
                        <div key={col} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                            <div className="p-2 sm:p-3 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                                <span className="font-medium text-slate-700 text-xs sm:text-sm truncate max-w-[150px] sm:max-w-[200px]" title={col}>{col}</span>
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
          <div className="bg-slate-50 rounded-xl p-4 sm:p-6 border border-slate-200">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3 sm:gap-0">
              <h3 className="text-base sm:text-lg font-semibold text-slate-800">Pairplot</h3>
              <button
                onClick={generatePairplot}
                disabled={loading}
                className="w-full sm:w-auto px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center justify-center space-x-2 text-sm sm:text-base"
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