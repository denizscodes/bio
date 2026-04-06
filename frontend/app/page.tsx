"use client";
import { useState, useRef, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  Music, 
  Search, 
  CheckCircle2, 
  AlertCircle, 
  Activity
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Styled Vinyl Component
const VinylPlayer = ({ active, analyzing, genre }: { active: boolean, analyzing: boolean, genre: string | null }) => {
  const rotationDuration = analyzing ? 2 : 8; // Faster when analyzing

  const genreColor = useMemo(() => {
    switch (genre?.toLowerCase()) {
      case 'metal': return '#ef4444'; // Red
      case 'blues': return '#3b82f6'; // Blue
      case 'rock': return '#f59e0b'; // Amber
      case 'pop': return '#ec4899'; // Pink
      case 'classical': return '#8b5cf6'; // Violet
      case 'jazz': return '#10b981'; // Emerald
      default: return '#22c55e'; // Green
    }
  }, [genre]);

  return (
    <div className="relative w-48 h-48 mx-auto mb-10 flex items-center justify-center">
      {/* Turntable Base */}
      <div className="absolute inset-0 bg-[#111] rounded-2xl shadow-inner border border-zinc-800 flex items-center justify-center">
        <div className="w-40 h-40 rounded-full bg-[#181818] border border-zinc-800 shadow-xl" />
      </div>

      {/* The Vinyl Record */}
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ scale: 0, opacity: 0, rotate: -180 }}
            animate={{ 
              scale: 1, 
              opacity: 1, 
              rotate: 360 * 1000 // Infinite rotation
            }}
            exit={{ scale: 0, opacity: 0, rotate: 180 }}
            transition={{
              scale: { duration: 0.5 },
              opacity: { duration: 0.5 },
              rotate: { duration: rotationDuration * 1000, ease: "linear", repeat: Infinity }
            }}
            className="absolute z-10 w-44 h-44 rounded-full shadow-2xl flex items-center justify-center overflow-hidden"
            style={{ 
              background: `radial-gradient(circle, transparent 20%, #000 21%, #111 25%, #000 26%, #111 40%, #000 41%, #111 60%, #000 61%, #111 80%, #000 81%)`,
              border: '2px solid #222'
            }}
          >
            {/* Record Label */}
            <div 
              className="w-16 h-16 rounded-full flex items-center justify-center text-[10px] font-black text-white/50 text-center leading-tight shadow-lg"
              style={{ backgroundColor: genre ? genreColor : '#333' }}
            >
              {genre || "SONIC LAB"}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tonearm (Needle) */}
      <motion.div 
        initial={{ rotate: -45 }}
        animate={{ rotate: active ? 10 : -45 }}
        transition={{ type: "spring", stiffness: 50 }}
        className="absolute top-0 right-0 z-20 origin-top-right translate-x-4 translate-y-4"
      >
        <div className="w-24 h-2 bg-zinc-700 rounded-full shadow-lg relative">
          <div className="absolute -right-1 -top-1 w-4 h-4 bg-zinc-600 rounded-full border-2 border-zinc-800" />
          <div className="absolute left-0 bottom-0 w-4 h-6 bg-zinc-500 rounded-sm origin-center -rotate-45 translate-y-1" />
        </div>
      </motion.div>
    </div>
  );
};

export default function MusicAI() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<{genre: string, confidence: string} | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [particles, setParticles] = useState<{x: string, y: string, opacity: number, scale: number, duration: number, delay: number, size: number}[]>([]);

  useEffect(() => {
    const newParticles = [...Array(15)].map(() => ({
      x: Math.random() * 100 + "%",
      y: "110%",
      opacity: 0.1 + Math.random() * 0.2,
      scale: 0.5 + Math.random(),
      duration: 15 + Math.random() * 20,
      delay: Math.random() * 10,
      size: 24 + Math.random() * 32
    }));
    setParticles(newParticles);
  }, []);

  const handlePredict = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error("Backend connection failed!");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Analysis failed. Please ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-zinc-100 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">
      
      {/* Background Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {particles.map((p, i) => (
          <motion.div
            key={i}
            initial={{ 
              x: p.x, 
              y: p.y, 
              opacity: p.opacity,
              scale: p.scale
            }}
            animate={{ 
              y: "-10%", 
              rotate: 360 
            }}
            transition={{ 
              duration: p.duration, 
              repeat: Infinity, 
              ease: "linear",
              delay: p.delay
            }}
            className="absolute text-green-500/10"
          >
            <Music size={p.size} />
          </motion.div>
        ))}
        <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent z-10" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-xl w-full z-20"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-medium uppercase tracking-[0.2em] mb-4"
          >
            <Activity size={14} className="animate-pulse" />
            Sonic Intelligence
          </motion.div>
          <h1 className="text-5xl font-black tracking-tighter text-white mb-2">
            SONIC<span className="text-green-500">LAB</span>
          </h1>
          <p className="text-zinc-500 text-xs font-bold uppercase tracking-[0.3em]">RABIA AND DENIZ'S Professional Studio</p>
        </div>

        {/* The Vinyl Player Section */}
        <VinylPlayer active={!!file} analyzing={loading} genre={result?.genre || null} />

        {/* Main Interface Card */}
        <div className="bg-zinc-900/40 backdrop-blur-3xl border border-zinc-800/50 rounded-[3rem] p-10 shadow-2xl relative overflow-hidden">
          {/* Subtle Glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-green-500/50 blur-xl animate-pulse" />

          <div className="relative">
            {/* Dropzone */}
            <motion.div 
              onClick={() => !loading && fileInputRef.current?.click()}
              whileHover={!loading ? { scale: 1.01 } : {}}
              className={cn(
                "relative cursor-pointer border-2 border-dashed rounded-3xl p-10 text-center transition-all duration-500",
                file ? "border-green-500/30 bg-green-500/5" : "border-zinc-800 hover:border-zinc-700 bg-zinc-950/30"
              )}
            >
              <input 
                ref={fileInputRef}
                type="file" 
                accept="audio/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
              />
              
              <div className="flex flex-col items-center gap-3">
                <div className={cn(
                  "w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-700",
                  file ? "bg-green-500 text-black shadow-[0_0_40px_rgba(34,197,94,0.3)]" : "bg-zinc-900 text-zinc-600"
                )}>
                  <AnimatePresence mode="wait">
                    {file ? (
                      <motion.div key="c" initial={{ scale: 0 }} animate={{ scale: 1 }}><CheckCircle2 size={32} /></motion.div>
                    ) : (
                      <motion.div key="u" initial={{ scale: 0 }} animate={{ scale: 1 }}><Upload size={32} /></motion.div>
                    )}
                  </AnimatePresence>
                </div>
                
                <h3 className="text-lg font-bold text-white">
                  {file ? file.name : "Insert Audio Source"}
                </h3>
              </div>
            </motion.div>

            {/* Prediction Reveal */}
            <AnimatePresence>
              {result && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-8 p-6 rounded-2xl bg-zinc-950/50 border border-zinc-800 flex items-center justify-between"
                >
                  <div>
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 block mb-1">Detected Output</span>
                    <span className="text-3xl font-black text-white italic tracking-tight">{result.genre}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-green-500 font-bold block">{result.confidence}</span>
                    <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest">Confidence</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Large CTA Button */}
            <button 
              onClick={handlePredict}
              disabled={!file || loading}
              className="w-full h-20 mt-8 rounded-2xl bg-white text-black font-black text-lg tracking-widest uppercase hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-20 disabled:grayscale overflow-hidden group relative"
            >
              <div className="absolute inset-0 bg-green-500 -translate-x-full group-hover:translate-x-0 transition-transform duration-500 opacity-10" />
              {loading ? "Decrypting Audio Signatures..." : "Engage Sonic Analysis"}
            </button>

            {error && <p className="mt-4 text-center text-red-500 text-xs italic">{error}</p>}
          </div>
        </div>

        {/* Studio Hardware Info */}
        <div className="mt-10 grid grid-cols-3 gap-4 opacity-50">
          {[
            { label: "Neural Net", val: "MusicANN v2" },
            { label: "Features", val: "55 Vectors" },
            { label: "System", val: "Uvicorn:8000" }
          ].map((item, i) => (
            <div key={i} className="bg-zinc-900/50 p-4 rounded-2xl border border-zinc-800 text-center">
              <span className="block text-[8px] font-black uppercase tracking-widest text-zinc-500 mb-1">{item.label}</span>
              <span className="text-[10px] font-bold text-white tracking-widest">{item.val}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}