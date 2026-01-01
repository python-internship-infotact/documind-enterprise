import { User } from "lucide-react";
import { motion } from "framer-motion";

interface UserMessageProps {
  content: string;
  timestamp: Date;
}

const UserMessage = ({ content, timestamp }: UserMessageProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex gap-3 fade-in"
    >
      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
        <User className="w-4 h-4 text-secondary-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-foreground">You</span>
          <span className="text-xs text-muted-foreground font-mono">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <p className="text-sm text-foreground/90 leading-relaxed">{content}</p>
      </div>
    </motion.div>
  );
};

export default UserMessage;
