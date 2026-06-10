import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import LoginPage from "../pages/LoginPage";
import { AuthProvider } from "../AuthContext";

jest.mock("../api", () => ({
  api: {
    login: jest.fn(),
    me: jest.fn(),
    refreshSession: jest.fn(),
  },
  authStorage: {
    getToken: jest.fn(() => null),
    getRefreshToken: jest.fn(() => null),
    getUser: jest.fn(() => null),
    saveSession: jest.fn(),
    clear: jest.fn(),
  },
}));

const { api } = require("../api");

function renderPage() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  );
}

test("loguje użytkownika poprawnie", async () => {
  api.login.mockResolvedValue({
    accessToken: "token",
    refreshToken: "refresh",
    user: {
      id: "1",
      firstName: "Jan",
      lastName: "Kowalski",
      email: "jan@example.com",
      roles: ["PATIENT"],
    },
  });

  renderPage();

  fireEvent.change(screen.getByLabelText(/Email/i), {
    target: { value: "jan@example.com" },
  });

  fireEvent.change(screen.getByLabelText(/Hasło/i), {
    target: { value: "Password123!" },
  });

  fireEvent.click(screen.getByRole("button", { name: /Zaloguj/i }));

  await waitFor(() => {
    expect(api.login).toHaveBeenCalledWith("jan@example.com", "Password123!");
  });
});