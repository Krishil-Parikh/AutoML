import { useState } from 'react';
import { Upload, Database, Trash2, AlertCircle, BarChart3, Download, CheckCircle, Sparkles, TrendingUp, Layers, Settings } from 'lucide-react';
import FileUpload from './components/FileUpload';
import ColumnManager from './components/ColumnManager';
import MissingValuesManager from './components/MissingValuesManager';
import OutliersManager from './components/OutliersManager';
import CorrelationManager from './components/CorrelationManager';
import EncodingManager from './components/EncodingManager';
import ScalingManager from './components/ScalingManager';
import Analysis from './components/Analysis';
import DownloadSection from './components/DownloadSection';
import StepIndicator from './components/StepIndicator';

type Step = 'upload' | 'columns' | 'missing' | 'outliers' | 'correlation' | 'encoding' | 'scaling' | 'analysis' | 'download';

function App() {
  const [currentStep, setCurrentStep] = useState<Step>('upload');
  const [sessionId, setSessionId] = useState<string>('');
  const [dataShape, setDataShape] = useState<[number, number] | null>(null);

  const steps: { id: Step; label: string; icon: any }[] = [
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'columns', label: 'Columns', icon: Database },
    { id: 'missing', label: 'Missing Values', icon: AlertCircle },
    { id: 'outliers', label: 'Outliers', icon: TrendingUp },
    { id: 'correlation', label: 'Correlation', icon: Layers },
    { id: 'encoding', label: 'Encoding', icon: Settings },
    { id: 'scaling', label: 'Scaling', icon: Sparkles },
    { id: 'analysis', label: 'Analysis', icon: BarChart3 },
    { id: 'download', label: 'Download', icon: Download },
  ];

  const handleUploadComplete = (id: string, shape: [number, number]) => {
    setSessionId(id);
    setDataShape(shape);
    setCurrentStep('columns');
  };

  const handleStepComplete = (nextStep: Step) => {
    setCurrentStep(nextStep);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMwMDAwMDAiIGZpbGwtb3BhY2l0eT0iMC4wMiI+PHBhdGggZD0iTTM2IDE2YzAtMS4xLjktMiAyLTJzMiAuOSAyIDItLjkgMi0yIDItMi0uOS0yLTJ6bTAgMjBjMC0xLjEuOS0yIDItMnMyIC45IDIgMi0uOSAyLTIgMi0yLS45LTItMnpNMTYgMTZjMC0xLjEuOS0yIDItMnMyIC45IDIgMi0uOSAyLTIgMi0yLS45LTItMnptMCAyMGMwLTEuMS45LTIgMi0yczIgLjkgMiAyLS45IDItMiAyLTItLjktMi0yeiIvPjwvZz48L2c+PC9zdmc+')] opacity-40"></div>

      <div className="relative">
        <header className="backdrop-blur-md bg-white/70 border-b border-slate-200 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-3 rounded-xl shadow-lg transform hover:scale-105 transition-transform duration-300">
                <Database className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  AutoEDA Studio
                </h1>
                <p className="text-sm text-slate-500">Intelligent Data Preprocessing & Analysis</p>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-6 py-8">
          <StepIndicator steps={steps} currentStep={currentStep} onStepClick={setCurrentStep} sessionId={sessionId} />

          {dataShape && (
            <div className="mb-6 bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-slate-200 animate-slide-down">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2 text-slate-600">
                    <Database className="w-4 h-4" />
                    <span className="text-sm font-medium">Dataset Shape:</span>
                  </div>
                  <div className="flex space-x-4">
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-semibold">
                      {dataShape[0]} rows
                    </span>
                    <span className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-lg text-sm font-semibold">
                      {dataShape[1]} columns
                    </span>
                  </div>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium flex items-center space-x-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>Session Active</span>
                </span>
              </div>
            </div>
          )}

          <div className="animate-fade-in">
            {currentStep === 'upload' && (
              <FileUpload onComplete={handleUploadComplete} />
            )}
            {currentStep === 'columns' && sessionId && (
              <ColumnManager sessionId={sessionId} onComplete={() => handleStepComplete('missing')} onDataShapeChange={setDataShape} />
            )}
            {currentStep === 'missing' && sessionId && (
              <MissingValuesManager sessionId={sessionId} onComplete={() => handleStepComplete('outliers')} />
            )}
            {currentStep === 'outliers' && sessionId && (
              <OutliersManager sessionId={sessionId} onComplete={() => handleStepComplete('correlation')} />
            )}
            {currentStep === 'correlation' && sessionId && (
              <CorrelationManager sessionId={sessionId} onComplete={() => handleStepComplete('encoding')} />
            )}
            {currentStep === 'encoding' && sessionId && (
              <EncodingManager sessionId={sessionId} onComplete={() => handleStepComplete('scaling')} />
            )}
            {currentStep === 'scaling' && sessionId && (
              <ScalingManager sessionId={sessionId} onComplete={() => handleStepComplete('analysis')} />
            )}
            {currentStep === 'analysis' && sessionId && (
              <Analysis sessionId={sessionId} onComplete={() => handleStepComplete('download')} />
            )}
            {currentStep === 'download' && sessionId && (
              <DownloadSection sessionId={sessionId} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
