import { useState } from "react";
import { UserPlus, Mail, Lock, User, Shield, Loader2, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await axios.post(`${API_BASE}/auth/register`, {
        email,
        name,
        password,
        role,
      });

      alert("Registration successful! You can now log in.");
      navigate("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950">
      <div className="w-full max-w-lg">
        <button 
          onClick={() => navigate("/login")}
          className="flex items-center gap-2 text-slate-500 hover:text-white mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Login
        </button>

        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Join the Platform
          </h1>
          <p className="text-slate-400 mt-2">Start your learning or teaching journey today</p>
        </div>

        <div className="glass-card p-8">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  <User className="w-3 h-3" /> Full Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="input-field"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                  <Mail className="w-3 h-3" /> Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="input-field"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Lock className="w-3 h-3" /> Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                className="input-field"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Shield className="w-3 h-3" /> Choose Your Role
              </label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setRole("student")}
                  className={`py-3 rounded-xl border transition-all font-medium ${
                    role === "student"
                      ? "bg-blue-600/20 border-blue-500 text-blue-400 shadow-lg shadow-blue-500/10"
                      : "bg-slate-900 border-white/5 text-slate-500 hover:border-white/10"
                  }`}
                >
                  Student
                </button>
                <button
                  type="button"
                  onClick={() => setRole("admin")}
                  className={`py-3 rounded-xl border transition-all font-medium ${
                    role === "admin"
                      ? "bg-violet-600/20 border-violet-500 text-violet-400 shadow-lg shadow-violet-500/10"
                      : "bg-slate-900 border-white/5 text-slate-500 hover:border-white/10"
                  }`}
                >
                  Administrator
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-4 mt-4 flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Create Free Account <UserPlus className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
