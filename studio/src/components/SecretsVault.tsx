import { useState, useEffect } from 'react';
import { Key, Plus, Trash2, Eye, EyeOff, X } from 'lucide-react';

interface Secret {
    id: string;
    key: string;
    value: string;
    created_at: string;
}

export const SecretsVault = ({ onClose }: { onClose: () => void }) => {
    const [secrets, setSecrets] = useState<Secret[]>([]);
    const [loading, setLoading] = useState(false);
    const [newKey, setNewKey] = useState('');
    const [newValue, setNewValue] = useState('');
    const [showValue, setShowValue] = useState(false);

    const loadSecrets = async () => {
        const token = localStorage.getItem('aion_token');
        try {
            const res = await fetch('/api/secrets', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setSecrets(data);
            }
        } catch (error) {
            console.error('Failed to load secrets', error);
        }
    };

    useEffect(() => {
        loadSecrets();
    }, []);

    const handleCreate = async () => {
        if (!newKey || !newValue) return;
        
        setLoading(true);
        const token = localStorage.getItem('aion_token');
        
        try {
            const res = await fetch('/api/secrets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ key: newKey, value: newValue })
            });

            if (res.ok) {
                setNewKey('');
                setNewValue('');
                setShowValue(false);
                await loadSecrets();
            }
        } catch (error) {
            console.error('Failed to create secret', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        const token = localStorage.getItem('aion_token');
        try {
            await fetch(`/api/secrets/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            await loadSecrets();
        } catch (error) {
            console.error('Failed to delete secret', error);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-zinc-900 border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Key className="w-5 h-5 text-violet-500" />
                        <h2 className="text-xl font-bold text-white">Secrets Vault</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                        <X className="w-4 h-4 text-zinc-400" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {/* Add New Secret */}
                    <div className="bg-zinc-950 border border-zinc-700 rounded-lg p-4 space-y-3">
                        <h3 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">Add New Secret</h3>
                        <div className="grid grid-cols-2 gap-3">
                            <input 
                                type="text"
                                placeholder="Secret Key (e.g., OPENAI_API_KEY)"
                                value={newKey}
                                onChange={(e) => setNewKey(e.target.value)}
                                className="bg-zinc-900 border border-zinc-700 rounded-lg p-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-violet-500"
                            />
                            <div className="relative">
                                <input 
                                    type={showValue ? "text" : "password"}
                                    placeholder="Secret Value"
                                    value={newValue}
                                    onChange={(e) => setNewValue(e.target.value)}
                                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-2 pr-10 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-violet-500"
                                />
                                <button 
                                    onClick={() => setShowValue(!showValue)}
                                    className="absolute right-2 top-2 text-zinc-500 hover:text-white"
                                >
                                    {showValue ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                        </div>
                        <button 
                            onClick={handleCreate}
                            disabled={loading || !newKey || !newValue}
                            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            Add Secret
                        </button>
                    </div>

                    {/* Secrets List */}
                    <div className="space-y-2">
                        <h3 className="text-sm font-bold text-zinc-500 uppercase tracking-wider">Stored Secrets</h3>
                        {secrets.length === 0 ? (
                            <p className="text-zinc-600 text-sm italic text-center py-8">No secrets stored yet</p>
                        ) : (
                            secrets.map(secret => (
                                <div key={secret.id} className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 flex items-center justify-between group hover:border-zinc-700 transition-colors">
                                    <div className="flex-1">
                                        <div className="text-sm font-semibold text-white">{secret.key}</div>
                                        <div className="text-xs text-zinc-600 font-mono">{secret.value}</div>
                                    </div>
                                    <button 
                                        onClick={() => handleDelete(secret.id)}
                                        className="opacity-0 group-hover:opacity-100 p-2 hover:bg-red-500/20 rounded text-zinc-400 hover:text-red-400 transition-all"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
