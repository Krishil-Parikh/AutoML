import { Download, FileText, FileCode, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface DownloadSectionProps {
  sessionId: string;
}

export default function DownloadSection({ sessionId }: DownloadSectionProps) {
  const downloadCSV = () => {
    window.open(`${API_BASE_URL}/download/csv/${sessionId}`, '_blank');
  };

  const downloadNotebook = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/download/notebook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          filename: 'preprocessing_workflow'
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'preprocessing_workflow.ipynb';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading notebook:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-0">
      <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl p-4 sm:p-8 border border-slate-200 animate-scale-in">
        <div className="text-center mb-6 sm:mb-8">
          <div className="inline-flex p-3 sm:p-4 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl shadow-lg mb-3 sm:mb-4">
            <CheckCircle className="w-8 h-8 sm:w-12 sm:h-12 text-white" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-2">Preprocessing Complete!</h2>
          <p className="text-sm sm:text-base text-slate-500">Your data has been cleaned and is ready for analysis</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <button
            onClick={downloadCSV}
            className="group bg-gradient-to-br from-blue-50 to-cyan-50 hover:from-blue-100 hover:to-cyan-100 border-2 border-blue-200 rounded-2xl p-4 sm:p-6 transition-all duration-300 hover:scale-105 hover:shadow-xl">
          
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-1">Clean Dataset</h3>
                <p className="text-sm text-slate-600">Download processed CSV file</p>
              </div>
              <div className="flex items-center space-x-2 text-blue-600 font-medium">
                <Download className="w-4 h-4" />
                <span>Download CSV</span>
              </div>
            </div>
          </button>

          <button
            onClick={downloadNotebook}
            className="group bg-gradient-to-br from-violet-50 to-pink-50 hover:from-violet-100 hover:to-pink-100 border-2 border-violet-200 rounded-2xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-xl"
          >
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-gradient-to-br from-violet-500 to-pink-500 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <FileCode className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-1">Workflow Code</h3>
                <p className="text-sm text-slate-600">Download Jupyter Notebook</p>
              </div>
              <div className="flex items-center space-x-2 text-violet-600 font-medium">
                <Download className="w-4 h-4" />
                <span>Download .ipynb</span>
              </div>
            </div>
          </button>
        </div>

        <div className="mt-8 bg-green-50 rounded-xl p-6 border border-green-200">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-green-800 mb-2">What's included:</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Cleaned dataset with no missing values</li>
                <li>• Outliers handled appropriately</li>
                <li>• Categorical variables encoded</li>
                <li>• Features scaled for ML models</li>
                <li>• Complete Python code for reproducibility</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
