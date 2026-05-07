import { useState, useEffect } from "react";
import { BookOpen, GraduationCap, Clock, ChevronRight, Search, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import axios from "axios";
import Navbar from "../components/Navbar";

export default function CourseListPage() {
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const res = await axios.get(`${API_BASE}/course/all`);
        setCourses(res.data);
      } catch (err) {
        console.error("Failed to fetch courses");
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, []);

  const filteredCourses = courses.filter(c => 
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-7xl mx-auto pt-28 pb-20 px-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-12 gap-6">
          <header>
            <h1 className="text-4xl font-bold text-white mb-2">Available Courses</h1>
            <p className="text-slate-400">Explore our curriculum and start learning today.</p>
          </header>

          <div className="relative w-full md:w-80">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-12"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredCourses.length > 0 ? filteredCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            )) : (
              <div className="col-span-full py-20 text-center glass-card border-dashed border-white/5">
                <p className="text-slate-500">No courses found matching your search.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function CourseCard({ course }: any) {
  return (
    <Link to={`/courses/${course.id}`} className="glass-card p-0 overflow-hidden group">
      <div className="h-48 bg-gradient-to-br from-blue-600/20 to-violet-600/20 flex items-center justify-center border-b border-white/5 relative">
        <GraduationCap className="w-16 h-16 text-blue-500/40 group-hover:scale-110 transition-transform" />
        <div className="absolute top-4 right-4 bg-slate-900/80 backdrop-blur px-3 py-1 rounded-full text-[10px] font-bold text-blue-400 border border-blue-500/20 uppercase tracking-widest">
          Public
        </div>
      </div>
      <div className="p-6">
        <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{course.title}</h3>
        <p className="text-slate-400 text-sm line-clamp-2 mb-6">{course.description || "No description available for this course yet."}</p>
        
        <div className="flex items-center justify-between mt-auto">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-widest">
              <BookOpen className="w-3.5 h-3.5" /> 12 Lectures
            </div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-widest border-l border-white/10 pl-3">
              <Clock className="w-3.5 h-3.5" /> 4h 30m
            </div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-all">
            <ChevronRight className="w-5 h-5" />
          </div>
        </div>
      </div>
    </Link>
  );
}
