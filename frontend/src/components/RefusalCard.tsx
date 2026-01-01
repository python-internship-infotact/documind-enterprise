import { ShieldX, AlertOctagon, FileQuestion, RotateCcw } from "lucide-react";
import { motion } from "framer-motion";

interface RefusalCardProps {
  reason: string;
  suggestions: string[];
  timestamp: Date;
}

const RefusalCard = ({ reason, suggestions, timestamp }: RefusalCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="fade-in"
    >
      <div className="enterprise-card border-destructive/30 glow-destructive p-4">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4 pb-3 border-b border-destructive/20">
          <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center">
            <ShieldX className="w-5 h-5 text-destructive" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-destructive flex items-center gap-2">
              <AlertOctagon className="w-4 h-4" />
              Outside Knowledge Boundary
            </h3>
            <p className="text-xs text-muted-foreground">
              {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
        </div>

        {/* Reason */}
        <div className="mb-4">
          <p className="text-sm text-foreground/90 leading-relaxed">
            {reason}
          </p>
        </div>

        {/* Suggestions */}
        <div className="p-3 rounded-lg bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <FileQuestion className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Try Instead
            </span>
          </div>
          <ul className="space-y-1.5">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start gap-2 text-xs text-muted-foreground">
                <span className="text-primary mt-0.5">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Action */}
        <div className="mt-4 pt-3 border-t border-border">
          <button className="flex items-center gap-2 text-xs text-primary hover:text-primary/80 transition-colors">
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Rephrase Question</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default RefusalCard;
