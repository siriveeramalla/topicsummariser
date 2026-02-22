import { useState } from "react";
import axios from "axios";

const Index = () => {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/summarize/",
        { text: text }
      );
      setSummary(response.data.summary);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: "40px", 
      fontFamily: "Arial, sans-serif",
      maxWidth: "800px",
      margin: "0 auto",
      backgroundColor: "#f8fafc",
      minHeight: "100vh"
    }}>
      <header style={{ textAlign: "center", marginBottom: "40px" }}>
        <h1 style={{ fontSize: "2.5rem", color: "#1e293b", marginBottom: "10px" }}>
          AI Topic Summarizer
        </h1>
        <p style={{ color: "#64748b", fontSize: "1.1rem" }}>
          Transform lengthy content into clear, concise summaries
        </p>
      </header>

      <div style={{ 
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        border: "1px solid #e2e8f0",
        overflow: "hidden",
        marginBottom: "20px"
      }}>
        <div style={{ 
          padding: "12px 16px",
          backgroundColor: "#f1f5f9",
          borderBottom: "1px solid #e2e8f0",
          fontSize: "14px",
          color: "#64748b"
        }}>
          Input Text
        </div>
        <textarea
          rows={10}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste your article, document, or any text you want to summarize..."
          style={{
            width: "100%",
            padding: "16px",
            border: "none",
            outline: "none",
            fontSize: "16px",
            resize: "vertical",
            boxSizing: "border-box"
          }}
        />
      </div>

      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <button
          onClick={handleSubmit}
          disabled={isLoading || !text.trim()}
          style={{
            padding: "14px 32px",
            backgroundColor: isLoading ? "#94a3b8" : "#f97316",
            color: "#ffffff",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: !text.trim() ? 0.5 : 1
          }}
        >
          {isLoading ? "Summarizing..." : "✨ Summarize"}
        </button>
      </div>

      {summary && (
        <div style={{ 
          backgroundColor: "#ffffff",
          borderRadius: "12px",
          border: "1px solid #fed7aa",
          overflow: "hidden"
        }}>
          <div style={{ 
            padding: "12px 16px",
            backgroundColor: "#fff7ed",
            borderBottom: "1px solid #fed7aa",
            fontSize: "14px",
            fontWeight: "600",
            color: "#1e293b"
          }}>
            💡 Summary
          </div>
          <div style={{ padding: "20px" }}>
            <p style={{ color: "#334155", lineHeight: "1.7", margin: 0 }}>
              {summary}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
