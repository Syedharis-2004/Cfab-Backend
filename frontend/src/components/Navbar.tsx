import { LayoutDashboard, BookOpen, Shield, LogOut, User } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (!token) return null;

  return (
    <nav className="fixed top-0 left-0 right-0 h-20 bg-slate-950/80 backdrop-blur-xl border-b border-white/5 z-50 px-6">
      <div className="max-w-7xl mx-auto h-full flex items-center justify-between">
        <div className="flex items-center gap-10">
          <Link to="/dashboard" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
            Check Yourself
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <NavLink to="/dashboard" icon={<LayoutDashboard className="w-4 h-4" />} label="Dashboard" active={location.pathname === "/dashboard"} />
            <NavLink to="/courses" icon={<BookOpen className="w-4 h-4" />} label="Courses" active={location.pathname === "/courses"} />
            <NavLink to="/admin" icon={<Shield className="w-4 h-4" />} label="Admin" active={location.pathname.startsWith("/admin")} />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium text-slate-300">Haris</span>
          </div>
          <button 
            onClick={logout}
            className="p-2.5 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, icon, label, active }: { to: string; icon: React.ReactNode; label: string; active: boolean }) {
  return (
    <Link 
      to={to} 
      className={`flex items-center gap-2 text-sm font-semibold transition-all ${
        active ? "text-blue-400" : "text-slate-500 hover:text-slate-300"
      }`}
    >
      {icon}
      {label}
    </Link>
  );
}
