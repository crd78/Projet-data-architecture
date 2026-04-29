import { render, screen } from "@testing-library/react";
import App from "./App";

jest.mock("./pages/DashboardPage", () => function MockDashboardPage() {
  return <main>Urban Data Explorer</main>;
});

test("renders dashboard shell", () => {
  render(<App />);
  expect(screen.getByText(/urban data explorer/i)).toBeInTheDocument();
});
