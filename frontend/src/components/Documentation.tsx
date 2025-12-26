import React, { useState, useEffect } from 'react';
import { 
  Book, 
  Code, 
  Terminal, 
  Database, 
  Layers, 
  BarChart2, 
  Zap, 
  ChevronRight, 
  ArrowLeft,
  Copy,
  Check
} from 'lucide-react';

interface DocumentationProps {
  onBack: () => void;
}

export default function Documentation({ onBack }: DocumentationProps) {
  const [activeSection, setActiveSection] = useState('intro');
  const [copied, setCopied] = useState('');

  const sections = [
    { id: 'intro', label: 'Introduction', icon: Book },
    { id: 'quickstart', label: 'Quick Start', icon: Zap },
    { id: 'data-prep', label: 'Data Preprocessing', icon: Database },
    { id: 'analysis', label: 'Analysis Engine', icon: BarChart2 },
    { id: 'api', label: 'API Reference', icon: Terminal },
  ];

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(text);
    setTimeout(() => setCopied(''), 2000);
  };

  // Scroll spy to update active section
  useEffect(() => {
    const handleScroll = () => {
      const sectionElements = sections.map(s => document.getElementById(s.id));
      const scrollPosition = window.scrollY + 100;

      for (const section of sectionElements) {
        if (section && section.offsetTop <= scrollPosition && (section.offsetTop + section.offsetHeight) > scrollPosition) {
          setActiveSection(section.id);
        }
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollTo = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      window.scrollTo({ top: element.offsetTop - 80, behavior: 'smooth' });
      setActiveSection(id);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-violet-500/30">
      
      {/* Background Ambience */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-violet-900/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-indigo-900/10 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
      </div>

      {/* Navbar / Top Bar */}
      <header className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-md border-b border-white/5 h-16 flex items-center px-6 justify-between">
        <div className="flex items-center space-x-3 cursor-pointer group" onClick={onBack}>
          <div className="p-1.5 rounded-lg bg-slate-800 group-hover:bg-slate-700 transition-colors border border-white/10">
            <ArrowLeft className="w-4 h-4 text-slate-400 group-hover:text-white" />
          </div>
          <span className="font-semibold text-slate-200 group-hover:text-violet-400 transition-colors">Back to App</span>
        </div>
        <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-xs font-mono text-emerald-500">v2.4.0 Live</span>
        </div>
      </header>

      <div className="flex max-w-7xl mx-auto pt-16 relative z-10">
        
        {/* Sidebar Navigation */}
        <aside className="w-64 fixed h-[calc(100vh-4rem)] overflow-y-auto border-r border-white/5 bg-slate-950/50 backdrop-blur-sm hidden lg:block p-6">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-6">Documentation</h3>
          <nav className="space-y-1">
            {sections.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => scrollTo(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                    isActive 
                      ? 'bg-violet-500/10 text-violet-400 border border-violet-500/20' 
                      : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-violet-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && <ChevronRight className="w-3 h-3 ml-auto animate-pulse" />}
                </button>
              );
            })}
          </nav>

          <div className="mt-10 p-4 rounded-xl bg-gradient-to-br from-violet-900/20 to-indigo-900/20 border border-violet-500/10">
            <h4 className="text-sm font-semibold text-white mb-2">Need Help?</h4>
            <p className="text-xs text-slate-400 mb-3">Join our Discord community for real-time support.</p>
            <button className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs font-medium text-white transition-colors">
              Join Discord
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:pl-72 p-8 lg:p-12 max-w-5xl">
          
          {/* Intro Section */}
          <section id="intro" className="mb-20 animate-fade-in-up">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              AutoML<span className="text-violet-500">.io</span> Documentation
            </h1>
            <p className="text-xl text-slate-400 leading-relaxed mb-8">
              Welcome to the most advanced automated exploratory data analysis tool. 
              Our engine processes your raw datasets using optimized Python Pandas & Scikit-Learn pipelines, 
              delivering actionable insights in seconds.
            </p>
            <div className="grid md:grid-cols-2 gap-4">
               <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 hover:border-violet-500/30 transition-colors">
                  <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" /> Instant Processing
                  </h3>
                  <p className="text-sm text-slate-400">Handle CSVs up to 50MB entirely in-memory with zero latency.</p>
               </div>
               <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 hover:border-violet-500/30 transition-colors">
                  <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <Code className="w-4 h-4 text-blue-400" /> Export Code
                  </h3>
                  <p className="text-sm text-slate-400">Download the generated Python notebook to extend the analysis.</p>
               </div>
            </div>
          </section>

          <hr className="border-white/5 mb-20" />

          {/* Quick Start */}
          <section id="quickstart" className="mb-20 scroll-mt-24">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><Zap className="w-6 h-6" /></div>
              <h2 className="text-3xl font-bold text-white">Quick Start</h2>
            </div>
            
            <div className="space-y-6">
              <StepItem number="01" title="Upload your Dataset">
                Simply drag and drop a <CodeBadge>.csv</CodeBadge> file into the upload zone. The system will automatically scan for headers and data types.
              </StepItem>
              <StepItem number="02" title="Review Suggestions">
                Our AI suggests cleaning operations (e.g., "Drop column due to 60% missing values"). You can accept or customize these actions.
              </StepItem>
              <StepItem number="03" title="Generate Report">
                Once cleaning is done, access the Analysis dashboard to view correlation heatmaps and distribution charts.
              </StepItem>
            </div>
          </section>

          {/* Data Prep */}
          <section id="data-prep" className="mb-20 scroll-mt-24">
             <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400"><Database className="w-6 h-6" /></div>
              <h2 className="text-3xl font-bold text-white">Data Preprocessing</h2>
            </div>
            <p className="text-slate-400 mb-6">The pipeline executes the following stages sequentially:</p>
            
            <div className="bg-slate-900 rounded-2xl border border-white/10 overflow-hidden">
                <TableRow 
                  method="Missing Values" 
                  desc="Imputes numerical data with Mean/Median and categorical with Mode." 
                  tags={['SimpleImputer', 'Pandas']}
                />
                <TableRow 
                  method="Outlier Detection" 
                  desc="Uses IQR (Interquartile Range) to detect and cap/remove anomalies." 
                  tags={['Statistical', 'Robust']}
                />
                <TableRow 
                  method="Encoding" 
                  desc="Applies One-Hot for low cardinality and Label Encoding for high cardinality." 
                  tags={['Sklearn', 'Feature Eng']}
                />
                 <TableRow 
                  method="Scaling" 
                  desc="StandardScaler (Z-score) or MinMaxScaler based on skewness." 
                  tags={['Normalization']}
                  last
                />
            </div>
          </section>

          {/* API Reference */}
          <section id="api" className="mb-20 scroll-mt-24">
             <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-lg bg-pink-500/10 text-pink-400"><Terminal className="w-6 h-6" /></div>
              <h2 className="text-3xl font-bold text-white">API Reference</h2>
            </div>
            <p className="text-slate-400 mb-6">
              You can interact with our engine programmatically using the REST API.
            </p>

            <div className="space-y-6">
               <CodeBlock 
                 label="Upload Dataset"
                 method="POST"
                 url="/api/v1/upload"
                 code={`curl -X POST https://automl.io/api/upload \\
  -F "file=@dataset.csv" \\
  -H "Authorization: Bearer <your_token>"`}
                 onCopy={handleCopy}
                 copied={copied}
               />
               
               <CodeBlock 
                 label="Get Cleaning Suggestions"
                 method="GET"
                 url="/api/v1/suggestions/{session_id}"
                 code={`// Response Example
{
  "column": "age",
  "missing_pct": 12.5,
  "suggested_action": "impute_median"
}`}
                 onCopy={handleCopy}
                 copied={copied}
               />
            </div>
          </section>

        </main>
      </div>
    </div>
  );
}

// --- Subcomponents ---

function StepItem({ number, title, children }: { number: string, title: string, children: React.ReactNode }) {
  return (
    <div className="flex gap-6 group">
      <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-slate-800 border border-white/10 flex items-center justify-center text-lg font-bold text-violet-400 group-hover:bg-violet-500 group-hover:text-white transition-colors duration-300 shadow-lg">
        {number}
      </div>
      <div>
        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-violet-300 transition-colors">{title}</h3>
        <p className="text-slate-400 leading-relaxed">{children}</p>
      </div>
    </div>
  );
}

function CodeBadge({ children }: { children: React.ReactNode }) {
  return (
    <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-white/10 text-violet-300 font-mono text-sm">
      {children}
    </span>
  );
}

function TableRow({ method, desc, tags, last }: { method: string, desc: string, tags: string[], last?: boolean }) {
  return (
    <div className={`p-6 flex flex-col md:flex-row gap-4 md:items-center border-b border-white/5 hover:bg-white/[0.02] transition-colors ${last ? 'border-b-0' : ''}`}>
      <div className="w-48 font-semibold text-white flex-shrink-0">{method}</div>
      <div className="flex-1 text-slate-400 text-sm">{desc}</div>
      <div className="flex gap-2">
        {tags.map(tag => (
          <span key={tag} className="px-2 py-1 rounded text-xs font-medium bg-slate-800 text-slate-300 border border-white/10">
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

function CodeBlock({ label, method, url, code, onCopy, copied }: { label: string, method: string, url: string, code: string, onCopy: (t: string) => void, copied: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0d1117] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <span className={`px-2 py-0.5 rounded text-xs font-bold ${
            method === 'GET' ? 'bg-blue-500/20 text-blue-400' : 
            method === 'POST' ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-300'
          }`}>
            {method}
          </span>
          <span className="font-mono text-sm text-slate-300">{url}</span>
        </div>
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</div>
      </div>
      <div className="p-4 relative group">
        <pre className="text-sm font-mono text-slate-300 overflow-x-auto">
          <code>{code}</code>
        </pre>
        <button 
          onClick={() => onCopy(code)}
          className="absolute top-4 right-4 p-2 rounded-lg bg-white/10 text-slate-400 hover:text-white hover:bg-white/20 transition-all opacity-0 group-hover:opacity-100"
        >
          {copied === code ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}