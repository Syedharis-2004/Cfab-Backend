import { Shield, BookPlus, ClipboardList, Users, ArrowRight, Settings, Plus, Upload } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function AdminDashboardPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-7xl mx-auto pt-28 pb-20 px-6">
        <header className="mb-12">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-violet-500/10 rounded-lg border border-violet-500/20">
              <Shield className="w-5 h-5 text-violet-400" />
            </div>
            <span className="text-sm font-bold text-violet-400 uppercase tracking-widest">Admin Control Center</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Platform Management</h1>
          <p className="text-slate-400">Create courses, manage quizzes, and track student performance.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AdminCard 
            to="/admin/quiz"
            icon={<ClipboardList className="w-8 h-8 text-blue-400" />}
            title="Quiz Management"
            desc="Create manual quizzes or upload PDF files for automatic MCQ extraction."
            color="blue"
          />
          <AdminCard 
            to="/admin/courses"
            icon={<BookPlus className="w-8 h-8 text-violet-400" />}
            title="Course Builder"
            desc="Design new curriculum, upload lectures, and organize modules."
            color="violet"
          />
          <AdminCard 
            to="/admin/users"
            icon={<Users className="w-8 h-8 text-emerald-400" />}
            title="User Directory"
            desc="Monitor student enrollment, progress, and account permissions."
            color="emerald"
          />
        </div>

        <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="glass-card p-8">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-400" /> Quick Actions
            </h3>
            <div className="space-y-4">
              <QuickAction icon={<BookPlus className="w-4 h-4" />} label="Create New Course" />
              <QuickAction icon={<Upload className="w-4 h-4" />} label="Upload PDF Assignment" />
              <QuickAction icon={<Settings className="w-4 h-4" />} label="System Configuration" />
            </div>
          </div>

          <div className="glass-card p-8 border-violet-500/10">
            <h3 className="text-xl font-bold text-white mb-6">Recent Activity</h3>
            <div className="space-y-6">
              <ActivityItem user="Haris" action="Created a new quiz: 'Python Advanced'" time="2 mins ago" />
              <ActivityItem user="Admin" action="Uploaded 3 new lectures to 'React Mastery'" time="1 hour ago" />
              <ActivityItem user="System" action="Automated PDF parsing completed for 'ML Quiz'" time="5 hours ago" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function AdminCard({ to, icon, title, desc, color }: any) {
  const colors: any = {
    blue: "hover:border-blue-500/50 group-hover:bg-blue-500/10",
    violet: "hover:border-violet-500/50 group-hover:bg-violet-500/10",
    emerald: "hover:border-emerald-500/50 group-hover:bg-emerald-500/10",
  };
  return (
    <Link to={to} className={`glass-card p-8 group transition-all ${colors[color]}`}>
      <div className="mb-6 p-4 rounded-2xl bg-white/5 border border-white/5 w-fit group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed mb-6">{desc}</p>
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 group-hover:text-white transition-colors">
        Open Panel <ArrowRight className="w-4 h-4" />
      </div>
    </Link>
  );
}

function QuickAction({ icon, label }: any) {
  return (
    <button className="w-full p-4 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between hover:bg-white/10 hover:border-white/10 transition-all text-slate-300">
      <div className="flex items-center gap-3">
        {icon}
        <span className="font-semibold text-sm">{label}</span>
      </div>
      <Plus className="w-4 h-4 text-slate-500" />
    </button>
  );
}

function ActivityItem({ user, action, time }: any) {
  return (
    <div className="flex items-start gap-4">
      <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/5 flex items-center justify-center text-[10px] font-bold text-slate-400 uppercase">
        {user[0]}
      </div>
      <div>
        <p className="text-sm text-slate-300"><span className="font-bold text-white">{user}</span> {action}</p>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1 flex items-center gap-1">
          <ClockIcon className="w-3 h-3" /> {time}
        </p>
      </div>
    </div>
  );
}

function ClockIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
  );
}
