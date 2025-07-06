import { Handle, Position } from '@xyflow/react';
import {
  CheckCircle,
  Clock,
  Play,
  XCircle,
  AlertTriangle
} from 'lucide-react';

const statusIcons = {
  idle: Play,
  running: Clock,
  waiting: AlertTriangle,
  completed: CheckCircle,
  failed: XCircle,
};

const statusColors = {
  idle: 'text-gray-600 bg-white/95 border-gray-300 shadow-lg backdrop-blur-sm',
  running: 'text-blue-700 bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200 border-blue-400 shadow-blue-200/50 backdrop-blur-sm',
  waiting: 'text-amber-700 bg-gradient-to-br from-amber-50 via-yellow-100 to-amber-200 border-amber-400 shadow-amber-200/50 backdrop-blur-sm',
  completed: 'text-emerald-700 bg-gradient-to-br from-emerald-50 via-green-100 to-emerald-200 border-emerald-400 shadow-emerald-200/50 backdrop-blur-sm',
  failed: 'text-red-700 bg-gradient-to-br from-red-50 via-red-100 to-red-200 border-red-400 shadow-red-200/50 backdrop-blur-sm',
};

export default function BaseNode({ 
  data, 
  children, 
  sourcePosition = Position.Bottom,
  targetPosition = Position.Top,
  showSource = true,
  showTarget = true,
  icon: Icon,
  className = ''
}) {
  const { status = 'idle', label } = data;
  const StatusIcon = statusIcons[status];
  
  return (
    <div className={`
      relative min-w-[240px] p-5 rounded-2xl border-2 transition-all duration-300
      hover:shadow-xl hover:-translate-y-1 hover:scale-[1.02]
      ${statusColors[status]}
      ${className}
    `}>
      {showTarget && (
        <Handle
          type="target"
          position={targetPosition}
          className="w-4 h-4 !bg-white !border-2 !border-indigo-400 !shadow-lg hover:!border-indigo-500 transition-colors"
        />
      )}

      <div className="flex items-start space-x-4">
        {Icon && (
          <div className={`
            p-3 rounded-xl bg-white/90 shadow-md border border-white/50
            ${status === 'running' ? 'animate-pulse' : ''}
          `}>
            <Icon className="w-6 h-6" />
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-sm truncate">{label}</h3>
            <StatusIcon className={`w-5 h-5 flex-shrink-0 ml-2 ${
              status === 'running' ? 'animate-spin' : ''
            }`} />
          </div>

          {children && (
            <div className="text-xs leading-relaxed">
              {children}
            </div>
          )}
        </div>
      </div>

      {showSource && (
        <Handle
          type="source"
          position={sourcePosition}
          className="w-4 h-4 !bg-white !border-2 !border-indigo-400 !shadow-lg hover:!border-indigo-500 transition-colors"
        />
      )}
    </div>
  );
}
