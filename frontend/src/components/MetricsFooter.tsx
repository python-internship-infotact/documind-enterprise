import { Cpu, Clock, Zap, Hash } from "lucide-react";

interface MetricsFooterProps {
  ttft?: number;
  totalTime?: number;
  tokensUsed?: number;
  model: string;
  isStreaming: boolean;
}

const MetricsFooter = ({ ttft, totalTime, tokensUsed, model, isStreaming }: MetricsFooterProps) => {
  return (
    <footer className="h-10 border-t border-border bg-card/30 backdrop-blur-sm flex items-center justify-between px-6">
      <div className="flex items-center gap-4 text-xs text-muted-foreground font-mono">
        <div className="flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5" />
          <span className="text-foreground/80">{model}</span>
        </div>

        <div className="h-3 w-px bg-border" />

        <div className="flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5" />
          <span className="text-muted-foreground/70">TTFT:</span>
          <span className={`${ttft && ttft < 1000 ? 'text-success' : 'text-foreground/80'}`}>
            {isStreaming ? '...' : ttft ? `${ttft}ms` : '—'}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5" />
          <span className="text-muted-foreground/70">Total:</span>
          <span className="text-foreground/80">
            {isStreaming ? '...' : totalTime ? `${(totalTime / 1000).toFixed(2)}s` : '—'}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <Hash className="w-3.5 h-3.5" />
          <span className="text-muted-foreground/70">Tokens:</span>
          <span className="text-foreground/80">
            {isStreaming ? '...' : tokensUsed ?? '—'}
          </span>
        </div>
      </div>

      <div className="text-xs text-muted-foreground">
        {isStreaming ? (
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            Streaming response...
          </span>
        ) : (
          <span>Ready</span>
        )}
      </div>
    </footer>
  );
};

export default MetricsFooter;
