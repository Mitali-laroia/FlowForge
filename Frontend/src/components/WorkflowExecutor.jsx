import { useState, useEffect } from 'react';
import {
  X,
  Play,
  Check,
  XCircle,
  Clock,
  AlertTriangle
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function WorkflowExecutor({ workflow, status, onStatusChange }) {
  const [isVisible, setIsVisible] = useState(false);
  const [topic, setTopic] = useState('');
  const [theme, setTheme] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);

  // Show panel when workflow is ready to execute
  useEffect(() => {
    if (workflow && !status) {
      setIsVisible(true);
    }
  }, [workflow, status]);

  const startWorkflow = async () => {
    if (!topic.trim()) {
      alert('Please enter a topic for your content');
      return;
    }

    setIsExecuting(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/workflows/start`, {
        user_id: 'frontend_user',
        topic: topic.trim(),
        theme: theme.trim() || null
      });

      const threadId = response.data.thread_id;
      setCurrentThreadId(threadId);
      
      // Start polling for status
      pollWorkflowStatus(threadId);
      
      setIsVisible(false);
    } catch (error) {
      console.error('Failed to start workflow:', error);
      alert('Failed to start workflow. Please try again.');
      setIsExecuting(false);
    }
  };

  const pollWorkflowStatus = async (threadId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/workflows/${threadId}/status`);
      onStatusChange(response.data);

      // Continue polling if workflow is still running
      if (response.data.status && !['completed', 'failed'].includes(response.data.status)) {
        setTimeout(() => pollWorkflowStatus(threadId), 2000);
      } else {
        setIsExecuting(false);
      }
    } catch (error) {
      console.error('Failed to get workflow status:', error);
      setIsExecuting(false);
    }
  };

  const approveHashnode = async () => {
    if (!currentThreadId) return;
    
    try {
      await axios.post(`${API_BASE_URL}/workflows/${currentThreadId}/approve/hashnode`);
      pollWorkflowStatus(currentThreadId);
    } catch (error) {
      console.error('Failed to approve Hashnode:', error);
    }
  };

  const approveTwitter = async () => {
    if (!currentThreadId) return;
    
    try {
      await axios.post(`${API_BASE_URL}/workflows/${currentThreadId}/approve/twitter`);
      pollWorkflowStatus(currentThreadId);
    } catch (error) {
      console.error('Failed to approve Twitter:', error);
    }
  };

  const rejectHashnode = async () => {
    if (!currentThreadId) return;
    
    try {
      await axios.post(`${API_BASE_URL}/workflows/${currentThreadId}/reject/hashnode`);
      pollWorkflowStatus(currentThreadId);
    } catch (error) {
      console.error('Failed to reject Hashnode:', error);
    }
  };

  const rejectTwitter = async () => {
    if (!currentThreadId) return;
    
    try {
      await axios.post(`${API_BASE_URL}/workflows/${currentThreadId}/reject/twitter`);
      pollWorkflowStatus(currentThreadId);
    } catch (error) {
      console.error('Failed to reject Twitter:', error);
    }
  };

  if (!isVisible && !status) return null;

  return (
    <div className="absolute top-4 right-4 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          {isVisible ? 'Start Workflow' : 'Workflow Status'}
        </h3>
        <button
          onClick={() => setIsVisible(false)}
          className="p-1 text-gray-400 hover:text-gray-600 rounded"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {isVisible ? (
          // Start Workflow Form
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic *
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., The Future of AI in Software Development"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Theme (Optional)
              </label>
              <input
                type="text"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                placeholder="e.g., Technical, Beginner-friendly, Industry trends"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <button
              onClick={startWorkflow}
              disabled={isExecuting || !topic.trim()}
              className={`
                w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-colors
                ${isExecuting || !topic.trim()
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
                }
              `}
            >
              <Play className="w-4 h-4" />
              <span>{isExecuting ? 'Starting...' : 'Start Workflow'}</span>
            </button>
          </div>
        ) : (
          // Status Display
          <div className="space-y-4">
            {/* Current Status */}
            <div className="flex items-center space-x-3">
              {status?.status === 'running' && <Clock className="w-5 h-5 text-blue-500 animate-spin" />}
              {status?.status === 'completed' && <Check className="w-5 h-5 text-green-500" />}
              {status?.status === 'failed' && <XCircle className="w-5 h-5 text-red-500" />}
              {status?.status?.includes('waiting') && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
              
              <div>
                <div className="font-medium text-gray-900">
                  {status?.status === 'waiting_hashnode_approval' && 'Hashnode Approval Required'}
                  {status?.status === 'waiting_twitter_approval' && 'Twitter Approval Required'}
                  {status?.status === 'running' && 'Workflow Running...'}
                  {status?.status === 'completed' && 'Workflow Completed'}
                  {status?.status === 'failed' && 'Workflow Failed'}
                </div>
                <div className="text-sm text-gray-500">
                  Current step: {status?.current_node || 'Unknown'}
                </div>
              </div>
            </div>

            {/* Approval Buttons */}
            {status?.status === 'waiting_hashnode_approval' && (
              <div className="flex space-x-2">
                <button
                  onClick={approveHashnode}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  Approve Hashnode
                </button>
                <button
                  onClick={rejectHashnode}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  Reject
                </button>
              </div>
            )}

            {status?.status === 'waiting_twitter_approval' && (
              <div className="flex space-x-2">
                <button
                  onClick={approveTwitter}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  Approve Twitter
                </button>
                <button
                  onClick={rejectTwitter}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  Reject
                </button>
              </div>
            )}

            {/* Results */}
            {status?.status === 'completed' && status?.state?.channel_values && (
              <div className="space-y-2 text-sm">
                {status.state.channel_values.hashnode_post?.url && (
                  <div>
                    <span className="font-medium">Hashnode: </span>
                    <a 
                      href={status.state.channel_values.hashnode_post.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      View Published Post
                    </a>
                  </div>
                )}
                {status.state.channel_values.twitter_post?.thread_url && (
                  <div>
                    <span className="font-medium">Twitter: </span>
                    <a 
                      href={status.state.channel_values.twitter_post.thread_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      View Twitter Thread
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
