import { useCallback, useRef, useState, useMemo } from 'react';
import ReactFlow, {
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Connection,
  Edge,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import BaseNode from '../nodes/BaseNode';

const initialNodes = [
  { id: '1', position: { x: 100, y: 100 }, data: { label: 'Static Text', type: 'loader.static' }, type: 'baseNode' },
];

let id = 0;
const getId = () => `dndnode_${id++}`;

import { NodeConfigPanel } from './NodeConfigPanel';
import { apiFetch } from '@/lib/api'

const EditorInner = () => {
    const reactFlowWrapper = useRef<HTMLDivElement>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    
    // Handlers passed to nodes
    const onNodeDelete = useCallback((id: string) => {
        setNodes((nds) => nds.filter((node) => node.id !== id));
        setEdges((eds) => eds.filter((edge) => edge.source !== id && edge.target !== id));
        if (selectedNodeId === id) setSelectedNodeId(null);
    }, [setNodes, setEdges, selectedNodeId]);

    const onNodeConfig = useCallback((id: string) => {
        setSelectedNodeId(id);
    }, []);

    // Configuration Save Handler
    const onConfigSave = useCallback((id: string, newConfig: any) => {
        setNodes((nds) => nds.map((node) => {
            if (node.id === id) {
                return { ...node, data: { ...node.data, config: newConfig } };
            }
            return node;
        }));
        // Show feedback?
        console.log("Updated config for", id, newConfig);
    }, [setNodes]);

    // Define custom node types
    const nodeTypes = useMemo(() => ({
        baseNode: BaseNode,
        'loader.pdf': BaseNode,
        'loader.static': BaseNode,
        'default': BaseNode
    }), []);

    const onConnect = useCallback(
      (params: Connection | Edge) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#7c3aed', strokeWidth: 2 } }, eds)),
      [setEdges],
    );
  
    const onDragOver = useCallback((event: React.DragEvent) => {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    }, []);
  
    const onDrop = useCallback(
      (event: React.DragEvent) => {
        event.preventDefault();
  
        const type = event.dataTransfer.getData('application/reactflow');
        const label = event.dataTransfer.getData('application/label');
  
        if (typeof type === 'undefined' || !type) {
          return;
        }
  
        const position = reactFlowInstance?.screenToFlowPosition({
          x: event.clientX,
          y: event.clientY,
        });

        const newNode = {
          id: getId(),
          type: 'baseNode', 
          position,
          data: { 
              label: `${label}`, 
              type: type,
              onDelete: onNodeDelete, // Pass handlers
              onConfig: onNodeConfig
          },
        };
  
        setNodes((nds) => nds.concat(newNode));
      },
      [reactFlowInstance, onNodeDelete, onNodeConfig],
    );
  
    const onSave = useCallback(async () => {
      if (!reactFlowInstance) return;

      const flow = reactFlowInstance.toObject();
      
      const dsl = {
          metadata: {
              name: "New Flow " + new Date().toLocaleTimeString(),
              version: "0.1.0",
              created_at: new Date().toISOString(),
              owner: "studio-user"
          },
          nodes: flow.nodes.map((n: any) => ({
              id: n.id,
              type: n.data.type || "default", 
              version: "1.0",
              config: n.data.config || {}, // Save the config!
              position: n.position
          })),
          edges: flow.edges.map((e: any) => ({
              id: e.id,
              source: e.source,
              source_output: e.sourceHandle || "output",
              target: e.target,
              target_input: e.targetHandle || "input",
          }))
      };

      console.log("Saving DSL:", dsl);

      const token = localStorage.getItem('aion_token');
      if (!token) {
          alert('You must be logged in to save.');
          return;
      }

      try {
          const response = await apiFetch('/flows', {
              method: 'POST',
              headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ dsl })
          });
          
          if (response.ok) {
              const res = await response.json();
              alert('Flow saved! ID: ' + res.id);
          } else {
              alert('Failed to save flow');
          }
      } catch (error) {
          console.error("Save failed", error);
      }
    }, [reactFlowInstance]);

    // Handle Backspace Delete (Global)
    // Note: reactflow handles this natively via onNodesChange if keyboard char is enabled (default)
    // But we need to sync our custom delete logic just in case? 
    // Actually React Flow's verify default delete works.

    const selectedNode = nodes.find(n => n.id === selectedNodeId);
  
    return (
      <div className="w-full h-full relative" ref={reactFlowWrapper}>
        <div className="absolute top-4 right-4 z-10 flex gap-2">
            <button 
                onClick={onSave} 
                className="bg-green-600 hover:bg-green-500 text-white px-4 py-2 rounded shadow font-medium"
            >
                Save Flow
            </button>
        </div>
        
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          onPaneClick={() => setSelectedNodeId(null)} // Click outside to close config
          onNodeClick={(_, node) => setSelectedNodeId(node.id)}
          fitView
          proOptions={{ hideAttribution: true }}
          className="bg-zinc-950"
          deleteKeyCode={['Backspace', 'Delete']}
        >
          <Controls className="!bg-zinc-900 !border-zinc-800 !fill-zinc-400 !text-zinc-400 [&>button]:!border-b-zinc-800 hover:[&>button]:!bg-zinc-800 !rounded-xl !overflow-hidden !shadow-2xl" />
          <Background color="#555" gap={24} size={1} className="!bg-zinc-950 opacity-50" />
        </ReactFlow>

        {/* Config Panel */}
        {selectedNode && (
            <NodeConfigPanel 
                node={selectedNode} 
                onClose={() => setSelectedNodeId(null)} 
                onSave={onConfigSave}
            />
        )}
      </div>
    );
}

export const FlowEditor = () => {
    return (
        <ReactFlowProvider>
            <EditorInner />
        </ReactFlowProvider>
    )
}
