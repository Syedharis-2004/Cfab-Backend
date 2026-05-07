import { useState } from "react";
import { LogIn, UserPlus, Mail, Lock, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await axios.post(`${API_BASE}/auth/login`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const { access_token } = response.data;
      localStorage.setItem("token", access_token);
      
      // Basic role detection or fetch user profile
      // For now, let's just go to dashboard
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-blue-600/20 rounded-3xl flex items-center justify-center mx-auto mb-4 border border-blue-500/20 shadow-2xl shadow-blue-500/10">
            <LogIn className="w-10 h-10 text-blue-500" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Welcome Back
          </h1>
          <p className="text-slate-400 mt-2">Log in to your account to continue</p>
        </div>

        <div className="glass-card p-8">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm mb-6 flex items-start gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5" />
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
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

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Lock className="w-3 h-3" /> Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3.5 flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Sign In <LogIn className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-white/5 text-center">
            <p className="text-slate-500 text-sm">
              Don't have an account?{" "}
              <button 
                onClick={() => navigate("/register")}
                className="text-blue-400 font-semibold hover:text-blue-300 transition-colors"
              >
                Create Account
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
