
import { useState } from "react";
import {
  Bot,
  Send,
  Sparkles,
  User,
  Loader2,
  RotateCcw,
  MessageSquare,
  AlertCircle
} from "lucide-react";

import { askDatasetAI } from "../services/api";

const suggestedQuestions = [
  "Summarize my business performance.",
  "Which city generates the highest revenue?",
  "What are the biggest data quality problems?",
  "How can I improve my profitability?"
];

function AIChat({ file }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAsk = async (customQuestion) => {
    const currentQuestion = (
      customQuestion ?? question
    ).trim();

    if (!currentQuestion || !file || loading) return;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentQuestion
      }
    ]);

    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const result = await askDatasetAI(file, currentQuestion);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.answer
        }
      ]);

    } catch (err) {
      console.error("AI chat error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to get an AI response. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    handleAsk();
  };

  const clearConversation = () => {
    setMessages([]);
    setError("");
    setQuestion("");
  };

  return (
    <section className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5">

        <div className="flex items-center justify-between gap-4">

          <div className="flex items-center gap-3">

            <div className="bg-white/20 p-3 rounded-xl">
              <Sparkles className="text-white" size={23} />
            </div>

            <div>
              <h2 className="text-lg font-bold text-white">
                InsightIQ AI Assistant
              </h2>

              <p className="text-sm text-blue-100 mt-1">
                Ask questions about your uploaded dataset
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={clearConversation}
            disabled={messages.length === 0 || loading}
            className="flex items-center gap-2 text-sm text-white/90
              hover:text-white disabled:opacity-40 transition"
          >
            <RotateCcw size={16} />
            <span className="hidden sm:inline">Clear chat</span>
          </button>

        </div>

      </div>

      {/* Chat Area */}
      <div className="p-5 sm:p-6">

        {messages.length === 0 ? (

          <div className="py-8 text-center">

            <div className="bg-blue-50 w-16 h-16 rounded-2xl
              flex items-center justify-center mx-auto mb-4"
            >
              <Bot className="text-blue-600" size={32} />
            </div>

            <h3 className="text-lg font-semibold text-slate-800">
              What would you like to know?
            </h3>

            <p className="text-sm text-slate-500 mt-2">
              Ask InsightIQ to analyze your data, explain trends,
              or identify business opportunities.
            </p>

            {/* Suggested Questions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-7">

              {suggestedQuestions.map((item) => (

                <button
                  key={item}
                  type="button"
                  onClick={() => handleAsk(item)}
                  disabled={loading}
                  className="text-left p-4 rounded-xl border border-slate-200
                    text-sm text-slate-600 hover:border-blue-400
                    hover:bg-blue-50 hover:text-blue-700
                    transition disabled:opacity-50"
                >
                  <div className="flex items-start gap-2">
                    <MessageSquare
                      size={16}
                      className="mt-0.5 shrink-0 text-blue-500"
                    />
                    <span>{item}</span>
                  </div>
                </button>

              ))}

            </div>

          </div>

        ) : (

          <div className="space-y-6 max-h-[500px] overflow-y-auto pr-2">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >

                {message.role === "assistant" && (
                  <div className="w-9 h-9 shrink-0 rounded-xl
                    bg-blue-100 flex items-center justify-center"
                  >
                    <Bot className="text-blue-600" size={20} />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    message.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-slate-100 text-slate-800 rounded-bl-sm"
                  }`}
                >
                  <p className="text-sm font-semibold mb-2">
                    {message.role === "user"
                      ? "You"
                      : "InsightIQ AI"}
                  </p>

                  <div className="text-sm leading-7 whitespace-pre-wrap break-words">
                    {message.content}
                  </div>

                </div>

                {message.role === "user" && (
                  <div className="w-9 h-9 shrink-0 rounded-xl
                    bg-blue-600 flex items-center justify-center"
                  >
                    <User className="text-white" size={19} />
                  </div>
                )}

              </div>

            ))}

            {loading && (
              <div className="flex items-center gap-3">

                <div className="w-9 h-9 rounded-xl bg-blue-100
                  flex items-center justify-center"
                >
                  <Bot className="text-blue-600" size={20} />
                </div>

                <div className="bg-slate-100 rounded-xl px-4 py-3
                  flex items-center gap-2"
                >
                  <Loader2
                    size={17}
                    className="animate-spin text-blue-600"
                  />

                  <span className="text-sm text-slate-500">
                    Analyzing your dataset...
                  </span>
                </div>

              </div>
            )}

          </div>

        )}

        {/* Error */}
        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-lg
            bg-red-50 border border-red-200 p-3 text-sm text-red-700"
          >
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            {error}
          </div>
        )}

        {/* Question Input */}
        <form onSubmit={handleSubmit} className="mt-6">

          <div className="flex items-center gap-2 border border-slate-300
            rounded-xl p-2 focus-within:border-blue-500
            focus-within:ring-2 focus-within:ring-blue-100"
          >

            <input
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask anything about your dataset..."
              disabled={loading}
              className="flex-1 min-w-0 px-3 py-2 text-sm outline-none
                text-slate-700 placeholder:text-slate-400
                disabled:bg-white"
            />

            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="bg-blue-600 text-white p-3 rounded-lg
                hover:bg-blue-700 disabled:opacity-40
                disabled:cursor-not-allowed transition"
              aria-label="Send question"
            >
              {loading ? (
                <Loader2 size={19} className="animate-spin" />
              ) : (
                <Send size={19} />
              )}
            </button>

          </div>

          <p className="text-xs text-slate-400 mt-3 text-center">
            AI-generated answers should be checked against your source data.
          </p>

        </form>

      </div>

    </section>
  );
}

export default AIChat;
