import { Brain, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

const RetrievingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex items-start gap-3"
    >
      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
        <Brain className="w-4 h-4 text-primary" />
      </div>
      <div className="enterprise-card px-4 py-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin text-primary" />
          <span>Retrieving context from knowledge base...</span>
        </div>
      </div>
    </motion.div>
  );
};

export default RetrievingIndicator;
