import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Box, Settings, Activity, Trash2 } from 'lucide-react';

const BaseNode = ({ data, selected, id }: any) => {
  return (
    <div className={`
        group relative min-w-[200px] rounded-xl transition-all duration-300
        ${selected 
            ? 'ring-2 ring-violet-500 shadow-[0_0_40px_-10px_rgba(139,92,246,0.5)]' 
            : 'hover:ring-1 hover:ring-white/20 shadow-xl'
        }
    `}>
        {/* Glow Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-zinc-800 to-zinc-950 rounded-xl -z-10" />
        <div className="absolute inset-0 bg-white/5 rounded-xl backdrop-blur-sm -z-10" />

      {/* Header */}
      <div className={`
        flex items-center gap-3 p-3 rounded-t-xl border-b border-white/5
        ${selected ? 'bg-violet-500/10' : 'bg-transparent'}
      `}>
        <div className={`
            p-2 rounded-lg border border-white/10 shadow-inner
            ${selected ? 'bg-violet-500 text-white' : 'bg-zinc-800 text-zinc-400 group-hover:text-violet-400 group-hover:border-violet-500/50 transition-colors'}
        `}>
            {data.icon || <Box className="w-4 h-4" />}
        </div>
        
        <div className="flex-1 min-w-0">
            <h3 className="text-sm font-bold text-zinc-100 tracking-tight">{data.label}</h3>
            <p className="text-[10px] uppercase tracking-wider font-semibold text-zinc-500 group-hover:text-zinc-400 transition-colors">{data.type || 'Generic Node'}</p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
                onClick={(e) => {
                    e.stopPropagation(); // Prevent node selection
                    data.onConfig?.(id);
                }}
                className="p-1 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition-colors"
                title="Configure"
            >
                <Settings className="w-3.5 h-3.5" />
            </button>
            <button 
                onClick={(e) => {
                    e.stopPropagation();
                    data.onDelete?.(id);
                }}
                className="p-1 hover:bg-red-500/20 rounded text-zinc-400 hover:text-red-400 transition-colors"
                title="Delete"
            >
                <Trash2 className="w-3.5 h-3.5" />
            </button>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 bg-zinc-900/50 rounded-b-xl space-y-2">
        {data.description && (
            <p className="text-xs text-zinc-400 leading-relaxed">
                {data.description}
            </p>
        )}
        {!data.description && (
             <div className="flex items-center gap-2 text-xs text-zinc-600 italic">
                <Activity className="w-3 h-3" />
                <span>Ready to execute</span>
             </div>
        )}
      </div>

      {/* Handles */}
      <Handle 
        type="target" 
        position={Position.Left} 
        className="!w-3.5 !h-3.5 !border-4 !border-zinc-950 !bg-zinc-400 !rounded-full -ml-[9px] group-hover:!bg-violet-400 transition-colors shadow-lg"
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        className="!w-3.5 !h-3.5 !border-4 !border-zinc-950 !bg-zinc-400 !rounded-full -mr-[9px] group-hover:!bg-violet-400 transition-colors shadow-lg"
      />
    </div>
  );
};

export default memo(BaseNode);
