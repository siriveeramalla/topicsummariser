import React from "react";

const Navbar = ({ onGoToHome, onGoToText, onGoToTopic }) => {
  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "16px 28px",
        background: "#0f172a",
        color: "white",
        position: "sticky",
        top: 0,
        zIndex: 1000,
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <button
        onClick={onGoToHome}
        style={{
          background: "transparent",
          border: "none",
          color: "white",
          cursor: "pointer",
          fontWeight: 800,
          letterSpacing: "0.3px",
          fontSize: "18px",
        }}
        title="Go to home"
      >
        AI DocMind
      </button>

      <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
        <NavBtn onClick={onGoToText} label="Summarize Text / PDF" />
        <NavBtn onClick={onGoToTopic} label="Summarize Topic" />

        <span
          style={{
            fontSize: "12px",
            color: "#cbd5e1",
            padding: "6px 10px",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: "999px",
          }}
        >
          Local Demo
        </span>
      </div>
    </nav>
  );
};

const NavBtn = ({ label, onClick }) => (
  <button
    onClick={onClick}
    style={{
      background: "rgba(255,255,255,0.06)",
      border: "1px solid rgba(255,255,255,0.10)",
      color: "white",
      cursor: "pointer",
      padding: "10px 12px",
      borderRadius: "12px",
      fontWeight: 700,
      fontSize: "13px",
    }}
  >
    {label}
  </button>
);

export default Navbar;