import { useState } from "react";
import axios from "axios";

const Index = () => {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [simple, setSimple] = useState("");
  const [bullets, setBullets] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [sentiment, setSentiment] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [file, setFile] = useState(null);

  const handleSubmit = async () => {
    if (!text.trim() && !file) return;

    setIsLoading(true);

    try {
      const formData = new FormData();

      if (file) {
        formData.append("file", file);
      } else {
        formData.append("text", text);
      }

      const response = await axios.post(
        "http://127.0.0.1:8000/api/summarize/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setSummary(response.data.summary || "");
      setSimple(response.data.simple_explanation || "");
      setBullets(response.data.bullets || []);
      setKeywords(response.data.keywords || []);
      setSentiment(response.data.sentiment || "");

    } catch (error) {
      console.error(error);
      alert("Error connecting to backend");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: "40px",
        fontFamily: "Arial, sans-serif",
        maxWidth: "800px",
        margin: "0 auto",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
      }}
    >
      <header style={{ textAlign: "center", marginBottom: "40px" }}>
        <h1
          style={{
            fontSize: "2.5rem",
            color: "#1e293b",
            marginBottom: "10px",
          }}
        >
          AI Topic Summarizer
        </h1>
        <p style={{ color: "#64748b", fontSize: "1.1rem" }}>
          Transform lengthy content into clear, concise summaries
        </p>
      </header>

      <div
        style={{
          backgroundColor: "#ffffff",
          borderRadius: "12px",
          border: "1px solid #e2e8f0",
          overflow: "hidden",
          marginBottom: "20px",
        }}
      >
        <div
          style={{
            padding: "12px 16px",
            backgroundColor: "#f1f5f9",
            borderBottom: "1px solid #e2e8f0",
            fontSize: "14px",
            color: "#64748b",
          }}
        >
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
            boxSizing: "border-box",
          }}
        />

        {/* Added File Upload (no style change) */}
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ margin: "10px 16px" }}
        />
      </div>

      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <button
          onClick={handleSubmit}
          disabled={isLoading || (!text.trim() && !file)}
          style={{
            padding: "14px 32px",
            backgroundColor: isLoading ? "#94a3b8" : "#f97316",
            color: "#ffffff",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: (!text.trim() && !file) ? 0.5 : 1,
          }}
        >
          {isLoading ? "Summarizing..." : "✨ Summarize"}
        </button>
      </div>

      {summary && (
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "12px",
            border: "1px solid #fed7aa",
            overflow: "hidden",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              padding: "12px 16px",
              backgroundColor: "#fff7ed",
              borderBottom: "1px solid #fed7aa",
              fontSize: "14px",
              fontWeight: "600",
              color: "#1e293b",
            }}
          >
            💡 Summary
          </div>
          <div style={{ padding: "20px" }}>
            <p style={{ color: "#334155", lineHeight: "1.7", margin: 0 }}>
              {summary}
            </p>
          </div>
        </div>
      )}

      {bullets.length > 0 && (
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              padding: "12px 16px",
              backgroundColor: "#f1f5f9",
              borderBottom: "1px solid #e2e8f0",
              fontSize: "14px",
              fontWeight: "600",
              color: "#1e293b",
            }}
          >
            📌 Bullet Points
          </div>
          <div style={{ padding: "20px" }}>
            <ul style={{ margin: 0, paddingLeft: "20px", color: "#334155" }}>
              {bullets.map((point, index) => (
                <li key={index} style={{ marginBottom: "8px" }}>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {simple && (
        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              padding: "12px 16px",
              backgroundColor: "#f1f5f9",
              borderBottom: "1px solid #e2e8f0",
              fontSize: "14px",
              fontWeight: "600",
              color: "#1e293b",
            }}
          >
            🧒 Explain Like I’m 10
          </div>
          <div style={{ padding: "20px" }}>
            <p style={{ color: "#334155", lineHeight: "1.7", margin: 0 }}>
              {simple}
            </p>
          </div>
        </div>
      )}

      {keywords.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3>🔑 Keywords</h3>
          <p>{keywords.join(", ")}</p>
        </div>
      )}

      {sentiment && (
        <div style={{ marginTop: "10px" }}>
          <h3>📊 Sentiment</h3>
          <p>{sentiment}</p>
        </div>
      )}
    </div>
  );
};

export default Index;