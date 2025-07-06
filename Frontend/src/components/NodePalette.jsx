import { useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Zap,
  PenTool,
  MessageSquare,
  CheckCircle,
  Globe,
  Send
} from 'lucide-react';

const nodeCategories = [
  {
    name: 'Workflow',
    nodes: [
      {
        type: 'startNode',
        label: 'Start',
        icon: Zap,
        description: 'Begin workflow with topic and theme',
        color: 'bg-gradient-to-br from-emerald-50 to-green-100 text-emerald-700 border-emerald-300'
      }
    ]
  },
  {
    name: 'Content Generation',
    nodes: [
      {
        type: 'blogGeneration',
        label: 'Blog Generator',
        icon: PenTool,
        description: 'AI generates blog content',
        color: 'bg-gradient-to-br from-blue-50 to-indigo-100 text-blue-700 border-blue-300'
      },
      {
        type: 'twitterGeneration',
        label: 'Twitter Thread',
        icon: MessageSquare,
        description: 'AI generates Twitter thread',
        color: 'bg-gradient-to-br from-sky-50 to-cyan-100 text-sky-700 border-sky-300'
      }
    ]
  },
  {
    name: 'Publishing',
    nodes: [
      {
        type: 'hashnodeApproval',
        label: 'Hashnode Approval',
        icon: CheckCircle,
        description: 'Human approval for Hashnode',
        color: 'bg-gradient-to-br from-amber-50 to-yellow-100 text-amber-700 border-amber-300'
      },
      {
        type: 'hashnodePublish',
        label: 'Hashnode Publish',
        icon: Globe,
        description: 'Publish to Hashnode blog',
        color: 'bg-gradient-to-br from-purple-50 to-violet-100 text-purple-700 border-purple-300'
      },
      {
        type: 'twitterApproval',
        label: 'Twitter Approval',
        icon: CheckCircle,
        description: 'Human approval for Twitter',
        color: 'bg-gradient-to-br from-orange-50 to-red-100 text-orange-700 border-orange-300'
      },
      {
        type: 'twitterPublish',
        label: 'Twitter Publish',
        icon: Send,
        description: 'Publish to Twitter',
        color: 'bg-gradient-to-br from-cyan-50 to-teal-100 text-cyan-700 border-cyan-300'
      }
    ]
  }
];

export default function NodePalette({ isOpen, onToggle }) {
  const [expandedCategories, setExpandedCategories] = useState(['Workflow', 'Content Generation', 'Publishing']);

  const toggleCategory = (categoryName) => {
    setExpandedCategories(prev => 
      prev.includes(categoryName) 
        ? prev.filter(name => name !== categoryName)
        : [...prev, categoryName]
    );
  };

  const onDragStart = (event, nodeType, nodeData) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({
      type: nodeType,
      data: nodeData
    }));
    event.dataTransfer.effectAllowed = 'move';
  };

  if (!isOpen) {
    return (
      <div className="w-16 bg-white/90 backdrop-blur-md border-r border-gray-200/50 flex flex-col items-center py-6 shadow-lg">
        <button
          onClick={onToggle}
          className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200 hover:scale-105"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white/90 backdrop-blur-md border-r border-gray-200/50 flex flex-col shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-gray-200/50 flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3 mb-2 text-black">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="font-bold text-xl">⚡</span>
            </div>
            <div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text">
                FlowForge
              </h2>
              <p className="text-xs text-gray-500 -mt-1">Workflow Builder</p>
            </div>
          </div>
          <div className="text-sm text-gray-600 bg-gradient-to-r from-blue-50 to-purple-50 px-3 py-2 rounded-lg border border-blue-200/50">
            <span className="text-blue-500">💡</span> Drag nodes to canvas
          </div>
        </div>
        <button
          onClick={onToggle}
          className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200 hover:scale-105"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
      </div>

      {/* Node Categories */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {nodeCategories.map((category) => (
          <div key={category.name} className="space-y-3">
            <button
              onClick={() => toggleCategory(category.name)}
              className="w-full flex items-center justify-between p-3 text-left text-sm font-semibold text-gray-700 hover:bg-gray-50/50 rounded-xl transition-all duration-200"
            >
              <span>{category.name}</span>
              <ChevronRight
                className={`w-4 h-4 transition-transform duration-200 ${
                  expandedCategories.includes(category.name) ? 'rotate-90' : ''
                }`}
              />
            </button>

            {expandedCategories.includes(category.name) && (
              <div className="space-y-3 ml-1">
                {category.nodes.map((node) => {
                  const IconComponent = node.icon;
                  return (
                    <div
                      key={node.type}
                      draggable
                      onDragStart={(e) => onDragStart(e, node.type, {
                        label: node.label,
                        description: node.description
                      })}
                      className={`
                        p-4 rounded-xl border-2 cursor-move transition-all duration-200
                        hover:shadow-xl hover:scale-[1.02] hover:-translate-y-1 active:scale-95
                        backdrop-blur-sm
                        ${node.color}
                      `}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="p-2.5 rounded-xl bg-white/90 shadow-md border border-white/50">
                          <IconComponent className="w-5 h-5 flex-shrink-0" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-sm">{node.label}</div>
                          <div className="text-xs opacity-75 truncate mt-1">
                            {node.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-200/50">
        <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-indigo-50 p-4 rounded-xl border border-blue-200/50">
          <div className="text-xs text-gray-600 space-y-2">
            <div className="flex items-center space-x-2">
              <span className="text-blue-500">🎯</span>
              <span>Drag nodes to the canvas</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-purple-500">🔗</span>
              <span>Connect nodes to build workflow</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-green-500">▶️</span>
              <span>Execute workflow from top bar</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
