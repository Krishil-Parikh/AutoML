import { 
  Cpu, 
  BarChart2, 
  ShieldCheck, 
  Zap, 
  Download, 
  Search, 
  Layers, 
  Wand2,
  GitBranch 
} from 'lucide-react';

const features = [
  {
    icon: Search,
    title: "Smart Type Detection",
    description: "Our engine automatically infers data types (numerical, categorical, datetime) and suggests the best cleaning strategy for each.",
    color: "from-blue-500 to-cyan-500"
  },
  {
    icon: Wand2,
    title: "Automated Cleaning",
    description: "Instantly handle missing values, drop duplicates, and fix structural errors with intelligent defaults or custom rules.",
    color: "from-violet-500 to-fuchsia-500"
  },
  {
    icon: ShieldCheck,
    title: "Outlier Detection",
    description: "Identify anomalies using IQR and Z-Score methods. Choose to cap, remove, or flag outliers to improve model robustness.",
    color: "from-emerald-500 to-teal-500"
  },
  {
    icon: Layers,
    title: "Multicollinearity Check",
    description: "Detect highly correlated features that might skew your model. We visualize the heatmap and suggest features to drop.",
    color: "from-orange-500 to-red-500"
  },
  {
    icon: GitBranch,
    title: "Smart Encoding",
    description: "Automatically decide between One-Hot and Label encoding based on cardinality. Prepare categorical data for ML in seconds.",
    color: "from-pink-500 to-rose-500"
  },
  {
    icon: BarChart2,
    title: "Instant Visualization",
    description: "Generate univariate distributions and bivariate pairplots automatically. Spot trends and patterns without writing code.",
    color: "from-indigo-500 to-violet-500"
  },
  {
    icon: Cpu,
    title: "Feature Scaling",
    description: "Normalize your data using Standard or MinMax scaling based on distribution skewness, ensuring optimal model performance.",
    color: "from-cyan-500 to-blue-500"
  },
  {
    icon: Download,
    title: "Export to Python",
    description: "Don't just get the clean data. Download the full Jupyter Notebook (.ipynb) to reproduce the entire pipeline locally.",
    color: "from-yellow-500 to-amber-500"
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Built on optimized Pandas and React. Process datasets up to 50MB entirely in-memory with near-instant feedback.",
    color: "from-fuchsia-500 to-pink-500"
  }
];

export default function Features() {
  return (
    <section className="py-24 bg-slate-950 relative overflow-hidden" id="features">
      
      {/* Background Ambience */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-violet-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px]" />
        {/* Noise Texture */}
        <div className="absolute inset-0 opacity-[0.03] bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
      </div>

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        
        {/* Section Header */}
        <div className="text-center mb-20 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-white/10 text-violet-400 text-sm font-medium mb-6 animate-fade-in-up">
            <SparkleIcon />
            <span>Battery Included</span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight animate-fade-in-up delay-100">
            Everything you need to <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400">
              Master Your Data
            </span>
          </h2>
          
          <p className="text-lg text-slate-400 animate-fade-in-up delay-200">
            Stop writing boilerplate pandas code. Our intelligent pipeline handles the tedious preprocessing steps so you can focus on the modeling.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div 
              key={idx}
              className="group relative p-8 bg-slate-900/40 backdrop-blur-sm border border-white/5 rounded-3xl hover:bg-slate-800/40 transition-all duration-300 hover:-translate-y-1 animate-fade-in-up"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {/* Hover Glow Gradient Border */}
              <div className={`absolute inset-0 rounded-3xl bg-gradient-to-r ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                {/* Icon Box */}
                <div className={`
                  w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.color} p-0.5 mb-6
                  group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-black/20
                `}>
                  <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>
                </div>

                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-slate-300 transition-all">
                  {feature.title}
                </h3>
                
                <p className="text-slate-400 leading-relaxed text-sm">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Simple Sparkle Icon Component for the badge
function SparkleIcon() {
  return (
    <svg 
      className="w-4 h-4" 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <path 
        d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" 
        className="fill-current"
      />
    </svg>
  );
}