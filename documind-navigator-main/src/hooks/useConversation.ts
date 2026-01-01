import { useState, useRef, useEffect, useCallback } from "react";

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

// Simulated responses for demo
const simulatedResponses: Record<string, { content: string; citations: Message["citations"]; confidence: Message["confidence"] }> = {
  refund: {
    content: `Based on the uploaded documentation, refunds are processed according to the following policy:

**Standard Refund Timeline:**
Refunds are typically processed within 5-7 business days after the request is approved. The actual credit to the customer's account may take an additional 3-5 business days depending on their financial institution.

**Eligibility Criteria:**
- Product must be returned within 30 days of purchase
- Original receipt or proof of purchase is required
- Items must be in original, unopened condition
- Digital products are non-refundable after download

**Exception Handling:**
For orders over $500, manager approval is required before processing. Expedited refunds can be requested for VIP customers through the escalation channel.`,
    citations: [
      { id: "1", document: "RefundPolicy_2024.pdf", page: 14, excerpt: "Refunds are processed within 5-7 business days after approval..." },
      { id: "2", document: "CustomerService_SOP.pdf", page: 7, excerpt: "Items must be returned in original, unopened condition..." },
      { id: "3", document: "VIP_Guidelines.pdf", page: 3, excerpt: "Expedited refunds available through escalation channel..." },
    ],
    confidence: "high",
  },
  policy: {
    content: `According to the corporate policy documentation:

**Employee Conduct Standards:**
All employees are expected to maintain professional conduct during business hours. The dress code is business casual for office days, with exceptions for client-facing meetings where formal attire is required.

**Remote Work Policy:**
Eligible employees may work remotely up to 3 days per week with manager approval. Core collaboration hours are 10 AM - 3 PM in local timezone when all team members should be available.

**Performance Reviews:**
Annual performance reviews are conducted in Q4, with mid-year check-ins in Q2. Goals should be set within the first 30 days of each fiscal year.`,
    citations: [
      { id: "1", document: "HR_Policy_Manual.pdf", page: 22, excerpt: "Dress code is business casual for office days..." },
      { id: "2", document: "Remote_Work_Guidelines.pdf", page: 5, excerpt: "Eligible employees may work remotely up to 3 days per week..." },
    ],
    confidence: "high",
  },
  procedure: {
    content: `The standard operating procedure for this process is as follows:

**Step 1: Initial Assessment**
Evaluate the incoming request against the criteria outlined in Section 3.2 of the SOP manual. Document all findings in the tracking system.

**Step 2: Escalation Path**
If the request meets escalation criteria, forward to the appropriate department head within 24 hours. Include all supporting documentation.

**Step 3: Resolution Timeline**
Standard requests should be resolved within 5 business days. Complex cases may require up to 10 business days with documented justification.

**Step 4: Follow-up**
Send confirmation to all stakeholders within 2 hours of resolution. Update the knowledge base if new edge cases are identified.`,
    citations: [
      { id: "1", document: "Operations_SOP_v3.pdf", page: 12, excerpt: "Evaluate incoming requests against Section 3.2 criteria..." },
      { id: "2", document: "Escalation_Matrix.pdf", page: 2, excerpt: "Forward to department head within 24 hours..." },
    ],
    confidence: "medium",
  },
};

const outOfScopeKeywords = ["weather", "sports", "news", "celebrity", "who is", "what year", "how old", "capital of"];

export const useConversation = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isRetrieving, setIsRetrieving] = useState(false);
  const [currentMetrics, setCurrentMetrics] = useState({
    ttft: 0,
    totalTime: 0,
    tokensUsed: 0,
  });
  
  const streamingContentRef = useRef("");

  const simulateStreaming = useCallback((
    fullContent: string,
    messageId: string,
    onComplete: () => void
  ) => {
    const words = fullContent.split(" ");
    let currentIndex = 0;
    streamingContentRef.current = "";

    const streamInterval = setInterval(() => {
      if (currentIndex < words.length) {
        const wordsToAdd = Math.min(2, words.length - currentIndex);
        const newWords = words.slice(currentIndex, currentIndex + wordsToAdd).join(" ");
        streamingContentRef.current += (currentIndex > 0 ? " " : "") + newWords;
        currentIndex += wordsToAdd;

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId
              ? { ...msg, content: streamingContentRef.current }
              : msg
          )
        );
      } else {
        clearInterval(streamInterval);
        onComplete();
      }
    }, 50);
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

    // Simulate retrieval delay
    await new Promise((resolve) => setTimeout(resolve, 800));
    setIsRetrieving(false);

    const ttft = Date.now() - startTime;
    setCurrentMetrics((prev) => ({ ...prev, ttft }));

    const lowerContent = content.toLowerCase();

    // Check for out-of-scope
    const isOutOfScope = outOfScopeKeywords.some((kw) => lowerContent.includes(kw));

    if (isOutOfScope) {
      const refusalMessage: Message = {
        id: `refusal-${Date.now()}`,
        type: "refusal",
        content: "",
        timestamp: new Date(),
        refusalReason: "This question cannot be answered using the currently loaded documents. The query appears to be seeking information outside the corporate knowledge base scope.",
        refusalSuggestions: [
          "Rephrase with specific document or policy references",
          "Ask about internal procedures, guidelines, or SOPs",
          "Upload relevant documentation to expand the knowledge base",
        ],
      };

      setMessages((prev) => [...prev, refusalMessage]);
      setIsLoading(false);
      setCurrentMetrics({
        ttft,
        totalTime: Date.now() - startTime,
        tokensUsed: 0,
      });
      return;
    }

    // Find matching response
    let response = simulatedResponses.procedure; // default
    if (lowerContent.includes("refund")) {
      response = simulatedResponses.refund;
    } else if (lowerContent.includes("policy") || lowerContent.includes("hr") || lowerContent.includes("remote")) {
      response = simulatedResponses.policy;
    }

    const aiMessage: Message = {
      id: `ai-${Date.now()}`,
      type: "ai",
      content: "",
      timestamp: new Date(),
      citations: response.citations,
      confidence: response.confidence,
    };

    setMessages((prev) => [...prev, aiMessage]);
    setIsStreaming(true);

    simulateStreaming(response.content, aiMessage.id, () => {
      const totalTime = Date.now() - startTime;
      const tokensUsed = Math.floor(response.content.length / 4);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessage.id
            ? { ...msg, ttft, totalTime, tokensUsed }
            : msg
        )
      );

      setCurrentMetrics({ ttft, totalTime, tokensUsed });
      setIsStreaming(false);
      setIsLoading(false);
    });
  }, [simulateStreaming]);

  return {
    messages,
    isLoading,
    isStreaming,
    isRetrieving,
    currentMetrics,
    sendMessage,
  };
};
