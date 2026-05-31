import { render, screen } from "@testing-library/react";
import App from "./App";

afterEach(() => {
  jest.restoreAllMocks();
});

test("renders backend status screen", async () => {
  jest.spyOn(global, "fetch").mockResolvedValue({
    json: async () => ({ data: { status: "ok" } }),
  });

  render(<App />);
  expect(screen.getByText(/Frontend działa/i)).toBeInTheDocument();
  expect(await screen.findByText(/Status backendu:/i)).toBeInTheDocument();
  expect(await screen.findByText("ok")).toBeInTheDocument();
});
