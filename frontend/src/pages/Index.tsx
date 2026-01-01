import { useState, useRef, useEffect } from "react";
import { PanelLeftOpen } from "lucide-react";
import TopBar from "@/components/TopBar";
import ContextPanel from "@/components/ContextPanel";
import QuestionComposer from "@/components/QuestionComposer";
import MetricsFooter from "@/components/MetricsFooter";
import UserMessage from "@/components/UserMessage";
import AIResponse from "@/components/AIResponse";
import RefusalCard from "@/components/RefusalCard";
import RetrievingIndicator from "@/components/RetrievingIndicator";
import WelcomeMessage from "@/components/WelcomeMessage";
import { useConversation } from "@/hooks/useConversation";
import { AnimatePresence } from "framer-motion";

const Index = () => {
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    isStreaming,
    isRetrieving,
    currentMetrics,
    documents,
    sendMessage,
    uploadDocument,
    checkConnection,
  } = useConversation();

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      const connected = await checkConnection();
      setIsConnected(connected);
    };
    
    checkBackend();
    
    // Check connection every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isRetrieving]);

  const handleSubmit = (question: string) => {
    sendMessage(question);
  };

  const handleDocumentUpload = async (file: File) => {
    const success = await uploadDocument(file);
    if (!success) {
      // Handle upload error - could show a toast notification
      console.error('Failed to upload document:', file.name);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Bar */}
      <TopBar isConnected={isConnected} documentsLoaded={documents.length} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Context Panel */}
        <ContextPanel
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          documents={documents}
          vectorStatus={isConnected ? "ready" : "disconnected"}
          onDocumentUpload={handleDocumentUpload}
        />

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Toggle Panel Button (when closed) */}
          {!isPanelOpen && (
            <button
              onClick={() => setIsPanelOpen(true)}
              className="absolute left-4 top-20 z-10 p-2 rounded-lg bg-card border border-border hover:bg-muted transition-colors"
            >
              <PanelLeftOpen className="w-4 h-4 text-muted-foreground" />
            </button>
          )}

          {/* Conversation Stream */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.length === 0 ? (
                <WelcomeMessage />
              ) : (
                <>
                  {messages.map((message) => {
                    if (message.type === "user") {
                      return (
                        <UserMessage
                          key={message.id}
                          content={message.content}
                          timestamp={message.timestamp}
                        />
                      );
                    }

                    if (message.type === "refusal") {
                      return (
                        <RefusalCard
                          key={message.id}
                          reason={message.refusalReason || ""}
                          suggestions={message.refusalSuggestions || []}
                          timestamp={message.timestamp}
                        />
                      );
                    }

                    return (
                      <AIResponse
                        key={message.id}
                        content={message.content}
                        citations={message.citations || []}
                        confidence={message.confidence || "medium"}
                        isStreaming={isStreaming && message.id === messages[messages.length - 1]?.id}
                        timestamp={message.timestamp}
                        ttft={message.ttft}
                        totalTime={message.totalTime}
                        tokensUsed={message.tokensUsed}
                      />
                    );
                  })}

                  <AnimatePresence>
                    {isRetrieving && <RetrievingIndicator />}
                  </AnimatePresence>
                </>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Question Composer */}
          <QuestionComposer
            onSubmit={handleSubmit}
            isLoading={isLoading}
            isConnected={isConnected}
          />
        </div>
      </div>

      {/* Metrics Footer */}
      <MetricsFooter
        ttft={currentMetrics.ttft}
        totalTime={currentMetrics.totalTime}
        tokensUsed={currentMetrics.tokensUsed}
        model="Groq Llama"
        isStreaming={isStreaming}
      />
    </div>
  );
};

export default Index;
