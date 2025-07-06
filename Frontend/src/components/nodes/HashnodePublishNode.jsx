import { Globe } from 'lucide-react';
import BaseNode from './BaseNode';

export default function HashnodePublishNode({ data }) {
  return (
    <BaseNode
      data={data}
      icon={Globe}
      showSource={false}
      className="border-purple-300 bg-gradient-to-br from-purple-50 to-violet-100"
    >
      <div className="text-purple-700 font-medium">
        Will publish to Hashnode blog
      </div>
    </BaseNode>
  );
}
