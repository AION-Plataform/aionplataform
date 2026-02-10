import { useState, useEffect } from 'react';
import { Trash2, Play, Clock, FolderOpen, X } from 'lucide-react';
import { apiUrl } from '@/lib/api'

interface Flow {
    id: string;
    name: string;
    created_at: string;
}

export const FlowLibrary = ({ onClose, onLoadFlow }: { onClose: () => void, onLoadFlow: (flowId: string) => void }) => {
    const [flows, setFlows] = useState<Flow[]>([]);
    const [loading, setLoading] = useState(false);

    const loadFlows = async () => {
        setLoading(true);
        const token = localStorage.getItem('aion_token');
        try {
            const res = await fetch(apiUrl('/flows'), {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setFlows(data);
            }
        } catch (error) {
            console.error('Failed to load flows', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadFlows();
    }, []);

    const handleDelete = async (id: string) => {
        if (!confirm('Delete this flow?')) return;
        
        const token = localStorage.getItem('aion_token');
        try {
            await fetch(apiUrl(`/flows/${id}`), {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            await loadFlows();
        } catch (error) {
            console.error('Failed to delete flow', error);
        }
    };

    const handleRun = async (flowId: string) => {
        const token = localStorage.getItem('aion_token');
        try {
            const res = await fetch(apiUrl(`/flows/${flowId}/execute`), {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                alert(`Execution started: ${data.execution_id}`);
            }
        } catch (error) {
            console.error('Failed to run flow', error);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FolderOpen className="w-5 h-5 text-violet-500" />
                        <h2 className="text-xl font-bold text-white">Flow Library</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                        <X className="w-4 h-4 text-zinc-400" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="text-center py-12 text-zinc-500">Loading flows...</div>
                    ) : flows.length === 0 ? (
                        <div className="text-center py-12 text-zinc-600">
                            <FolderOpen className="w-16 h-16 mx-auto mb-4 text-zinc-700" />
                            <p className="text-sm italic">No flows saved yet</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {flows.map(flow => (
                                <div key={flow.id} className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 flex items-center justify-between group hover:border-zinc-700 transition-colors">
                                    <div className="flex-1">
                                        <div className="text-base font-semibold text-white">{flow.name}</div>
                                        <div className="flex items-center gap-2 text-xs text-zinc-500 mt-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(flow.created_at).toLocaleString()}
                                        </div>
                                    </div>
                                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button 
                                            onClick={() => onLoadFlow(flow.id)}
                                            className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-sm font-medium transition-colors"
                                            title="Load Flow"
                                        >
                                            Edit
                                        </button>
                                        <button 
                                            onClick={() => handleRun(flow.id)}
                                            className="p-2 hover:bg-green-500/20 rounded text-zinc-400 hover:text-green-400 transition-colors"
                                            title="Run Flow"
                                        >
                                            <Play className="w-4 h-4" />
                                        </button>
                                        <button 
                                            onClick={() => handleDelete(flow.id)}
                                            className="p-2 hover:bg-red-500/20 rounded text-zinc-400 hover:text-red-400 transition-colors"
                                            title="Delete Flow"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
