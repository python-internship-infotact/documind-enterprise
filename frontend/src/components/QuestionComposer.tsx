import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface QuestionComposerProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
  disabled?: boolean;
  isConnected?: boolean;
}

type QueryQuality = "good" | "needs-refinement" | "out-of-scope" | null;

const QuestionComposer = ({ onSubmit, isLoading, disabled, isConnected = true }: QuestionComposerProps) => {
  const [input, setInput] = useState("");
  const [queryQuality, setQueryQuality] = useState<QueryQuality>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Simple heuristic for query quality indicator
  useEffect(() => {
    if (input.length === 0) {
      setQueryQuality(null);
      return;
    }

    // Simulate quality detection
    const lowercaseInput = input.toLowerCase();
    if (
      lowercaseInput.includes("document") ||
      lowercaseInput.includes("policy") ||
      lowercaseInput.includes("procedure") ||
      lowercaseInput.includes("refund") ||
      lowercaseInput.includes("sop") ||
      lowercaseInput.includes("guideline")
    ) {
      setQueryQuality("good");
    } else if (
      lowercaseInput.includes("weather") ||
      lowercaseInput.includes("news") ||
      lowercaseInput.includes("sports") ||
      lowercaseInput.includes("who is") ||
      lowercaseInput.includes("what year")
    ) {
      setQueryQuality("out-of-scope");
    } else if (input.length > 5) {
      setQueryQuality("needs-refinement");
    } else {
      setQueryQuality(null);
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading && !disabled && isConnected) {
      onSubmit(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const qualityConfig = {
    good: {
      color: "text-success",
      bg: "bg-success/10",
      border: "border-success/30",
      label: "Query matches document scope",
      icon: "✓",
    },
    "needs-refinement": {
      color: "text-warning",
      bg: "bg-warning/10",
      border: "border-warning/30",
      label: "Consider adding document context",
      icon: "!",
    },
    "out-of-scope": {
      color: "text-destructive",
      bg: "bg-destructive/10",
      border: "border-destructive/30",
      label: "May be outside document scope",
      icon: "✕",
    },
  };

  return (
    <div className="border-t border-border bg-card/50 backdrop-blur-sm p-4">
      <form onSubmit={handleSubmit}>
        <div className={`relative rounded-lg border bg-background transition-colors ${
          queryQuality ? qualityConfig[queryQuality].border : "border-border"
        } focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/20`}>
          {/* Quality Indicator */}
          <AnimatePresence>
            {queryQuality && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`absolute -top-8 left-0 flex items-center gap-1.5 px-2 py-1 rounded-md text-xs ${qualityConfig[queryQuality].bg} ${qualityConfig[queryQuality].color}`}
              >
                <span className="font-mono">{qualityConfig[queryQuality].icon}</span>
                <span>{qualityConfig[queryQuality].label}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex items-end gap-2 p-2">
            <div className="p-2">
              <Sparkles className="w-4 h-4 text-muted-foreground" />
            </div>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isConnected ? "Ask a question about your documents..." : "Backend disconnected - check server status"}
              disabled={isLoading || disabled || !isConnected}
              rows={1}
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none min-h-[24px] max-h-[120px] py-1"
              style={{ height: "auto" }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading || disabled || !isConnected}
              className="p-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        <p className="text-xs text-muted-foreground mt-2 text-center">
          Press <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs font-mono">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 rounded bg-muted text-xs font-mono">Shift+Enter</kbd> for new line
        </p>
      </form>
    </div>
  );
};

export default QuestionComposer;
