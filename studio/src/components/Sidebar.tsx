import React from 'react';
import { FileText, Database, Bot, Layers, ArrowRight, Box } from 'lucide-react';

export const Sidebar = () => {
    
  const onDragStart = (event: React.DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/label', label);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="w-72 glass-panel h-full flex flex-col z-20 shadow-2xl animate-in">
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-zinc-900 rounded-xl border border-white/10 flex items-center justify-center shadow-inner">
            <Box className="w-5 h-5 text-violet-500" />
          </div>
          <div>
             <h1 className="font-bold text-lg tracking-tight text-white">AION Studio</h1>
             <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Online</p>
             </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-8">
        
        <Section title="Data Sources">
            <DraggableNode type="loader.pdf" label="PDF Document" icon={<FileText className="w-4 h-4 text-rose-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="loader.static" label="Static Text" icon={<FileText className="w-4 h-4 text-zinc-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="loader.web" label="Web Scraper" icon={<Database className="w-4 h-4 text-cyan-400"/>} onDragStart={onDragStart} />
        </Section>
        
        <Section title="RAG Operations">
            <DraggableNode type="rag.chunk" label="Chunk Text" icon={<Layers className="w-4 h-4 text-amber-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="rag.embed" label="Generate Embeddings" icon={<Layers className="w-4 h-4 text-fuchsia-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="rag.vector_store" label="Vector Store" icon={<Database className="w-4 h-4 text-emerald-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="rag.retrieve" label="Context Retrieval" icon={<ArrowRight className="w-4 h-4 text-indigo-400"/>} onDragStart={onDragStart} />
        </Section>

        <Section title="Intelligence">
            <DraggableNode type="llm.generate" label="LLM Generation" icon={<Bot className="w-4 h-4 text-violet-400"/>} onDragStart={onDragStart} />
            <DraggableNode type="agent.react" label="ReAct Agent" icon={<Bot className="w-4 h-4 text-teal-400"/>} onDragStart={onDragStart} />
        </Section>

      </div>
      
      <div className="p-4 border-t border-white/5">
        <div className="glass p-3 rounded-lg flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs text-zinc-400">System Online</span>
        </div>
      </div>
    </aside>
  );
};

const Section = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <div className="space-y-3">
        <div className="text-xs font-bold text-zinc-500 px-2 uppercase tracking-wider">{title}</div>
        <div className="space-y-2">
            {children}
        </div>
    </div>
);

const DraggableNode = ({ type, label, icon, onDragStart }: any) => {
    return (
        <div 
            className="flex items-center gap-3 p-3 rounded-xl bg-zinc-800/30 hover:bg-zinc-800/80 border border-white/5 hover:border-white/10 cursor-grab active:cursor-grabbing transition-all hover:translate-x-1 group"
            onDragStart={(event) => onDragStart(event, type, label)}
            draggable
        >
            <div className="p-2 rounded-lg bg-zinc-900 border border-white/5 group-hover:border-white/10 transition-colors">
                {icon}
            </div>
            <span className="text-sm font-medium text-zinc-400 group-hover:text-white transition-colors">{label}</span>
        </div>
    )
}
