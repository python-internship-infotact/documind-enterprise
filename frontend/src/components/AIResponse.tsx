import { Brain, FileText, ExternalLink, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface Citation {
  id: string;
  document: string;
  page: number;
  excerpt: string;
  document_title?: string;
  section_header?: string;
  relevance_score?: number;
  chunk_index?: number;
  total_chunks?: number;
  created_at?: string;
  file_size?: number;
  total_pages?: number;
}

interface AIResponseProps {
  content: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low";
  isStreaming: boolean;
  timestamp: Date;
  ttft?: number;
  totalTime?: number;
  tokensUsed?: number;
}

const AIResponse = ({
  content,
  citations,
  confidence,
  isStreaming,
  timestamp,
  ttft,
  totalTime,
  tokensUsed,
}: AIResponseProps) => {
  const confidenceConfig = {
    high: { color: "text-success", bg: "bg-success/10", label: "High Confidence" },
    medium: { color: "text-warning", bg: "bg-warning/10", label: "Medium Confidence" },
    low: { color: "text-destructive", bg: "bg-destructive/10", label: "Low Confidence" },
  };

  const conf = confidenceConfig[confidence];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="fade-in"
    >
      <div className="enterprise-card p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3 pb-3 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Brain className="w-4 h-4 text-primary" />
            </div>
            <span className="text-sm font-medium text-foreground">DocuMind Response</span>
          </div>
          <div className="flex items-center gap-2">
            {isStreaming ? (
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-primary/10 text-primary text-xs">
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Generating...</span>
              </div>
            ) : (
              <span className="text-xs text-muted-foreground font-mono">
                {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="mb-4">
          <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
            {content}
            {isStreaming && <span className="streaming-cursor" />}
          </p>
        </div>

        {/* Citations */}
        {citations.length > 0 && !isStreaming && (
          <div className="mb-4 pt-3 border-t border-border">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-citation" />
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Citations ({citations.length})
              </span>
            </div>
            <div className="space-y-2">
              {citations.map((citation) => (
                <div
                  key={citation.id}
                  className="group p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-citation">
                          {citation.document_title || citation.document}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          Page {citation.page}
                          {citation.total_pages && citation.total_pages > 1 && ` of ${citation.total_pages}`}
                        </span>
                        {citation.relevance_score && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary font-mono">
                            {citation.relevance_score}%
                          </span>
                        )}
                      </div>
                      {citation.section_header && (
                        <div className="text-xs text-muted-foreground/80 mb-1 italic">
                          Section: {citation.section_header}
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">
                        "{citation.excerpt}"
                      </p>
                      {citation.chunk_index !== undefined && citation.total_chunks && citation.total_chunks > 1 && (
                        <div className="text-xs text-muted-foreground/60 mt-1">
                          Chunk {citation.chunk_index + 1} of {citation.total_chunks}
                        </div>
                      )}
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-0.5" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer: Confidence + Metrics */}
        {!isStreaming && (
          <div className="flex items-center justify-between pt-3 border-t border-border">
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${conf.bg} text-xs font-medium ${conf.color}`}>
              {confidence === "high" ? (
                <CheckCircle2 className="w-3 h-3" />
              ) : (
                <AlertTriangle className="w-3 h-3" />
              )}
              <span>{conf.label}</span>
            </div>

            {(ttft || totalTime || tokensUsed) && (
              <div className="flex items-center gap-3 text-xs text-muted-foreground font-mono">
                {ttft && (
                  <span className="flex items-center gap-1">
                    <span className="text-muted-foreground/60">TTFT:</span>
                    <span className="text-foreground">{ttft}ms</span>
                  </span>
                )}
                {totalTime && (
                  <span className="flex items-center gap-1">
                    <span className="text-muted-foreground/60">Total:</span>
                    <span className="text-foreground">{totalTime}ms</span>
                  </span>
                )}
                {tokensUsed && (
                  <span className="flex items-center gap-1">
                    <span className="text-muted-foreground/60">Tokens:</span>
                    <span className="text-foreground">{tokensUsed}</span>
                  </span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default AIResponse;
