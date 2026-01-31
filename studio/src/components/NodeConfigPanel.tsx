import { X, Save } from 'lucide-react';
import { useState, useEffect } from 'react';

interface NodeConfigPanelProps {
    node: any;
    onClose: () => void;
    onSave: (nodeId: string, newConfig: any) => void;
}

export const NodeConfigPanel = ({ node, onClose, onSave }: NodeConfigPanelProps) => {
    // Initialize config from node data or defaults
    const [config, setConfig] = useState<any>(node.data.config || {});

    // Reset when node selection changes
    useEffect(() => {
        setConfig(node.data.config || {});
    }, [node]);

    const handleChange = (key: string, value: string) => {
        setConfig((prev: any) => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        onSave(node.id, config);
    };

    // Determine fields based on node type
    const renderFields = () => {
        switch (node.data.type) {
            case 'loader.static':
                return (
                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-zinc-500">Text Content</label>
                        <textarea 
                            className="w-full h-32 bg-zinc-950 border border-zinc-700 rounded-lg p-3 text-sm focus:outline-none focus:border-violet-500"
                            value={config.text || ''}
                            onChange={(e) => handleChange('text', e.target.value)}
                            placeholder="Enter static text here..."
                        />
                    </div>
                );
            case 'loader.pdf':
                return (
                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-zinc-500">PDF Path</label>
                        <input 
                            type="text"
                            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-sm focus:outline-none focus:border-violet-500"
                            value={config.path || ''}
                            onChange={(e) => handleChange('path', e.target.value)}
                            placeholder="/path/to/document.pdf"
                        />
                    </div>
                );
             case 'loader.web':
                return (
                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-zinc-500">URL</label>
                        <input 
                            type="text"
                            className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-sm focus:outline-none focus:border-violet-500"
                            value={config.url || ''}
                            onChange={(e) => handleChange('url', e.target.value)}
                            placeholder="https://example.com"
                        />
                    </div>
                );
             case 'llm.generate':
                return (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs uppercase font-bold text-zinc-500">System Prompt</label>
                            <textarea 
                                className="w-full h-24 bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-sm focus:outline-none focus:border-violet-500"
                                value={config.system_prompt || ''}
                                onChange={(e) => handleChange('system_prompt', e.target.value)}
                                placeholder="You are a helpful assistant..."
                            />
                        </div>
                         <div className="space-y-2">
                            <label className="text-xs uppercase font-bold text-zinc-500">Model</label>
                            <select 
                                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2 text-sm focus:outline-none focus:border-violet-500"
                                value={config.model || 'gpt-3.5-turbo'}
                                onChange={(e) => handleChange('model', e.target.value)}
                            >
                                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                <option value="gpt-4">GPT-4</option>
                                <option value="claude-3">Claude 3</option>
                            </select>
                        </div>
                    </div>
                );
            default:
                return (
                    <div className="text-zinc-500 text-sm italic p-4 text-center border border-dashed border-zinc-700 rounded-lg">
                        No configuration available for this node type.
                    </div>
                );
        }
    };

    return (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-zinc-900 border-l border-white/10 shadow-2xl z-50 animate-in slide-in-from-right flex flex-col">
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
                <div>
                     <h2 className="font-bold text-white">Configuration</h2>
                     <p className="text-xs text-zinc-500">{node.data.label}</p>
                </div>
                <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                    <X className="w-4 h-4 text-zinc-400" />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                {renderFields()}
            </div>

            <div className="p-4 border-t border-white/5 bg-zinc-900/50">
                <button 
                    onClick={handleSave}
                    className="w-full bg-violet-600 hover:bg-violet-500 text-white font-medium py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
                >
                    <Save className="w-4 h-4" />
                    Apply Changes
                </button>
            </div>
        </div>
    );
};
