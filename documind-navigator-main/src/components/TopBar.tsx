import { Brain, CheckCircle2, AlertCircle } from "lucide-react";

interface TopBarProps {
  isConnected: boolean;
  documentsLoaded: number;
}

const TopBar = ({ isConnected, documentsLoaded }: TopBarProps) => {
  return (
    <header className="h-14 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Brain className="w-5 h-5 text-primary" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-foreground">DocuMind Enterprise</span>
            <span className="text-[10px] text-muted-foreground -mt-0.5">Context-Aware Corporate Brain</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Environment Badge */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
          isConnected 
            ? 'bg-success/10 text-success' 
            : 'bg-destructive/10 text-destructive'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-success' : 'bg-destructive'} status-pulse`} />
          {isConnected ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Connected to Knowledge Base</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5" />
              <span>No Documents Loaded</span>
            </>
          )}
        </div>

        {/* Document Count */}
        {documentsLoaded > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-xs font-medium text-secondary-foreground">
            <span className="font-mono">{documentsLoaded}</span>
            <span>Documents</span>
          </div>
        )}
      </div>
    </header>
  );
};

export default TopBar;
