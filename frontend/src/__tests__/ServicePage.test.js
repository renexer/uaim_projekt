import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ServicesPage from "../pages/ServicesPage";

jest.mock("../api", () => ({
  api: {
    services: jest.fn(),
  },
}));

const { api } = require("../api");

test("renderuje listę usług", async () => {
  api.services.mockResolvedValue([
    {
      id: "1",
      code: "CONSULT_50",
      name: "Konsultacja psychologiczna",
      description: "Pierwsza konsultacja",
      durationMinutes: 50,
      basePrice: "180.00",
      currency: "PLN",
    },
  ]);

  render(
    <MemoryRouter>
      <ServicesPage />
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(screen.getByText("Konsultacja psychologiczna")).toBeInTheDocument();
  });
});