import { PenTool } from 'lucide-react';
import BaseNode from './BaseNode';

export default function BlogGenerationNode({ data }) {
  return (
    <BaseNode
      data={data}
      icon={PenTool}
      className="border-blue-300 bg-gradient-to-br from-blue-50 to-indigo-100"
    >
      <div className="text-blue-700 font-medium">
        AI will generate blog content
      </div>
    </BaseNode>
  );
}
