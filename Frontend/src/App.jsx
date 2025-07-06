import { useState } from 'react';
import WorkflowCanvas from './components/WorkflowCanvas';
import NodePalette from './components/NodePalette';
import TopBar from './components/TopBar';
import StatusPanel from './components/StatusPanel';
import WorkflowExecutor from './components/WorkflowExecutor';

function App() {
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState(null);
  const [paletteOpen, setPaletteOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Node Palette Sidebar */}
      <NodePalette
        isOpen={paletteOpen}
        onToggle={() => setPaletteOpen(!paletteOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar
          currentWorkflow={currentWorkflow}
          workflowStatus={workflowStatus}
          onPaletteToggle={() => setPaletteOpen(!paletteOpen)}
        />

        {/* Workflow Canvas */}
        <div className="flex-1 relative overflow-hidden">
          <WorkflowCanvas
            workflow={currentWorkflow}
            onWorkflowChange={setCurrentWorkflow}
            onStatusChange={setWorkflowStatus}
          />

          {/* Workflow Executor Panel */}
          <WorkflowExecutor
            workflow={currentWorkflow}
            status={workflowStatus}
            onStatusChange={setWorkflowStatus}
          />

          {/* Status Panel */}
          {workflowStatus && (
            <StatusPanel
              status={workflowStatus}
              workflow={currentWorkflow}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
