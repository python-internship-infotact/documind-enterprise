import { useState, useRef, useCallback } from "react";

interface Message {
  id: string;
  type: "user" | "ai" | "refusal";
  content: string;
  timestamp: Date;
  citations?: Array<{
    id: string;
    document: string;
    page: number;
    excerpt: string;
  }>;
  confidence?: "high" | "medium" | "low";
  ttft?: number;
  totalTime?: number;
  tokensUsed?: number;
  refusalReason?: string;
  refusalSuggestions?: string[];
}

interface Document {
  id: string;
  name: string;
  pages: number;
  indexed: boolean;
}

// Backend API configuration
const API_BASE = 'http://localhost:8000';

export const useConversation = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isRetrieving, setIsRetrieving] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentMetrics, setCurrentMetrics] = useState({
    ttft: 0,
    totalTime: 0,
    tokensUsed: 0,
  });
  
  const sessionId = useRef(`session_${Date.now()}`);

  const uploadDocument = useCallback(async (file: File): Promise<boolean> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        
        // Add document to list
        const newDoc: Document = {
          id: result.document_id || Date.now().toString(),
          name: file.name,
          pages: result.pages || 1,
          indexed: true,
        };
        
        setDocuments(prev => [...prev, newDoc]);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Document upload failed:', error);
      return false;
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setIsRetrieving(true);

    const startTime = Date.now();
    let firstTokenTime: number | null = null;
    let fullResponse = '';
    let sources: any[] = [];

    try {
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: content,
          session_id: sessionId.current,
          include_sources: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      setIsRetrieving(false);
      setIsStreaming(true);

      // Create AI message placeholder
      const aiMessageId = `ai-${Date.now()}`;
      const aiMessage: Message = {
        id: aiMessageId,
        type: "ai",
        content: "",
        timestamp: new Date(),
        citations: [],
        confidence: "medium",
      };

      setMessages((prev) => [...prev, aiMessage]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'sources') {
                  sources = data.sources || [];
                  
                } else if (data.type === 'token') {
                  if (firstTokenTime === null) {
                    firstTokenTime = Date.now() - startTime;
                    setCurrentMetrics(prev => ({ ...prev, ttft: firstTokenTime! }));
                  }

                  fullResponse += data.content || '';
                  
                  // Update streaming message
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === aiMessageId
                        ? { ...msg, content: fullResponse }
                        : msg
                    )
                  );

                } else if (data.type === 'error') {
                  // Handle refusal
                  const refusalMessage: Message = {
                    id: `refusal-${Date.now()}`,
                    type: "refusal",
                    content: "",
                    timestamp: new Date(),
                    refusalReason: data.error,
                    refusalSuggestions: [
                      "Try asking about uploaded documents",
                      "Rephrase with specific document references",
                      "Upload relevant documentation first",
                    ],
                  };

                  setMessages((prev) => 
                    prev.slice(0, -1).concat([refusalMessage])
                  );
                  
                  setIsStreaming(false);
                  setIsLoading(false);
                  return;

                } else if (data.type === 'metadata') {
                  if (data.metadata?.latency_metrics) {
                    const metrics = data.metadata.latency_metrics;
                    setCurrentMetrics({
                      ttft: (metrics.time_to_first_token || 0) * 1000,
                      totalTime: metrics.total_processing_time || 0,
                      tokensUsed: Math.floor(fullResponse.length / 4),
                    });
                  }

                } else if (data.type === 'done') {
                  // Finalize message with citations
                  const citations = sources.map((source, index) => ({
                    id: index.toString(),
                    document: source.source_file || 'Unknown',
                    page: source.page_number || 1,
                    excerpt: source.content_preview || '',
                  }));

                  const totalTime = Date.now() - startTime;
                  const tokensUsed = Math.floor(fullResponse.length / 4);

                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === aiMessageId
                        ? {
                            ...msg,
                            citations,
                            confidence: sources.length > 0 ? "high" : "medium",
                            ttft: firstTokenTime,
                            totalTime,
                            tokensUsed,
                          }
                        : msg
                    )
                  );

                  setCurrentMetrics({
                    ttft: firstTokenTime || 0,
                    totalTime,
                    tokensUsed,
                  });

                  break;
                }
              } catch (parseError) {
                console.warn('Failed to parse chunk:', parseError);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      
      // Handle connection error
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: "refusal",
        content: "",
        timestamp: new Date(),
        refusalReason: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        refusalSuggestions: [
          "Check if the backend server is running",
          "Verify the API endpoint is accessible",
          "Try again in a moment",
        ],
      };

      setMessages((prev) => 
        prev.slice(0, -1).concat([errorMessage])
      );
    } finally {
      setIsStreaming(false);
      setIsLoading(false);
      setIsRetrieving(false);
    }
  }, []);

  const deleteDocument = useCallback(async (filename: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove document from list
        setDocuments(prev => prev.filter(doc => doc.name !== filename));
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Document deletion failed:', error);
      return false;
    }
  }, []);

  const clearAllDocuments = useCallback(async (): Promise<boolean> => {
    try {
      // Get all document names and delete them one by one
      const deletePromises = documents.map(doc => deleteDocument(doc.name));
      const results = await Promise.all(deletePromises);
      
      // Return true if all deletions were successful
      return results.every(result => result);
    } catch (error) {
      console.error('Clear all documents failed:', error);
      return false;
    }
  }, [documents, deleteDocument]);

  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }, []);

  return {
    messages,
    isLoading,
    isStreaming,
    isRetrieving,
    currentMetrics,
    documents,
    sendMessage,
    uploadDocument,
    deleteDocument,
    clearAllDocuments,
    checkConnection,
  };
};
