import { Brain, FileText, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const WelcomeMessage = () => {
  const features = [
    {
      icon: FileText,
      title: "Document-Grounded Answers",
      description: "Every response is backed by citations from your uploaded documents",
    },
    {
      icon: Brain,
      title: "Hallucination Guardrails",
      description: "Out-of-scope queries are refused to maintain accuracy",
    },
    {
      icon: Sparkles,
      title: "Real-Time Streaming",
      description: "Watch responses generate token-by-token with live metrics",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center py-12"
    >
      <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6 glow-blue">
        <Brain className="w-8 h-8 text-primary" />
      </div>

      <h2 className="text-xl font-semibold text-foreground mb-2">
        Welcome to DocuMind Enterprise
      </h2>
      <p className="text-sm text-muted-foreground text-center max-w-md mb-8">
        Ask questions about your corporate documents. All answers are grounded in your knowledge base with full citation transparency.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl w-full px-4">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index }}
            className="enterprise-card p-4 text-center"
          >
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-3">
              <feature.icon className="w-5 h-5 text-primary" />
            </div>
            <h3 className="text-sm font-medium text-foreground mb-1">{feature.title}</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">{feature.description}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-8 p-4 rounded-lg bg-muted/30 border border-border max-w-md w-full">
        <p className="text-xs text-muted-foreground text-center">
          <span className="text-warning font-medium">Demo Mode:</span> Try asking about refund policies, SOPs, or company guidelines
        </p>
      </div>
    </motion.div>
  );
};

export default WelcomeMessage;
