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

const sampleDocuments = [
  { id: "1", name: "RefundPolicy_2024.pdf", pages: 24, indexed: true },
  { id: "2", name: "CustomerService_SOP.pdf", pages: 18, indexed: true },
  { id: "3", name: "HR_Policy_Manual.pdf", pages: 45, indexed: true },
  { id: "4", name: "Remote_Work_Guidelines.pdf", pages: 12, indexed: true },
  { id: "5", name: "VIP_Guidelines.pdf", pages: 8, indexed: true },
];

const Index = () => {
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    isStreaming,
    isRetrieving,
    currentMetrics,
    sendMessage,
  } = useConversation();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isRetrieving]);

  const handleSubmit = (question: string) => {
    sendMessage(question);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Bar */}
      <TopBar isConnected={true} documentsLoaded={sampleDocuments.length} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Context Panel */}
        <ContextPanel
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          documents={sampleDocuments}
          vectorStatus="ready"
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
          />
        </div>
      </div>

      {/* Metrics Footer */}
      <MetricsFooter
        ttft={currentMetrics.ttft}
        totalTime={currentMetrics.totalTime}
        tokensUsed={currentMetrics.tokensUsed}
        model="GPT-4o"
        isStreaming={isStreaming}
      />
    </div>
  );
};

export default Index;
