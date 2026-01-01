import { FileText, ChevronRight, Database, Shield, X, Upload, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useRef, useState } from "react";

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
  vectorStatus: "ready" | "indexing" | "empty" | "disconnected";
  onDocumentUpload?: (file: File) => Promise<void>;
}

const ContextPanel = ({ isOpen, onClose, documents, vectorStatus, onDocumentUpload }: ContextPanelProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && onDocumentUpload) {
      setIsUploading(true);
      try {
        await onDocumentUpload(file);
      } catch (error) {
        console.error('Upload failed:', error);
      } finally {
        setIsUploading(false);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

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
                  vectorStatus === "disconnected" ? "bg-destructive" :
                  "bg-muted-foreground"
                }`} />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Vector Store
                </span>
              </div>
              <p className="text-sm text-foreground">
                {vectorStatus === "ready" ? "Ready for queries" :
                 vectorStatus === "indexing" ? "Indexing documents..." :
                 vectorStatus === "disconnected" ? "Backend disconnected" :
                 "No documents indexed"}
              </p>
            </div>

            {/* Document Upload */}
            <div className="p-4 border-b border-border">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
              
              <button
                onClick={triggerFileUpload}
                disabled={isUploading || vectorStatus === "disconnected"}
                className="w-full flex items-center gap-2 p-3 rounded-lg border-2 border-dashed border-muted-foreground/30 hover:border-primary/50 hover:bg-muted/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm text-muted-foreground">Uploading...</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Upload PDF Document</span>
                  </>
                )}
              </button>
              
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Only PDF files are supported
              </p>
            </div>

            {/* Documents List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Loaded Documents ({documents.length})
                </span>
              </div>

              {documents.length === 0 ? (
                <div className="text-center py-8">
                  <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">No documents uploaded</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Upload PDF files to start asking questions
                  </p>
                </div>
              ) : (
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
                            {doc.pages} pages • {doc.indexed ? 'Indexed' : 'Processing...'}
                          </p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
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
