import React from "react";

const Loader = () => {
  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <div
        style={{
          width: "50px",
          height: "50px",
          border: "5px solid #e2e8f0",
          borderTop: "5px solid #f97316",
          borderRadius: "50%",
          margin: "0 auto",
          animation: "spin 1s linear infinite",
        }}
      />

      <p style={{ marginTop: "10px" }}>
        AI is analyzing your document...
      </p>

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default Loader;