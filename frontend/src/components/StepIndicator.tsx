import { Check } from 'lucide-react';

interface StepIndicatorProps {
  steps: { id: string; label: string; icon: any }[];
  currentStep: string;
  onStepClick: (step: any) => void;
  sessionId: string;
}

export default function StepIndicator({ steps, currentStep, onStepClick, sessionId }: StepIndicatorProps) {
  const currentIndex = steps.findIndex(s => s.id === currentStep);

  return (
    <div className="mb-4 sm:mb-8 bg-white/80 backdrop-blur-sm rounded-2xl p-3 sm:p-6 shadow-lg border border-slate-200">
      {/* Horizontal scrollable container for mobile */}
      <div className="overflow-x-auto pb-2 -mx-3 px-3 sm:mx-0 sm:px-0">
        <div className="flex items-center justify-between min-w-max sm:min-w-0">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const isClickable = sessionId && index <= currentIndex;

          return (
            <div key={step.id} className="flex items-center flex-shrink-0 sm:flex-1">
              <button
                onClick={() => isClickable && onStepClick(step.id)}
                disabled={!isClickable}
                className={`flex flex-col items-center space-y-1 sm:space-y-2 transition-all duration-300 px-1 sm:px-0 ${
                  isClickable ? 'cursor-pointer hover:scale-105' : 'cursor-not-allowed'
                }`}
              >
                <div
                  className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl flex items-center justify-center transition-all duration-500 transform ${
                    isCompleted
                      ? 'bg-gradient-to-br from-green-500 to-emerald-500 shadow-lg scale-100'
                      : isCurrent
                      ? 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-xl scale-110 animate-pulse-soft'
                      : 'bg-slate-200 scale-95'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4 sm:w-6 sm:h-6 text-white" />
                  ) : (
                    <Icon className={`w-4 h-4 sm:w-6 sm:h-6 ${isCurrent ? 'text-white' : 'text-slate-400'}`} />
                  )}
                </div>
                <span
                  className={`text-[10px] sm:text-xs font-medium transition-colors duration-300 whitespace-nowrap ${
                    isCurrent ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-slate-400'
                  }`}
                >
                  {step.label}
                </span>
              </button>

              {index < steps.length - 1 && (
                <div className="flex-shrink-0 w-8 sm:flex-1 h-1 mx-1 sm:mx-2 relative overflow-hidden rounded-full bg-slate-200">
                  <div
                    className={`absolute inset-0 transition-all duration-700 ease-out ${
                      isCompleted ? 'bg-gradient-to-r from-green-400 to-emerald-400 w-full' : 'w-0'
                    }`}
                  />
                </div>
              )}
            </div>
          );
        })}
        </div>
      </div>
    </div>
  );
}
