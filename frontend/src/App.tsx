import { useState, useEffect, useCallback } from 'react';
import {
  Cpu,
  HardDrive,
  Wifi,
  WifiOff,
  Play,
  Pause,
  Zap,
  FolderPlus,
  Undo2,
  RotateCcw,
  FileText,
  Image,
  Code2,
  Receipt,
  GraduationCap,
  User,
  Archive,
  Moon,
  Activity,
  Shield,
  Clock,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import {
  getStatus,
  getHistory,
  toggleDaemon,
  generateSandbox,
  undoSingle,
  undoAll,
  IS_DEMO,
  type StatusResponse,
  type HistoryRecord,
} from './api';

/* ============================================================
   Category config — icons & colors
   ============================================================ */

const CATEGORY_META: Record<string, { icon: typeof FileText; label: string; color: string; bg: string }> = {
  Finance_And_Bills: { icon: Receipt, label: 'Finance', color: 'text-amber-400', bg: 'bg-amber-400/10' },
  Study_And_Papers: { icon: GraduationCap, label: 'Study', color: 'text-blue-400', bg: 'bg-blue-400/10' },
  Code_And_Tech: { icon: Code2, label: 'Code', color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  Screenshots_And_Media: { icon: Image, label: 'Media', color: 'text-purple-400', bg: 'bg-purple-400/10' },
  Personal_And_Docs: { icon: User, label: 'Personal', color: 'text-pink-400', bg: 'bg-pink-400/10' },
  Misc_Archive: { icon: Archive, label: 'Misc', color: 'text-slate-400', bg: 'bg-slate-400/10' },
};

const STATE_CONFIG: Record<string, { color: string; pulse: boolean; label: string }> = {
  Napping: { color: 'text-amber-400', pulse: true, label: '💤 Napping' },
  Sorting: { color: 'text-sloth-400', pulse: true, label: '🦥 Sorting' },
  Paused: { color: 'text-bark-400', pulse: false, label: '⏸ Paused' },
  Idle: { color: 'text-sloth-300', pulse: true, label: '🌿 Idle' },
};

/* ============================================================
   Main App
   ============================================================ */

export default function App() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const showFeedback = (msg: string) => {
    setActionFeedback(msg);
    setTimeout(() => setActionFeedback(null), 3000);
  };

  const refresh = useCallback(async () => {
    try {
      const [s, h] = await Promise.all([getStatus(), getHistory()]);
      setStatus(s);
      setHistory(h.records);
      setError(null);
    } catch (e: any) {
      setError(e.message || 'Cannot reach SlothSort backend');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleToggle = async (action: 'start' | 'pause' | 'sort_one') => {
    try {
      const res = await toggleDaemon(action);
      showFeedback(res.message);
      await refresh();
    } catch (e: any) {
      showFeedback(`Error: ${e.message}`);
    }
  };

  const handleGenSandbox = async () => {
    try {
      const res = await generateSandbox();
      showFeedback(res.message);
      await refresh();
    } catch (e: any) {
      showFeedback(`Error: ${e.message}`);
    }
  };

  const handleUndo = async (id: string) => {
    try {
      const res = await undoSingle(id);
      showFeedback(res.message);
      await refresh();
    } catch (e: any) {
      showFeedback(`Error: ${e.message}`);
    }
  };

  const handleUndoAll = async () => {
    try {
      const res = await undoAll();
      showFeedback(res.message);
      await refresh();
    } catch (e: any) {
      showFeedback(`Error: ${e.message}`);
    }
  };

  /* ============================================================
     Render helpers
     ============================================================ */

  const cpuColor = (pct: number) => {
    if (pct < 25) return 'bg-sloth-500';
    if (pct < 50) return 'bg-amber-400';
    if (pct < 75) return 'bg-orange-500';
    return 'bg-red-500';
  };

  /* ============================================================
     Loading / Error states
     ============================================================ */

  if (loading && !status) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-surface)' }}>
        <div className="text-center animate-fade-in">
          <div className="text-6xl mb-4 animate-float">🦥</div>
          <p className="text-bark-400 text-lg font-medium">Waking up the sloth...</p>
        </div>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--color-surface)' }}>
        <div className="text-center max-w-md animate-fade-in">
          <div className="text-6xl mb-4">😴</div>
          <h2 className="text-xl font-semibold text-bark-200 mb-2">Backend Not Reachable</h2>
          <p className="text-bark-400 mb-4">{error}</p>
          <p className="text-bark-500 text-sm font-mono">
            Start the backend with:<br />
            <code className="text-sloth-400">cd slothsort/backend && uvicorn main:app --port 8000</code>
          </p>
        </div>
      </div>
    );
  }

  const st = status!;
  const stateConf = STATE_CONFIG[st.state] || STATE_CONFIG.Idle;
  const activeHistory = history.filter((r) => !r.undone);

  /* ============================================================
     Main UI
     ============================================================ */

  return (
    <div className="min-h-screen bg-noise" style={{ background: 'var(--color-surface)' }}>
      {/* ── Demo Mode Banner ── */}
      {IS_DEMO && (
        <div className="w-full bg-amber-500/20 text-amber-300 text-center text-sm py-2">
          🦥 Demo mode: sample data. The real app runs 100% locally with Ollama.{' '}
          <a className="underline" href="https://github.com/srinjoyeegoswami/SlothSort">Get the code</a>
        </div>
      )}

      {/* ── Feedback Toast ── */}
      {actionFeedback && (
        <div className="fixed top-4 right-4 z-50 animate-slide-up">
          <div className="glass-strong rounded-xl px-5 py-3 text-sm font-medium text-sloth-300 shadow-2xl flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-400" />
            {actionFeedback}
          </div>
        </div>
      )}

      {/* ── Header ── */}
      <header className="glass-strong sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <span className="text-3xl animate-float">🦥</span>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-bark-100">
                Sloth<span className="text-sloth-400">Sort</span>
              </h1>
              <p className="text-xs text-bark-500 font-medium">The Lazy Control Panel</p>
            </div>
          </div>

          {/* Status badges */}
          <div className="flex items-center gap-4">
            {/* Ollama status */}
            <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full ${st.ollama_online ? 'bg-sloth-500/10 text-sloth-400' : 'bg-red-500/10 text-red-400'}`}>
              {st.ollama_online ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
              {st.ollama_online ? '100% Local & Offline' : 'Ollama Offline'}
            </div>

            {/* Daemon state */}
            <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-bark-800 ${stateConf.color}`}>
              {stateConf.pulse && <span className="w-2 h-2 rounded-full bg-current animate-pulse-glow" />}
              {stateConf.label}
            </div>

            {/* Privacy badge */}
            <div className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full bg-bark-800 text-bark-300">
              <Shield className="w-3.5 h-3.5 text-sloth-500" />
              Zero Cloud
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* ── Sloth Meter ── */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-slide-up">
          {/* CPU */}
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-bark-300 text-sm font-medium">
                <Cpu className="w-4 h-4 text-sloth-400" />
                CPU Load
              </div>
              <span className="text-2xl font-bold font-mono text-bark-100">{st.cpu_percent}%</span>
            </div>
            <div className="cpu-bar">
              <div className={`cpu-bar-fill ${cpuColor(st.cpu_percent)}`} style={{ width: `${Math.min(st.cpu_percent, 100)}%` }} />
            </div>
            <p className="text-xs text-bark-500 mt-2">
              {st.is_system_busy ? '⚠️ System busy — sloth napping' : '✅ System idle — safe to sort'}
            </p>
          </div>

          {/* Memory */}
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-bark-300 text-sm font-medium">
                <HardDrive className="w-4 h-4 text-amber-400" />
                Memory
              </div>
              <span className="text-2xl font-bold font-mono text-bark-100">{st.memory_percent}%</span>
            </div>
            <div className="cpu-bar">
              <div className={`cpu-bar-fill ${cpuColor(st.memory_percent)}`} style={{ width: `${Math.min(st.memory_percent, 100)}%` }} />
            </div>
            <p className="text-xs text-bark-500 mt-2">
              {st.memory_percent > 85 ? '⚠️ High memory — pausing inference' : '✅ Memory healthy'}
            </p>
          </div>

          {/* Models */}
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center gap-2 text-bark-300 text-sm font-medium mb-3">
              <Activity className="w-4 h-4 text-purple-400" />
              Active Models
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-bark-400">Text</span>
                <span className="font-mono text-xs text-sloth-300 bg-sloth-500/10 px-2 py-0.5 rounded-md">{st.text_model}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-bark-400">Vision</span>
                <span className="font-mono text-xs text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded-md">{st.vision_model}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-bark-400">Sorted</span>
                <span className="font-mono text-xs text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded-md">{st.files_sorted} files</span>
              </div>
            </div>
          </div>
        </section>

        {/* ── Controls ── */}
        <section className="flex flex-wrap gap-3 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          {st.state === 'Paused' || st.state === 'Idle' ? (
            <button
              id="btn-start"
              onClick={() => handleToggle('start')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-sloth-600 hover:bg-sloth-500 text-white text-sm font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-sloth-600/20 active:scale-95 cursor-pointer"
            >
              <Play className="w-4 h-4" /> Start Sorting
            </button>
          ) : (
            <button
              id="btn-pause"
              onClick={() => handleToggle('pause')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-bark-700 hover:bg-bark-600 text-bark-200 text-sm font-semibold transition-all duration-200 active:scale-95 cursor-pointer"
            >
              <Pause className="w-4 h-4" /> Pause
            </button>
          )}

          <button
            id="btn-sort-one"
            onClick={() => handleToggle('sort_one')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-600/80 hover:bg-amber-500 text-white text-sm font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-amber-600/20 active:scale-95 cursor-pointer"
          >
            <Zap className="w-4 h-4" /> Sort 1 File Now
          </button>

          <button
            id="btn-gen-sandbox"
            onClick={handleGenSandbox}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600/80 hover:bg-purple-500 text-white text-sm font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-purple-600/20 active:scale-95 cursor-pointer"
          >
            <FolderPlus className="w-4 h-4" /> Generate Messy Demo Folder
          </button>

          {activeHistory.length > 0 && (
            <button
              id="btn-undo-all"
              onClick={handleUndoAll}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm font-semibold transition-all duration-200 active:scale-95 ml-auto cursor-pointer"
            >
              <RotateCcw className="w-4 h-4" /> Undo All
            </button>
          )}
        </section>

        {/* ── Activity Feed ── */}
        <section className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-bark-200 flex items-center gap-2">
              <Clock className="w-5 h-5 text-sloth-400" />
              Activity Feed
            </h2>
            <span className="text-xs text-bark-500 font-mono">{activeHistory.length} sorted</span>
          </div>

          {history.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center">
              <div className="text-5xl mb-4 animate-float">🌿</div>
              <h3 className="text-bark-300 font-semibold mb-1">No files sorted yet</h3>
              <p className="text-bark-500 text-sm">
                Generate some demo files and hit <strong>Start Sorting</strong> to see the sloth in action!
              </p>
            </div>
          ) : (
            <div className="space-y-3 stagger-children">
              {history.map((rec) => {
                const catMeta = CATEGORY_META[rec.category] || CATEGORY_META.Misc_Archive;
                const CatIcon = catMeta.icon;
                const isUndone = rec.undone;

                return (
                  <div
                    key={rec.id}
                    className={`glass rounded-2xl p-4 transition-all duration-300 hover:border-sloth-800 ${isUndone ? 'opacity-50' : ''}`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Category icon */}
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${catMeta.bg}`}>
                        <CatIcon className={`w-5 h-5 ${catMeta.color}`} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          {/* Old name */}
                          <span className="font-mono text-sm text-red-400/80 line-through truncate max-w-[200px]">{rec.original_name}</span>
                          <span className="text-bark-500">→</span>
                          {/* New name */}
                          <span className="font-mono text-sm text-sloth-300 font-medium truncate max-w-[200px]">{rec.new_name}</span>
                        </div>

                        {/* Summary + badges */}
                        <p className="text-xs text-bark-400 mt-1 leading-relaxed">{rec.summary}</p>

                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-md ${catMeta.bg} ${catMeta.color}`}>
                            {catMeta.label}
                          </span>
                          <span className="text-xs font-mono text-bark-500 bg-bark-800 px-2 py-0.5 rounded-md">
                            {rec.model_used}
                          </span>
                          <span className="text-xs text-bark-600">
                            {new Date(rec.timestamp).toLocaleTimeString()}
                          </span>

                          {isUndone && (
                            <span className="text-xs text-bark-500 bg-bark-800 px-2 py-0.5 rounded-md flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" /> Undone
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Undo button */}
                      {!isUndone && (
                        <button
                          onClick={() => handleUndo(rec.id)}
                          className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-bark-800 hover:bg-bark-700 text-bark-300 hover:text-amber-400 text-xs font-medium transition-all duration-200 active:scale-95 cursor-pointer"
                          title="Undo this move"
                        >
                          <Undo2 className="w-3.5 h-3.5" /> Undo
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* ── Footer ── */}
        <footer className="text-center py-8 border-t border-bark-800">
          <p className="text-bark-500 text-sm">
            🦥 <strong>SlothSort</strong> — Slow & Steady wins the file organization race
          </p>
          <p className="text-bark-600 text-xs mt-1">
            Built with open-source AI (Ollama + llama3.2 + moondream) · Zero bytes leave your laptop
          </p>
        </footer>
      </main>
    </div>
  );
}