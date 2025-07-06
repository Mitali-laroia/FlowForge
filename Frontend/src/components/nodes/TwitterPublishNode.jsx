import { Send } from 'lucide-react';
import BaseNode from './BaseNode';

export default function TwitterPublishNode({ data }) {
  const { workflowData } = data;
  
  return (
    <BaseNode 
      data={data} 
      icon={Send}
    >
      <div className="text-gray-600">
        {data.status === 'running' && 'Publishing to Twitter...'}
        {data.status === 'completed' && workflowData?.state?.channel_values?.twitter_post?.thread_url && (
          <div className="space-y-1">
            <div>✓ Published to Twitter</div>
            <a 
              href={workflowData.state.channel_values.twitter_post.thread_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:underline"
            >
              View Thread
            </a>
          </div>
        )}
        {data.status === 'idle' && 'Will publish to Twitter'}
      </div>
    </BaseNode>
  );
}
