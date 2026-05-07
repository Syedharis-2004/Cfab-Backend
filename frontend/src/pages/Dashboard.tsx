import { useState, useEffect } from "react";
import { LayoutDashboard, ClipboardCheck, FileCode, Clock, ChevronRight, Loader2, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";

interface DashboardData {
  assignments: any[];
  quizzes: any[];
  user_info?: any;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get(`${API_BASE}/check-yourself`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setData(res.data);
      } catch (err: any) {
        setError("Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-7xl mx-auto pt-28 pb-20 px-6">
        <header className="mb-12">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <Sparkles className="w-5 h-5 text-blue-400" />
            </div>
            <span className="text-sm font-bold text-blue-400 uppercase tracking-widest">Student Portal</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Your Progress Overview</h1>
          <p className="text-slate-400">Track your assignments, quizzes and upcoming study milestones.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* STATS MINI CARDS (MOCKED) */}
          <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-6">
            <StatCard icon={<ClipboardCheck className="text-green-400" />} label="Completed Quizzes" value="12" color="green" />
            <StatCard icon={<FileCode className="text-blue-400" />} label="Code Submissions" value="45" color="blue" />
            <StatCard icon={<Clock className="text-orange-400" />} label="Study Hours" value="28.5" color="orange" />
          </div>

          {/* MAIN SECTIONS */}
          <div className="lg:col-span-2 space-y-8">
            <Section 
              title="Recent Assignments" 
              count={data?.assignments?.length || 0}
              icon={<FileCode className="w-5 h-5 text-blue-400" />}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data?.assignments?.length ? data.assignments.map((item, idx) => (
                  <AssignmentCard key={idx} item={item} />
                )) : (
                  <EmptyState message="No pending assignments" />
                )}
              </div>
            </Section>

            <Section 
              title="Available Quizzes" 
              count={data?.quizzes?.length || 0}
              icon={<ClipboardCheck className="w-5 h-5 text-violet-400" />}
            >
              <div className="space-y-3">
                {data?.quizzes?.length ? data.quizzes.map((item, idx) => (
                  <QuizRow key={idx} item={item} />
                )) : (
                  <EmptyState message="All caught up! No quizzes found." />
                )}
              </div>
            </Section>
          </div>

          {/* SIDEBAR */}
          <div className="space-y-8">
            <div className="glass-card p-6 bg-gradient-to-br from-blue-600/10 to-violet-600/10">
              <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-yellow-400" /> Daily Tip
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed italic">
                "Consistent practice is the key to mastering any programming language. Try to solve at least one problem every day."
              </p>
            </div>

            <div className="glass-card p-6 border-blue-500/10">
              <h3 className="font-bold text-white mb-4">Study Plan Progress</h3>
              <div className="space-y-4">
                <ProgressItem label="Python Basics" progress={85} color="blue" />
                <ProgressItem label="Data Structures" progress={40} color="violet" />
                <ProgressItem label="FastAPI Backend" progress={15} color="orange" />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function Section({ title, count, icon, children }: any) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          {icon}
          {title}
          <span className="ml-2 text-xs bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-slate-500">
            {count}
          </span>
        </h2>
        <button className="text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors">View All</button>
      </div>
      {children}
    </div>
  );
}

function StatCard({ icon, label, value, color }: any) {
  const colorMap: any = {
    green: "from-green-500/10 to-emerald-500/5 border-green-500/10",
    blue: "from-blue-500/10 to-indigo-500/5 border-blue-500/10",
    orange: "from-orange-500/10 to-amber-500/5 border-orange-500/10",
  };
  return (
    <div className={`glass-card p-6 bg-gradient-to-br ${colorMap[color]}`}>
      <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center mb-4">
        {icon}
      </div>
      <p className="text-sm font-medium text-slate-400">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}

function AssignmentCard({ item }: any) {
  return (
    <Link to={`/assignments/${item.id}`} className="glass-card p-5 group">
      <div className="flex items-start justify-between">
        <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
          <FileCode className="w-6 h-6" />
        </div>
        <span className="px-2 py-1 bg-white/5 border border-white/5 rounded-lg text-[10px] font-bold text-slate-500 uppercase">
          Coding
        </span>
      </div>
      <h4 className="font-bold text-white mt-4 line-clamp-1">{item.title || "Assignment Title"}</h4>
      <p className="text-xs text-slate-500 mt-1 line-clamp-2">{item.description || "Learn core concepts with this hands-on assignment."}</p>
      <div className="mt-5 flex items-center justify-between text-blue-400 font-bold text-xs uppercase tracking-wider group-hover:gap-2 transition-all">
        Start Assignment <ChevronRight className="w-3 h-3" />
      </div>
    </Link>
  );
}

function QuizRow({ item }: any) {
  return (
    <Link to={`/quiz/${item.id}`} className="glass-card p-4 flex items-center justify-between hover:bg-white/5 group">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
          <ClipboardCheck className="w-5 h-5" />
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">{item.title}</h4>
          <p className="text-[10px] text-slate-500 mt-0.5 uppercase tracking-widest font-semibold">15 Questions • 20 Mins</p>
        </div>
      </div>
      <div className="w-8 h-8 rounded-full border border-white/5 flex items-center justify-center text-slate-500 group-hover:border-violet-500/50 group-hover:text-violet-400 transition-all">
        <ChevronRight className="w-4 h-4" />
      </div>
    </Link>
  );
}

function ProgressItem({ label, progress, color }: any) {
  const colors: any = {
    blue: "bg-blue-500 shadow-blue-500/20",
    violet: "bg-violet-500 shadow-violet-500/20",
    orange: "bg-orange-500 shadow-orange-500/20",
  };
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs font-semibold">
        <span className="text-slate-400">{label}</span>
        <span className="text-white">{progress}%</span>
      </div>
      <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden border border-white/5">
        <div 
          className={`h-full rounded-full ${colors[color]} shadow-lg transition-all duration-1000`} 
          style={{ width: `${progress}%` }} 
        />
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="py-10 text-center border-2 border-dashed border-white/5 rounded-2xl">
      <p className="text-slate-500 text-sm italic">{message}</p>
    </div>
  );
}
