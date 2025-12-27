import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  UploadCloud, 
  Wand2, 
  BarChart2, 
  Cpu, 
  Zap,
  Github
} from 'lucide-react';
import Features from './Features'; 
import Documentation from './Documentation'; // 1. Import Documentation

interface LandingPageProps {
  onStart: () => void;
}

export default function LandingPage({ onStart }: LandingPageProps) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [scrolled, setScrolled] = useState(false);
  const [showDocs, setShowDocs] = useState(false); // 2. Add State for navigation

  // Parallax / Mouse follow effect for background
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY,
      });
    };
    
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // 3. Early return for Documentation View
  if (showDocs) {
    return <Documentation onBack={() => setShowDocs(false)} />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden relative selection:bg-violet-500/30">
      
      {/* --- Dynamic Background --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Animated Gradient Orbs */}
        <div 
          className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-violet-600/20 rounded-full blur-[100px] animate-pulse"
          style={{ transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)` }}
        />
        <div 
          className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] bg-indigo-600/20 rounded-full blur-[100px] animate-pulse delay-1000"
          style={{ transform: `translate(${mousePosition.x * -0.02}px, ${mousePosition.y * -0.02}px)` }}
        />
        <div 
          className="absolute top-[40%] left-[40%] w-[20vw] h-[20vw] bg-fuchsia-600/10 rounded-full blur-[80px]"
          style={{ transform: `translate(${mousePosition.x * 0.04}px, ${mousePosition.y * 0.04}px)` }}
        />
        
        {/* Tech Grid Overlay */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      </div>

      {/* --- Navbar --- */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'bg-slate-950/80 backdrop-blur-md border-b border-white/5 py-3 sm:py-4' : 'bg-transparent py-4 sm:py-6'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex justify-between items-center">
          <div className="flex items-center space-x-2 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="bg-gradient-to-tr from-violet-600 to-indigo-600 p-1.5 sm:p-2 rounded-lg">
              <Cpu className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <span className="text-lg sm:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              AutoML<span className="text-violet-500">.io</span>
            </span>
          </div>
          <div className="hidden md:flex items-center space-x-6 lg:space-x-8 text-xs sm:text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            {/* 4. Update Documentation Link to trigger state */}
            <button 
              onClick={() => setShowDocs(true)} 
              className="hover:text-white transition-colors focus:outline-none"
            >
              Documentation
            </button>
            <a href="#" className="hover:text-white transition-colors">Pricing</a>
            <button className="flex items-center space-x-2 opacity-70 hover:opacity-100 transition-opacity">
              <Github className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      {/* --- Hero Section --- */}
      <main className="relative z-10 pt-24 sm:pt-32 pb-8 sm:pb-10 px-4 sm:px-6 min-h-screen flex flex-col justify-center">
        <div className="max-w-7xl mx-auto w-full">
          <div className="flex flex-col lg:flex-row items-center gap-10 sm:gap-16">
            
            {/* Left Content */}
            <div className="flex-1 space-y-6 sm:space-y-8 text-center lg:text-left">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-violet-300 text-xs sm:text-sm font-medium animate-fade-in-up">
                <Sparkles className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">Next Generation Data Intelligence</span>
                <span className="sm:hidden">Data Intelligence</span>
              </div>
              
              <h1 className="text-3xl sm:text-5xl lg:text-7xl font-bold tracking-tight leading-tight">
                Turn Raw Data into <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 animate-gradient-x">
                  Actionable Insights
                </span>
              </h1>
              
              <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto lg:mx-0 leading-relaxed px-4 sm:px-0">
                Upload your dataset and let our AI handle the rest. From cleaning multicollinearity to generating interactive visualizations, we automate the boring stuff.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 sm:gap-4 pt-4 px-4 sm:px-0">
                <button 
                  onClick={onStart}
                  className="w-full sm:w-auto group relative px-6 sm:px-8 py-3 sm:py-4 bg-white text-slate-950 rounded-full font-bold text-base sm:text-lg hover:shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] transition-all duration-300 overflow-hidden"
                >
                  <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-violet-200 via-indigo-200 to-fuchsia-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <span className="relative flex items-center justify-center space-x-2">
                    <span>Start Analyzing Free</span>
                    <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </button>
                
                <button className="w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 rounded-full font-semibold text-white border border-white/10 hover:bg-white/5 transition-all text-base sm:text-base">
                  View Demo
                </button>
              </div>

              {/* Stats / Trust Badges */}
              <div className="pt-6 sm:pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 sm:gap-8 text-slate-500 text-xs sm:text-sm">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-500" />
                  <span>20x Faster Analysis</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span>99.9% Uptime</span>
                </div>
              </div>
            </div>

            {/* Right Visual (Glass Card Stack) */}
            <div className="flex-1 w-full max-w-lg lg:max-w-none perspective-1000 relative px-4 sm:px-0">
              {/* Background Glow */}
              <div className="absolute inset-0 bg-gradient-to-tr from-violet-600 to-fuchsia-600 blur-[60px] sm:blur-[80px] opacity-20 -z-10 rounded-full" />
              
              <div className="relative space-y-3 sm:space-y-4">
                 {/* Card 1: Upload */}
                 <div className="transform translate-x-2 sm:translate-x-4 hover:-translate-y-2 transition-transform duration-500 bg-slate-900/60 backdrop-blur-xl border border-white/10 p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-2xl flex items-center space-x-3 sm:space-x-4 group cursor-default">
                   <div className="p-2 sm:p-3 bg-blue-500/20 rounded-lg sm:rounded-xl text-blue-400 group-hover:text-blue-300 transition-colors">
                     <UploadCloud className="w-6 h-6 sm:w-8 sm:h-8" />
                   </div>
                   <div>
                     <h3 className="font-bold text-slate-200 text-sm sm:text-base">Smart Upload</h3>
                     <p className="text-xs sm:text-sm text-slate-500">Auto-detects data types & errors</p>
                   </div>
                   <div className="ml-auto text-[10px] sm:text-xs font-mono text-emerald-400 bg-emerald-500/10 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded">
                     CSV / Excel
                   </div>
                 </div>

                 {/* Card 2: Processing (Main Focused Card) */}
                 <div className="transform -translate-x-2 sm:-translate-x-4 scale-105 z-10 hover:-translate-y-2 transition-transform duration-500 bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-violet-500/30 p-6 sm:p-8 rounded-xl sm:rounded-2xl shadow-[0_20px_50px_-12px_rgba(124,58,237,0.25)]">
                   <div className="flex justify-between items-start mb-4 sm:mb-6">
                     <div className="p-2 sm:p-3 bg-violet-500 rounded-lg sm:rounded-xl text-white shadow-lg shadow-violet-500/20">
                       <Wand2 className="w-6 h-6 sm:w-8 sm:h-8" />
                     </div>
                     <span className="flex h-3 w-3">
                       <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-violet-400 opacity-75"></span>
                       <span className="relative inline-flex rounded-full h-3 w-3 bg-violet-500"></span>
                     </span>
                   </div>
                   <h3 className="text-xl sm:text-2xl font-bold text-white mb-2">Automated Cleaning</h3>
                   <p className="text-slate-400 mb-4 sm:mb-6 text-sm sm:text-base">
                     We detect multicollinearity, handle missing values, and normalize features instantly.
                   </p>
                   <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
                     <div className="bg-gradient-to-r from-violet-500 to-fuchsia-500 h-full w-2/3 animate-loading-bar" />
                   </div>
                 </div>

                 {/* Card 3: Analysis */}
                 <div className="transform translate-x-4 sm:translate-x-8 hover:-translate-y-2 transition-transform duration-500 bg-slate-900/60 backdrop-blur-xl border border-white/10 p-4 sm:p-6 rounded-xl sm:rounded-2xl shadow-2xl flex items-center space-x-3 sm:space-x-4 group cursor-default">
                   <div className="p-2 sm:p-3 bg-pink-500/20 rounded-lg sm:rounded-xl text-pink-400 group-hover:text-pink-300 transition-colors">
                     <BarChart2 className="w-6 h-6 sm:w-8 sm:h-8" />
                   </div>
                   <div>
                     <h3 className="font-bold text-slate-200 text-sm sm:text-base">Deep Insights</h3>
                     <p className="text-xs sm:text-sm text-slate-500">Correlation heatmaps & distributions</p>
                   </div>
                 </div>
              </div>
            </div>
            
          </div>
        </div>
      </main>

      {/* --- Features Grid Section --- */}
      <Features />

      {/* --- Footer Feature Strip --- */}
      <div className="border-t border-white/5 bg-white/[0.02] backdrop-blur-sm relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
          {[
            { 
              title: "Privacy First", 
              desc: "Your data is processed in memory and never stored permanently.",
              icon: <div className="w-1 h-8 bg-emerald-500 rounded-full" />
            },
            { 
              title: "Lightning Fast", 
              desc: "Built on optimized Python pandas & React for instant feedback.",
              icon: <div className="w-1 h-8 bg-blue-500 rounded-full" />
            },
            { 
              title: "Export Ready", 
              desc: "Download cleaned datasets and high-res charts in one click.",
              icon: <div className="w-1 h-8 bg-violet-500 rounded-full" />
            }
          ].map((feature, idx) => (
            <div key={idx} className="flex items-start space-x-4 p-4 rounded-xl hover:bg-white/5 transition-colors cursor-default">
              {feature.icon}
              <div>
                <h4 className="font-bold text-white mb-1">{feature.title}</h4>
                <p className="text-sm text-slate-400">{feature.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* --- Footer --- */}
      <footer className="border-t border-white/5 bg-slate-950 py-8 sm:py-12 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row justify-between items-center text-slate-500 text-xs sm:text-sm gap-4">
          <p>© 2024 AutoML.io. All rights reserved.</p>
          <div className="flex flex-wrap justify-center space-x-4 sm:space-x-6 mt-0">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </footer>
      
      {/* Custom Styles for one-off animations */}
      <style>{`
        @keyframes gradient-x {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 3s ease infinite;
        }
        @keyframes loading-bar {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }
        .animate-loading-bar {
          animation: loading-bar 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}