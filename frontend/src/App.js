import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthProvider } from "./AuthContext";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import AppointmentsPage from "./pages/AppointmentsPage";
import BookingPage from "./pages/BookingPage";
import ConsultationsPage from "./pages/ConsultationsPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";
import RegisterPage from "./pages/RegisterPage";
import ServicesPage from "./pages/ServicesPage";
import StaffPage from "./pages/StaffPage";
import TherapistDetailsPage from "./pages/TherapistDetailsPage";
import TherapistsPage from "./pages/TherapistsPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="services/:serviceId/therapists" element={<TherapistsPage />} />
        <Route path="therapists" element={<TherapistsPage />} />
        <Route path="therapists/:therapistId" element={<TherapistDetailsPage />} />
        <Route path="booking" element={<BookingPage />} />
        <Route path="appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
        <Route path="consultations" element={<ProtectedRoute><ConsultationsPage /></ProtectedRoute>} />
        <Route path="staff" element={<ProtectedRoute roles={["ADMIN", "THERAPIST"]}><StaffPage /></ProtectedRoute>} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
