import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { FlowEditor } from './components/FlowEditor';
import { Login } from './components/Login';
import { SecretsVault } from './components/SecretsVault';
import { FlowLibrary } from './components/FlowLibrary';
import { Loader2, Play, CheckCircle2, Terminal, LogOut, Key, FolderOpen } from 'lucide-react';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('aion_token'));
  const [isExecuting, setIsExecuting] = useState(false);
  const [toast, setToast] = useState<{msg: string, type: 'success' | 'info'} | null>(null);
  const [showSecrets, setShowSecrets] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);

  useEffect(() => {
      // Sync auth state
      if (token) {
          localStorage.setItem('aion_token', token);
      } else {
          localStorage.removeItem('aion_token');
      }
  }, [token]);

  const handleLogout = () => {
      setToken(null);
  };

  const showToast = (msg: string, type: 'success' | 'info' = 'success') => {
      setToast({ msg, type });
      setTimeout(() => setToast(null), 3000);
  };

  const handleRun = () => {
    setIsExecuting(true);
    showToast("Execution started (Simulated)", "info");
    // TODO: Call API with token
    setTimeout(() => {
        setIsExecuting(false);
        showToast("Flow executed successfully", "success");
    }, 2000);
  };

  const handleLoadFlow = async (flowId: string) => {
      // TODO: Load flow into editor
      console.log("Load flow:", flowId);
      setShowLibrary(false);
      showToast("Flow loaded", "info");
  };

  if (!token) {
      return <Login onLogin={setToken} />;
  }

  return (
    <div className="flex h-screen w-full bg-zinc-950 text-white overflow-hidden selection:bg-violet-500/30">
        
      <Sidebar />
      
      <div className="flex-1 h-full relative flex flex-col">
         {/* Top Bar */}
         <div className="absolute top-0 left-0 right-0 z-10 p-4 flex justify-between items-center pointer-events-none">
            <div className="pointer-events-auto">
                {/* Breadcrumbs or Title could go here */}
            </div>
            
            <div className="flex gap-3 pointer-events-auto">
                <button 
                  onClick={handleLogout}
                  className="flex items-center gap-2 bg-zinc-900/50 backdrop-blur border border-white/5 hover:bg-zinc-800 text-zinc-300 px-4 py-2 rounded-xl shadow-lg font-medium transition-all text-sm group"
                >
                    <LogOut className="w-4 h-4 group-hover:text-red-400 transition-colors" />
                    <span className="group-hover:text-red-400 transition-colors">Logout</span>
                </button>
                <button 
                  onClick={() => setShowSecrets(true)}
                  className="flex items-center gap-2 bg-zinc-900/50 backdrop-blur border border-white/5 hover:bg-zinc-800 text-zinc-300 px-4 py-2 rounded-xl shadow-lg font-medium transition-all text-sm"
                >
                    <Key className="w-4 h-4" />
                    Secrets
                </button>
                <button 
                  onClick={() => setShowLibrary(true)}
                  className="flex items-center gap-2 bg-zinc-900/50 backdrop-blur border border-white/5 hover:bg-zinc-800 text-zinc-300 px-4 py-2 rounded-xl shadow-lg font-medium transition-all text-sm"
                >
                    <FolderOpen className="w-4 h-4" />
                    Flows
                </button>
                <button className="flex items-center gap-2 bg-zinc-900/50 backdrop-blur border border-white/5 hover:bg-zinc-800 text-zinc-300 px-4 py-2 rounded-xl shadow-lg font-medium transition-all text-sm">
                    <Terminal className="w-4 h-4" />
                    Console
                </button>
                <button 
                    onClick={handleRun}
                    className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-5 py-2 rounded-xl shadow-lg shadow-violet-500/20 font-medium transition-all text-sm"
                >
                    {isExecuting ? <Loader2 className="animate-spin w-4 h-4" /> : <Play className="w-4 h-4" />}
                    Run Flow
                </button>
            </div>
         </div>

         <FlowEditor />

         {/* Toast Notification */}
         {toast && (
              <div className="fixed bottom-6 right-6 z-50 animate-in">
                  <div className="bg-zinc-900/90 backdrop-blur-xl border border-white/10 text-white px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3">
                     {toast.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-green-400" /> : <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />}
                     <span className="text-sm font-medium">{toast.msg}</span>
                  </div>
              </div>
          )}

          {/* Secrets Vault Modal */}
          {showSecrets && <SecretsVault onClose={() => setShowSecrets(false)} />}

          {/* Flow Library Modal */}
          {showLibrary && <FlowLibrary onClose={() => setShowLibrary(false)} onLoadFlow={handleLoadFlow} />}
       </div>
     </div>
  )
}

export default App
