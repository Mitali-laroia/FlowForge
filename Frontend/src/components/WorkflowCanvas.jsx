import { useCallback, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
} from '@xyflow/react';

import BlogGenerationNode from './nodes/BlogGenerationNode';
import TwitterGenerationNode from './nodes/TwitterGenerationNode';
import HashnodePublishNode from './nodes/HashnodePublishNode';
import TwitterPublishNode from './nodes/TwitterPublishNode';
import StartNode from './nodes/StartNode';
import HashnodeApprovalNode from './nodes/HashnodeApprovalNode';
import TwitterApprovalNode from './nodes/TwitterApprovalNode';

const nodeTypes = {
  startNode: StartNode,
  blogGeneration: BlogGenerationNode,
  twitterGeneration: TwitterGenerationNode,
  hashnodeApproval: HashnodeApprovalNode,
  hashnodePublish: HashnodePublishNode,
  twitterApproval: TwitterApprovalNode,
  twitterPublish: TwitterPublishNode,
};

// Default workflow template
const defaultWorkflowNodes = [
  {
    id: 'start',
    type: 'startNode',
    position: { x: 250, y: 50 },
    data: {
      label: 'Start Workflow',
      status: 'idle'
    },
  },
  {
    id: 'blog-generation',
    type: 'blogGeneration',
    position: { x: 250, y: 180 },
    data: {
      label: 'Generate Blog Content',
      status: 'idle'
    },
  },
  {
    id: 'twitter-generation',
    type: 'twitterGeneration',
    position: { x: 250, y: 310 },
    data: {
      label: 'Generate Twitter Thread',
      status: 'idle'
    },
  },
  {
    id: 'hashnode-approval',
    type: 'hashnodeApproval',
    position: { x: 100, y: 440 },
    data: {
      label: 'Hashnode Approval',
      status: 'idle'
    },
  },
  {
    id: 'hashnode-publish',
    type: 'hashnodePublish',
    position: { x: 100, y: 570 },
    data: {
      label: 'Publish to Hashnode',
      status: 'idle'
    },
  },
  {
    id: 'twitter-approval',
    type: 'twitterApproval',
    position: { x: 400, y: 440 },
    data: {
      label: 'Twitter Approval',
      status: 'idle'
    },
  },
  {
    id: 'twitter-publish',
    type: 'twitterPublish',
    position: { x: 400, y: 570 },
    data: {
      label: 'Publish to Twitter',
      status: 'idle'
    },
  },
];

const defaultWorkflowEdges = [
  {
    id: 'start-blog',
    source: 'start',
    target: 'blog-generation',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
  {
    id: 'blog-twitter',
    source: 'blog-generation',
    target: 'twitter-generation',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
  {
    id: 'twitter-hashnode-approval',
    source: 'twitter-generation',
    target: 'hashnode-approval',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
  {
    id: 'twitter-twitter-approval',
    source: 'twitter-generation',
    target: 'twitter-approval',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
  {
    id: 'hashnode-approval-publish',
    source: 'hashnode-approval',
    target: 'hashnode-publish',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
  {
    id: 'twitter-approval-publish',
    source: 'twitter-approval',
    target: 'twitter-publish',
    type: 'smoothstep',
    style: { stroke: '#6366f1', strokeWidth: 2 },
  },
];

export default function WorkflowCanvas({ workflow, onWorkflowChange, onStatusChange }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultWorkflowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultWorkflowEdges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({
      ...params,
      type: 'smoothstep',
      style: { stroke: '#6366f1', strokeWidth: 2 }
    }, eds)),
    [setEdges]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const nodeData = JSON.parse(type);
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const newNode = {
        id: `${nodeData.type}-${Date.now()}`,
        type: nodeData.type,
        position,
        data: {
          ...nodeData.data,
          status: 'idle'
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  // Update node statuses based on workflow status
  useEffect(() => {
    if (workflow && workflow.status) {
      setNodes((nds) =>
        nds.map((node) => {
          let status = 'idle';

          // Map workflow status to node status based on current_node
          const currentNode = workflow.status.current_node;
          const workflowStatus = workflow.status.status;

          if (workflowStatus === 'completed') {
            status = 'completed';
          } else if (workflowStatus === 'failed') {
            status = node.id === currentNode ? 'failed' : 'idle';
          } else {
            // Map current node to visual node status
            switch (currentNode) {
              case 'start':
                status = node.id === 'start' ? 'running' : 'idle';
                break;
              case 'blog_generation':
                if (node.id === 'start') status = 'completed';
                else if (node.id === 'blog-generation') status = 'running';
                break;
              case 'twitter_generation':
                if (['start', 'blog-generation'].includes(node.id)) status = 'completed';
                else if (node.id === 'twitter-generation') status = 'running';
                break;
              case 'hashnode_post':
                if (['start', 'blog-generation', 'twitter-generation'].includes(node.id)) status = 'completed';
                else if (node.id === 'hashnode-approval') status = 'waiting';
                break;
              case 'publish_hashnode':
                if (['start', 'blog-generation', 'twitter-generation', 'hashnode-approval'].includes(node.id)) status = 'completed';
                else if (node.id === 'hashnode-publish') status = 'running';
                break;
              case 'twitter_post':
                if (['start', 'blog-generation', 'twitter-generation'].includes(node.id)) status = 'completed';
                if (node.id === 'hashnode-approval' || node.id === 'hashnode-publish') status = 'completed';
                else if (node.id === 'twitter-approval') status = 'waiting';
                break;
              case 'publish_twitter':
                if (['start', 'blog-generation', 'twitter-generation', 'hashnode-approval', 'hashnode-publish', 'twitter-approval'].includes(node.id)) status = 'completed';
                else if (node.id === 'twitter-publish') status = 'running';
                break;
              case 'end':
                status = 'completed';
                break;
              default:
                status = 'idle';
            }
          }

          return {
            ...node,
            data: {
              ...node.data,
              status,
              workflowData: workflow.status
            }
          };
        })
      );

      // Notify parent about workflow changes
      if (onWorkflowChange) {
        onWorkflowChange({ nodes, edges, status: workflow.status });
      }
    }
  }, [workflow, setNodes, nodes, edges, onWorkflowChange]);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gradient-to-br from-gray-50 via-white to-blue-50/30"
      >
        <Controls className="!bg-white/90 !backdrop-blur-md !border-gray-200/50 !shadow-xl !rounded-2xl" />
        <MiniMap
          className="!bg-white/90 !backdrop-blur-md !border-gray-200/50 !shadow-xl !rounded-2xl"
          nodeColor={(node) => {
            switch (node.data.status) {
              case 'running': return '#3b82f6';
              case 'completed': return '#10b981';
              case 'failed': return '#ef4444';
              case 'waiting': return '#f59e0b';
              default: return '#6b7280';
            }
          }}
        />
        <Background
          variant="dots"
          gap={24}
          size={1}
          color="#e2e8f0"
          className="opacity-30"
        />

        <Panel position="top-left" className="bg-white/90 backdrop-blur-md p-6 rounded-2xl shadow-xl border border-gray-200/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">⚡</span>
            </div>
            <div>
              <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text">
                FlowForge
              </h3>
              <p className="text-xs text-gray-500 -mt-1">Workflow Canvas</p>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-3">
            AI-powered content workflow automation
          </p>
          {workflow?.status && (
            <div className="text-xs text-gray-500 bg-gray-50/50 px-3 py-2 rounded-lg">
              <div>Status: <span className="font-medium">{workflow.status.status}</span></div>
              <div>Node: <span className="font-medium">{workflow.status.current_node}</span></div>
            </div>
          )}
        </Panel>
      </ReactFlow>
    </div>
  );
}
