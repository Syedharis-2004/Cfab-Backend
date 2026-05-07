import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import DashboardPage from "./pages/Dashboard";
import QuizAdminPage from "./pages/QuizAdmin";
import AdminDashboardPage from "./pages/AdminDashboard";
import CourseListPage from "./pages/CourseList";
import CourseDetailPage from "./pages/CourseDetail";
import QuizTakePage from "./pages/QuizTake";
import CodingPracticePage from "./pages/CodingPractice";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/courses" element={<CourseListPage />} />
        <Route path="/courses/:id" element={<CourseDetailPage />} />
        <Route path="/quiz/:id" element={<QuizTakePage />} />
        <Route path="/assignments/:id" element={<CodingPracticePage />} />
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="/admin/quiz" element={<QuizAdminPage />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
