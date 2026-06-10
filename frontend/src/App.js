import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import "./App.css";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import AppointmentsPage from "./pages/AppointmentsPage";
import BookingPage from "./pages/BookingPage";
import ConsultationsPage from "./pages/ConsultationsPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ServicesPage from "./pages/ServicesPage";
import StaffPage from "./pages/StaffPage";
import TherapistDetailsPage from "./pages/TherapistDetailsPage";
import TherapistsPage from "./pages/TherapistsPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import AdminServicesPage from "./pages/AdminServicesPage";
import AdminTherapistsPage from "./pages/AdminTherapistsPage";
import AdminAvailabilityPage from "./pages/AdminAvailabilityPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="services" element={<ServicesPage />} />
            <Route path="therapists" element={<TherapistsPage />} />
            <Route path="therapists/:therapistId" element={<TherapistDetailsPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="booking" element={<BookingPage />} />
              <Route path="appointments" element={<AppointmentsPage />} />
              <Route path="consultations" element={<ConsultationsPage />} />
            </Route>

            <Route element={<RoleRoute roles={["ADMIN", "THERAPIST"]} />}>
              <Route path="staff" element={<StaffPage />} />
            </Route>

            <Route element={<RoleRoute roles={["ADMIN"]} />}>
              <Route path="admin" element={<AdminDashboardPage />} />
              <Route path="admin/services" element={<AdminServicesPage />} />
              <Route path="admin/therapists" element={<AdminTherapistsPage />} />
              <Route path="admin/availability" element={<AdminAvailabilityPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}