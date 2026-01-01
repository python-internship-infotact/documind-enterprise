import { FileText, ChevronRight, Database, Shield, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Document {
  id: string;
  name: string;
  pages: number;
  indexed: boolean;
}

interface ContextPanelProps {
  isOpen: boolean;
  onClose: () => void;
  documents: Document[];
  vectorStatus: "ready" | "indexing" | "empty";
}

const ContextPanel = ({ isOpen, onClose, documents, vectorStatus }: ContextPanelProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.aside
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 300, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="border-r border-border bg-sidebar h-full overflow-hidden flex-shrink-0"
        >
          <div className="w-[300px] h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Knowledge Context</span>
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded hover:bg-muted transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            {/* Vector Store Status */}
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-2 h-2 rounded-full ${
                  vectorStatus === "ready" ? "bg-success" :
                  vectorStatus === "indexing" ? "bg-warning animate-pulse" :
                  "bg-muted-foreground"
                }`} />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Vector Store
                </span>
              </div>
              <p className="text-sm text-foreground">
                {vectorStatus === "ready" ? "Ready for queries" :
                 vectorStatus === "indexing" ? "Indexing documents..." :
                 "No documents indexed"}
              </p>
            </div>

            {/* Documents List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Loaded Documents
                </span>
              </div>

              <div className="space-y-2">
                {documents.map((doc) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="group p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                  >
                    <div className="flex items-start gap-2">
                      <FileText className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                          {doc.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {doc.pages} pages indexed
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Scope Notice */}
            <div className="p-4 border-t border-border bg-muted/30">
              <div className="flex items-start gap-2">
                <Shield className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-medium text-warning mb-1">Scope Boundary</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Answers are strictly limited to uploaded documents. Out-of-scope queries will be refused.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
};

export default ContextPanel;
