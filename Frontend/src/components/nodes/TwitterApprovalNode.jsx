import { CheckCircle } from 'lucide-react';
import BaseNode from './BaseNode';

export default function TwitterApprovalNode({ data }) {
  const { workflowData } = data;

  return (
    <BaseNode
      data={data}
      icon={CheckCircle}
    >
      <div className="text-gray-600">
        {data.status === 'waiting' && 'Waiting for human approval...'}
        {data.status === 'completed' && 'Twitter publishing approved'}
        {data.status === 'idle' && 'Human approval required for Twitter'}
      </div>
    </BaseNode>
  );
}
