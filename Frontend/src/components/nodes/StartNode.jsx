import { Zap } from 'lucide-react';
import BaseNode from './BaseNode';

export default function StartNode({ data }) {
  return (
    <BaseNode
      data={data}
      icon={Zap}
      showTarget={false}
      className="border-emerald-300 bg-gradient-to-br from-emerald-50 to-green-100"
    >
      <div className="text-emerald-700 font-medium">
        Configure topic and theme to begin
      </div>
    </BaseNode>
  );
}
