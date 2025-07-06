import { useState } from 'react';
import { ChevronUp, ChevronDown, Eye } from 'lucide-react';

export default function StatusPanel({ status, workflow }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  if (!status) return null;

  const channelValues = status.state?.channel_values || {};

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm border-t border-gray-200/50 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200/50 bg-gradient-to-r from-gray-50/50 to-blue-50/50">
        <div className="flex items-center space-x-6">
          <h3 className="text-lg font-bold text-gray-900">Workflow Details</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 text-sm rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'overview'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-200'
                  : 'text-gray-600 hover:bg-gray-100/50 hover:text-gray-900'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('content')}
              className={`px-4 py-2 text-sm rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'content'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-200'
                  : 'text-gray-600 hover:bg-gray-100/50 hover:text-gray-900'
              }`}
            >
              Generated Content
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-4 py-2 text-sm rounded-xl font-medium transition-all duration-200 ${
                activeTab === 'logs'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-200'
                  : 'text-gray-600 hover:bg-gray-100/50 hover:text-gray-900'
              }`}
            >
              Execution Logs
            </button>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-3 text-gray-500 hover:text-gray-700 hover:bg-gray-100/50 rounded-xl transition-all duration-200"
        >
          {isExpanded ? (
            <ChevronDown className="w-5 h-5" />
          ) : (
            <ChevronUp className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-6 max-h-96 overflow-y-auto bg-gradient-to-b from-white/50 to-gray-50/50">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-gray-200/50 shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-3">Workflow Status</h4>
                  <div className="text-sm text-gray-600 space-y-2">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className="font-medium">{status.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Current Node:</span>
                      <span className="font-medium">{status.current_node}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Requires Input:</span>
                      <span className="font-medium">{status.requires_human_input ? 'Yes' : 'No'}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-gray-200/50 shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-3">Content Info</h4>
                  <div className="text-sm text-gray-600 space-y-2">
                    <div className="flex justify-between">
                      <span>Topic:</span>
                      <span className="font-medium">{channelValues.topic || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Theme:</span>
                      <span className="font-medium">{channelValues.theme || 'None'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>User ID:</span>
                      <span className="font-medium">{channelValues.user_id || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Published URLs */}
              {(channelValues.hashnode_post?.url || channelValues.twitter_post?.thread_url) && (
                <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-gray-200/50 shadow-sm">
                  <h4 className="font-semibold text-gray-900 mb-3">Published Content</h4>
                  <div className="space-y-3">
                    {channelValues.hashnode_post?.url && (
                      <a
                        href={channelValues.hashnode_post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 text-blue-600 hover:text-blue-800 text-sm bg-blue-50/50 p-3 rounded-lg transition-all duration-200 hover:bg-blue-100/50"
                      >
                        <Eye className="w-4 h-4" />
                        <span className="font-medium">Hashnode Blog Post</span>
                      </a>
                    )}
                    {channelValues.twitter_post?.thread_url && (
                      <a
                        href={channelValues.twitter_post.thread_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 text-blue-600 hover:text-blue-800 text-sm bg-blue-50/50 p-3 rounded-lg transition-all duration-200 hover:bg-blue-100/50"
                      >
                        <Eye className="w-4 h-4" />
                        <span className="font-medium">Twitter Thread</span>
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'content' && (
            <div className="space-y-4">
              {channelValues.blog_content && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Generated Blog Content</h4>
                  <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 max-h-40 overflow-y-auto">
                    {channelValues.blog_content.substring(0, 500)}...
                  </div>
                </div>
              )}
              
              {channelValues.twitter_thread && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Generated Twitter Thread</h4>
                  <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 max-h-40 overflow-y-auto">
                    {channelValues.twitter_thread.substring(0, 500)}...
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'logs' && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Execution Logs</h4>
              <div className="bg-gray-900 text-green-400 p-3 rounded-lg text-sm font-mono max-h-60 overflow-y-auto">
                <div>[{new Date().toISOString()}] Workflow started</div>
                <div>[{new Date().toISOString()}] Current status: {status.status}</div>
                <div>[{new Date().toISOString()}] Current node: {status.current_node}</div>
                {status.requires_human_input && (
                  <div>[{new Date().toISOString()}] Waiting for human input...</div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
