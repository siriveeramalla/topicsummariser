import React from "react";
import { motion } from "framer-motion";

const Hero = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      style={{
        textAlign: "center",
        padding: "52px 20px 28px 20px",
        color: "white",
      }}
    >
      <h1 style={{ fontSize: "3.2rem", marginBottom: "12px" }}>
        Summarize Text, PDFs, and Topics
      </h1>

      <p
        style={{
          fontSize: "1.05rem",
          color: "#cbd5e1",
          maxWidth: "860px",
          margin: "0 auto",
          lineHeight: 1.7,
        }}
      >
        Paste content or upload a PDF to get an AI summary, bullet points, keywords,
        sentiment, and detected language. Choose Short / Medium / Detailed summaries.
      </p>

      <div
        style={{
          marginTop: "18px",
          display: "flex",
          justifyContent: "center",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
        <Badge text="PDF → Text Extraction" />
        <Badge text="Topic Explanation" />
        <Badge text="Keywords + Sentiment" />
        <Badge text="Copy / Download Results" />
      </div>
    </motion.div>
  );
};

const Badge = ({ text }) => (
  <span
    style={{
      fontSize: "12px",
      color: "#e2e8f0",
      border: "1px solid rgba(226,232,240,0.18)",
      background: "rgba(15,23,42,0.35)",
      padding: "7px 10px",
      borderRadius: "999px",
    }}
  >
    {text}
  </span>
);

export default Hero;