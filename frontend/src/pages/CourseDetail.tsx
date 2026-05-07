import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, BookOpen, Clock, PlayCircle, CheckCircle2, Calendar, Sparkles, Loader2 } from "lucide-react";
import axios from "axios";
import Navbar from "../components/Navbar";

export default function CourseDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState<any>(null);
  const [studyPlan, setStudyPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [availability, setAvailability] = useState({
    mon: 60, tue: 60, wed: 60, thu: 60, fri: 60, sat: 120, sun: 120
  });

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const cRes = await axios.get(`${API_BASE}/course/all`);
        const found = cRes.data.find((c: any) => c.id === id);
        setCourse(found);

        if (token) {
          try {
            const pRes = await axios.get(`${API_BASE}/study-plan/${id}`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            setStudyPlan(pRes.data);
          } catch (e) {
            // Plan might not exist yet
          }
        }
      } catch (err) {
        console.error("Error fetching details");
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id, token]);

  const handleStartCourse = async () => {
    setEnrolling(true);
    try {
      await axios.post(`${API_BASE}/course/start`, {
        course_id: id,
        daily_minutes: 60,
        availability: availability
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const pRes = await axios.get(`${API_BASE}/study-plan/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudyPlan(pRes.data);
    } catch (err) {
      alert("Failed to start course. Ensure you are logged in.");
    } finally {
      setEnrolling(false);
    }
  };

  const markComplete = async (lectureId: string) => {
    try {
      await axios.post(`${API_BASE}/lecture/complete`, {
        lecture_id: lectureId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Refresh plan
      const pRes = await axios.get(`${API_BASE}/study-plan/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudyPlan(pRes.data);
    } catch (e) {
      console.error("Failed to mark complete");
    }
  };

  if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center"><Loader2 className="animate-spin text-blue-500" /></div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-7xl mx-auto pt-28 pb-20 px-6">
        <button onClick={() => navigate("/courses")} className="flex items-center gap-2 text-slate-500 hover:text-white mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Courses
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* COURSE HERO */}
          <div className="lg:col-span-2 space-y-8">
            <div className="glass-card p-10 bg-gradient-to-br from-blue-600/10 to-violet-600/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-10">
                <BookOpen className="w-40 h-40" />
              </div>
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6">
                  <span className="bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-blue-500/20">Computer Science</span>
                </div>
                <h1 className="text-5xl font-bold text-white mb-4 leading-tight">{course?.title}</h1>
                <p className="text-slate-400 text-lg leading-relaxed max-w-2xl">{course?.description || "Master the core principles and advanced techniques of this subject with our structured curriculum."}</p>
                
                <div className="flex flex-wrap items-center gap-8 mt-10">
                  <DetailItem icon={<Clock className="w-5 h-5 text-blue-400" />} label="Duration" value="12 Hours Total" />
                  <DetailItem icon={<BookOpen className="w-5 h-5 text-violet-400" />} label="Modules" value="8 Structured Days" />
                  <DetailItem icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />} label="Level" value="Beginner to Pro" />
                </div>
              </div>
            </div>

            {studyPlan ? (
              <div className="space-y-8">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                    <Calendar className="w-6 h-6 text-violet-400" /> Personalized Study Plan
                  </h2>
                  <div className="flex items-center gap-4">
                    <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">Progress</span>
                    <span className="text-lg font-bold text-white">40%</span>
                  </div>
                </div>

                <div className="space-y-4">
                  {studyPlan.days?.map((day: any) => (
                    <DayCard key={day.day_number} day={day} onComplete={markComplete} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="glass-card p-10 text-center border-dashed border-white/10">
                <Sparkles className="w-12 h-12 text-yellow-500/40 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-white mb-2">Ready to Start Learning?</h3>
                <p className="text-slate-400 mb-8 max-w-md mx-auto">Generate a personalized study plan based on your weekly availability to track your progress.</p>
                
                <div className="bg-slate-900/50 p-6 rounded-2xl border border-white/5 max-w-xl mx-auto mb-8">
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Set Weekly Availability (Minutes/Day)</p>
                  <div className="grid grid-cols-4 md:grid-cols-7 gap-3">
                    {Object.keys(availability).map((day) => (
                      <div key={day} className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-600 uppercase">{day}</label>
                        <input 
                          type="number" 
                          value={availability[day as keyof typeof availability]} 
                          onChange={(e) => setAvailability({...availability, [day]: parseInt(e.target.value) || 0})}
                          className="w-full bg-slate-950 border border-white/5 rounded-lg py-2 px-1 text-center text-sm focus:border-blue-500 outline-none"
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <button 
                  onClick={handleStartCourse}
                  disabled={enrolling}
                  className="btn-primary px-10 py-4 text-lg flex items-center gap-2 mx-auto"
                >
                  {enrolling ? <Loader2 className="animate-spin w-5 h-5" /> : <>Generate My Plan <ArrowRightIcon className="w-5 h-5" /></>}
                </button>
              </div>
            )}
          </div>

          {/* SIDEBAR */}
          <div className="space-y-8">
            <div className="glass-card p-8">
              <h3 className="font-bold text-white mb-6 uppercase tracking-widest text-xs">Course Content</h3>
              <div className="space-y-6">
                <SidebarModule title="Getting Started" duration="45m" status="completed" />
                <SidebarModule title="Core Fundamentals" duration="1h 20m" status="current" />
                <SidebarModule title="Advanced Techniques" duration="2h 10m" status="locked" />
                <SidebarModule title="Final Project" duration="3h 00m" status="locked" />
              </div>
            </div>

            <div className="glass-card p-6 bg-blue-500/5 border-blue-500/10">
              <h4 className="text-sm font-bold text-blue-400 mb-2">Certificate Included</h4>
              <p className="text-xs text-slate-400 leading-relaxed">Complete all modules and pass the final quiz to earn a certified credential.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function DetailItem({ icon, label, value }: any) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center">
        {icon}
      </div>
      <div>
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{label}</p>
        <p className="text-sm font-bold text-white mt-0.5">{value}</p>
      </div>
    </div>
  );
}

function DayCard({ day, onComplete }: any) {
  return (
    <div className="glass-card p-6 border-l-4 border-l-blue-500">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white">Day {day.day_number}</h3>
        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{day.lectures?.length || 0} Lectures</span>
      </div>
      <div className="space-y-3">
        {day.lectures?.map((lecture: any) => (
          <div key={lecture.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-white/5 hover:border-white/10 transition-all">
            <div className="flex items-center gap-3">
              <PlayCircle className="w-5 h-5 text-slate-600" />
              <span className="text-sm font-medium text-slate-300">{lecture.title}</span>
            </div>
            <button 
              onClick={() => onComplete(lecture.id)}
              className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${
                lecture.is_completed ? 'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30' : 'bg-slate-800 text-slate-600 border border-white/5 hover:border-blue-500 hover:text-blue-400'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function SidebarModule({ title, duration, status }: any) {
  const statusColors: any = {
    completed: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
    current: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    locked: "text-slate-600 bg-slate-900/50 border-white/5",
  };
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${status === 'completed' ? 'bg-emerald-500' : status === 'current' ? 'bg-blue-500 animate-pulse' : 'bg-slate-800'}`} />
        <span className={`text-sm font-medium ${status === 'locked' ? 'text-slate-600' : 'text-slate-300'}`}>{title}</span>
      </div>
      <span className="text-[10px] font-bold text-slate-600 uppercase">{duration}</span>
    </div>
  );
}

function ArrowRightIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
  );
}
