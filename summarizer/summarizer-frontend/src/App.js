import { useMemo, useState } from "react";
import axios from "axios";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Loader from "./components/Loader";

const API_URL = "http://127.0.0.1:8000/api/summarize/";

const App = () => {
  const [mode, setMode] = useState("");

  const [text, setText] = useState("");
  const [topic, setTopic] = useState("");
  const [summaryLength, setSummaryLength] = useState("medium"); // short|medium|long
  const [quizCount, setQuizCount] = useState(5);

  const [summary, setSummary] = useState("");
  const [bullets, setBullets] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [sentiment, setSentiment] = useState("");
  const [language, setLanguage] = useState("");
  const [quiz, setQuiz] = useState([]);

  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const clearResults = () => {
    setSummary("");
    setBullets([]);
    setKeywords([]);
    setSentiment("");
    setLanguage("");
    setQuiz([]);
  };

  const textStats = useMemo(() => {
    const trimmed = text.trim();
    const words = trimmed ? trimmed.split(/\s+/).length : 0;
    const chars = trimmed.length;
    return { words, chars };
  }, [text]);

  const handleSubmit = async () => {
    if (
      (mode === "text" && !text.trim() && !file) ||
      (mode === "topic" && !topic.trim())
    ) {
      return;
    }

    setIsLoading(true);
    clearResults();

    try {
      const formData = new FormData();

      if (mode === "topic") {
        formData.append("topic", topic.trim());
      } else {
        if (file) {
          formData.append("file", file);
        } else {
          formData.append("text", text);
        }
      }

      formData.append("summary_length", summaryLength);
      formData.append("quiz_count", String(quizCount));

      const response = await axios.post(API_URL, formData);

      if (!response.data?.ok) {
        alert(response.data?.error?.message || "Backend Error");
        return;
      }

      const data = response.data.data || {};

      setSummary(data.summary || "");
      setBullets(data.bullets || []);
      setKeywords(data.keywords || []);
      setSentiment(data.sentiment || "");
      setLanguage(data.language || "");
      setQuiz(Array.isArray(data.quiz) ? data.quiz : []);
    } catch (error) {
      if (error.response) {
        alert(error.response.data?.error?.message || "Server Error");
      } else {
        alert("Cannot connect to backend server");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!mode) {
    return (
      <div
        style={{
          background: "linear-gradient(to bottom, #0f172a, #1e293b)",
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          color: "white",
          fontFamily: "Arial",
          padding: "20px",
        }}
      >
        <h1 style={{ fontSize: "3rem", marginBottom: "20px", textAlign: "center" }}>
          AI Document Intelligence Platform
        </h1>

        <p style={{ marginBottom: "40px", fontSize: "18px", color: "#cbd5e1", textAlign: "center" }}>
          Choose what you want to do
        </p>

        <div style={{ display: "flex", gap: "30px", flexWrap: "wrap", justifyContent: "center" }}>
          <div
            onClick={() => setMode("text")}
            style={{
              backgroundColor: "#ffffff",
              color: "#0f172a",
              width: "320px",
              padding: "40px",
              borderRadius: "20px",
              cursor: "pointer",
              textAlign: "center",
              boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
            }}
          >
            <h2>📄 Summarize Lengthy Text</h2>
            <p style={{ marginTop: "20px", lineHeight: "1.7" }}>
              Upload PDFs or paste long articles, research papers, notes, and documents for AI summarization.
            </p>
          </div>

          <div
            onClick={() => setMode("topic")}
            style={{
              backgroundColor: "#ffffff",
              color: "#0f172a",
              width: "320px",
              padding: "40px",
              borderRadius: "20px",
              cursor: "pointer",
              textAlign: "center",
              boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
            }}
          >
            <h2>🧠 Summarize a Topic</h2>
            <p style={{ marginTop: "20px", lineHeight: "1.7" }}>
              Enter any topic and get a structured summary with key points, keywords, and quiz.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: "linear-gradient(to bottom, #0f172a, #1e293b)", minHeight: "100vh" }}>
      <Navbar
        onGoToHome={() => setMode("")}
        onGoToText={() => setMode("text")}
        onGoToTopic={() => setMode("topic")}
      />

      <Hero />

      <div style={{ padding: "40px", fontFamily: "Arial, sans-serif", maxWidth: "900px", margin: "0 auto" }}>
        <button
          onClick={() => setMode("")}
          style={{
            marginBottom: "20px",
            padding: "10px 20px",
            border: "none",
            borderRadius: "10px",
            cursor: "pointer",
            backgroundColor: "#ffffff",
            fontWeight: "600",
          }}
        >
          ← Back
        </button>

        <div
          style={{
            backgroundColor: "#ffffff",
            borderRadius: "20px",
            border: "1px solid #334155",
            overflow: "hidden",
            marginBottom: "14px",
            boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
          }}
        >
          <div
            style={{
              padding: "14px 20px",
              backgroundColor: "#f1f5f9",
              borderBottom: "1px solid #e2e8f0",
              fontSize: "14px",
              color: "#64748b",
              fontWeight: "600",
            }}
          >
            {mode === "topic" ? "Enter Topic" : "Upload Document or Paste Text"}
          </div>

          {mode === "topic" && (
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter topic like Artificial Intelligence..."
              style={{
                width: "100%",
                padding: "20px",
                border: "none",
                outline: "none",
                fontSize: "16px",
                boxSizing: "border-box",
              }}
            />
          )}

          {mode === "text" && (
            <>
              <textarea
                rows={10}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste article, research paper, notes, or document text..."
                style={{
                  width: "100%",
                  padding: "20px",
                  border: "none",
                  outline: "none",
                  fontSize: "16px",
                  resize: "vertical",
                  boxSizing: "border-box",
                }}
              />

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0 20px 12px 20px",
                  fontSize: "12px",
                  color: "#64748b",
                }}
              >
                <span>
                  {textStats.words} words • {textStats.chars} characters
                </span>
                {textStats.chars > 0 && textStats.chars < 30 && (
                  <span style={{ color: "#b91c1c" }}>
                    Add more detail for better summarization (min 30 characters).
                  </span>
                )}
              </div>

              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                style={{ margin: "10px 20px 20px 20px" }}
              />
            </>
          )}
        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            justifyContent: "center",
            flexWrap: "wrap",
            marginBottom: "12px",
            color: "#e2e8f0",
          }}
        >
          <span style={{ fontWeight: 700 }}>Summary length:</span>
          <label>
            <input
              type="radio"
              name="summaryLength"
              value="short"
              checked={summaryLength === "short"}
              onChange={(e) => setSummaryLength(e.target.value)}
            />{" "}
            Short
          </label>
          <label>
            <input
              type="radio"
              name="summaryLength"
              value="medium"
              checked={summaryLength === "medium"}
              onChange={(e) => setSummaryLength(e.target.value)}
            />{" "}
            Medium
          </label>
          <label>
            <input
              type="radio"
              name="summaryLength"
              value="long"
              checked={summaryLength === "long"}
              onChange={(e) => setSummaryLength(e.target.value)}
            />{" "}
            Detailed
          </label>
        </div>

        <div
          style={{
            display: "flex",
            gap: "8px",
            justifyContent: "center",
            alignItems: "center",
            marginBottom: "18px",
            color: "#e2e8f0",
          }}
        >
          <span style={{ fontWeight: 700 }}>Quiz questions:</span>
          <select
            value={quizCount}
            onChange={(e) => setQuizCount(Number(e.target.value))}
            style={{ padding: "6px 10px", borderRadius: "8px", border: "none" }}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={7}>7</option>
            <option value={10}>10</option>
          </select>
        </div>

        <div style={{ textAlign: "center", marginBottom: "30px" }}>
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            style={{
              padding: "16px 36px",
              backgroundColor: isLoading ? "#94a3b8" : "#f97316",
              color: "#ffffff",
              border: "none",
              borderRadius: "12px",
              fontSize: "17px",
              fontWeight: "700",
              cursor: isLoading ? "not-allowed" : "pointer",
              minWidth: "220px",
            }}
          >
            {isLoading ? <Loader /> : "✨ Analyze"}
          </button>
        </div>

        {summary && <ResultCard title="💡 AI Summary" content={summary} />}
        {bullets.length > 0 && <ResultCard title="📌 Key Bullet Points" content={bullets} isList={true} />}
        {keywords.length > 0 && <ResultCard title="🔑 Keywords" content={keywords.join(", ")} />}
        {sentiment && <ResultCard title="📊 Sentiment Analysis" content={sentiment} />}
        {language && <ResultCard title="🌍 Detected Language" content={language} />}

        {quiz.length > 0 && (
          <div
            style={{
              backgroundColor: "#ffffff",
              borderRadius: "20px",
              border: "1px solid #e2e8f0",
              marginBottom: "20px",
              boxShadow: "0 10px 20px rgba(0,0,0,0.15)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "14px 20px",
                backgroundColor: "#f8fafc",
                borderBottom: "1px solid #e2e8f0",
                fontSize: "15px",
                fontWeight: "700",
                color: "#1e293b",
              }}
            >
              🧠 AI Quiz
            </div>

            <div style={{ padding: "20px 24px" }}>
              {quiz.map((q, idx) => (
                <div key={idx} style={{ marginBottom: "18px" }}>
                  <p style={{ fontWeight: 700, margin: "0 0 8px 0", color: "#1e293b" }}>
                    Q{idx + 1}. {q.question}
                  </p>
                  <ul style={{ margin: 0, paddingLeft: "20px", color: "#334155", lineHeight: "1.8" }}>
                    {Array.isArray(q.options) &&
                      q.options.map((opt, i) => <li key={i}>{opt}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const ResultCard = ({ title, content, isList }) => {
  const textContent = Array.isArray(content) ? content.join("\n") : String(content ?? "");

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(textContent);
      alert("Copied to clipboard!");
    } catch {
      alert("Copy failed (browser blocked clipboard).");
    }
  };

  const handleDownload = () => {
    const blob = new Blob([textContent], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = title.replace(/[^a-z0-9]+/gi, "_").toLowerCase() + ".txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        backgroundColor: "#ffffff",
        borderRadius: "20px",
        border: "1px solid #e2e8f0",
        overflow: "hidden",
        marginBottom: "20px",
        boxShadow: "0 10px 20px rgba(0,0,0,0.15)",
      }}
    >
      <div
        style={{
          padding: "14px 20px",
          backgroundColor: "#f8fafc",
          borderBottom: "1px solid #e2e8f0",
          fontSize: "15px",
          fontWeight: "700",
          color: "#1e293b",
          display: "flex",
          justifyContent: "space-between",
          gap: "12px",
          alignItems: "center",
        }}
      >
        <span>{title}</span>
        <span style={{ display: "flex", gap: "8px" }}>
          <button onClick={handleCopy} style={miniBtnStyle}>
            Copy
          </button>
          <button onClick={handleDownload} style={miniBtnStyle}>
            Download
          </button>
        </span>
      </div>

      <div style={{ padding: "24px" }}>
        {isList ? (
          <ul style={{ margin: 0, paddingLeft: "20px", color: "#334155", lineHeight: "1.8" }}>
            {content.map((item, index) => (
              <li key={index} style={{ marginBottom: "10px" }}>
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: "#334155", lineHeight: "1.8", margin: 0, fontSize: "16px" }}>{content}</p>
        )}
      </div>
    </div>
  );
};

const miniBtnStyle = {
  padding: "6px 10px",
  borderRadius: "10px",
  border: "1px solid #e2e8f0",
  backgroundColor: "#ffffff",
  cursor: "pointer",
  fontWeight: 700,
};

export default App;