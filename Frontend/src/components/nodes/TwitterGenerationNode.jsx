import { MessageSquare } from 'lucide-react';
import BaseNode from './BaseNode';

export default function TwitterGenerationNode({ data }) {
  const { workflowData } = data;
  
  return (
    <BaseNode 
      data={data} 
      icon={MessageSquare}
    >
      <div className="text-gray-600">
        {data.status === 'running' && 'Generating Twitter thread...'}
        {data.status === 'completed' && workflowData?.state?.channel_values?.twitter_thread && (
          <div className="space-y-1">
            <div>✓ Twitter thread generated</div>
            <div className="text-xs text-gray-500">
              {workflowData.state.channel_values.twitter_thread.length} characters
            </div>
          </div>
        )}
        {data.status === 'idle' && 'AI will generate Twitter thread'}
      </div>
    </BaseNode>
  );
}
