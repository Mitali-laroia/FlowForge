import { useState } from 'react';
import {
  Menu,
  Play,
  Pause,
  Square,
  Save,
  Settings,
  RefreshCw
} from 'lucide-react';

export default function TopBar({ currentWorkflow, workflowStatus, onPaletteToggle }) {
  const [isExecuting, setIsExecuting] = useState(false);

  const getStatusColor = () => {
    if (!workflowStatus) return 'text-gray-500';
    
    switch (workflowStatus.status) {
      case 'running':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'waiting_hashnode_approval':
      case 'waiting_twitter_approval':
        return 'text-yellow-600';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    if (!workflowStatus) return 'Ready';
    
    switch (workflowStatus.status) {
      case 'running':
        return 'Running...';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'waiting_hashnode_approval':
        return 'Waiting for Hashnode Approval';
      case 'waiting_twitter_approval':
        return 'Waiting for Twitter Approval';
      default:
        return workflowStatus.status || 'Ready';
    }
  };

  return (
    <div className="h-16 bg-white/80 backdrop-blur-sm border-b border-gray-200/50 flex items-center justify-between px-6 shadow-sm">
      {/* Left Section */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onPaletteToggle}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              {/* <span className="text-white font-bolds text-sm"></span> */}
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text">
              FlowForge
            </h1>
          </div>
          <span className="px-3 py-1 text-xs font-medium bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 rounded-full border border-blue-200/50">
            Beta
          </span>
        </div>
      </div>

      {/* Center Section - Workflow Controls */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setIsExecuting(!isExecuting)}
          disabled={!currentWorkflow}
          className={`
            flex items-center space-x-2 px-6 py-2.5 rounded-xl font-medium transition-all duration-200 shadow-sm
            ${currentWorkflow
              ? 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white shadow-green-200'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          {isExecuting ? (
            <>
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Execute</span>
            </>
          )}
        </button>

        <button
          onClick={() => setIsExecuting(false)}
          disabled={!isExecuting}
          className={`
            flex items-center space-x-2 px-4 py-2.5 rounded-xl font-medium transition-all duration-200 shadow-sm
            ${isExecuting
              ? 'bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white shadow-red-200'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          <Square className="w-4 h-4" />
          <span>Stop</span>
        </button>

        <div className="h-6 w-px bg-gray-300/50" />

        <button className="flex items-center space-x-2 px-4 py-2.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100/50 rounded-xl transition-all duration-200">
          <Save className="w-4 h-4" />
          <span>Save</span>
        </button>
      </div>

      {/* Right Section - Status and Settings */}
      <div className="flex items-center space-x-4">
        {/* Workflow Status */}
        <div className="flex items-center space-x-3 bg-white/50 px-4 py-2 rounded-xl border border-gray-200/50">
          <div className={`w-2.5 h-2.5 rounded-full ${
            workflowStatus?.status === 'running' ? 'bg-blue-500 animate-pulse shadow-lg shadow-blue-200' :
            workflowStatus?.status === 'completed' ? 'bg-green-500 shadow-lg shadow-green-200' :
            workflowStatus?.status === 'failed' ? 'bg-red-500 shadow-lg shadow-red-200' :
            workflowStatus?.status?.includes('waiting') ? 'bg-yellow-500 animate-pulse shadow-lg shadow-yellow-200' :
            'bg-gray-400'
          }`} />
          <span className={`text-sm font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>

        <div className="h-6 w-px bg-gray-300/50" />

        <button className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200">
          <RefreshCw className="w-4 h-4" />
        </button>

        <button className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
