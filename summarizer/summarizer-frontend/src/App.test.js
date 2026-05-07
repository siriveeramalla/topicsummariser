import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders app title", () => {
  render(<App />);
  const headingElement = screen.getByText(/AI Document Intelligence Platform/i);
  expect(headingElement).toBeInTheDocument();
});