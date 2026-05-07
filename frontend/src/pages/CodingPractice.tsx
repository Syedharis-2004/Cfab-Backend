import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Play, Terminal, CheckCircle, XCircle, Loader2, Sparkles, Code2 } from "lucide-react";
import axios from "axios";
import Navbar from "../components/Navbar";

export default function CodingPracticePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [code, setCode] = useState("def solve():\n    # Write your solution here\n    pass");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "pending" | "success" | "error">("idle");
  const [result, setResult] = useState<any>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
  const token = localStorage.getItem("token");

  const submitCode = async () => {
    setLoading(true);
    setStatus("pending");
    setResult(null);

    try {
      const res = await axios.post(`${API_BASE}/coding-assignments/submit`, {
        assignment_id: id,
        code,
        language: "python"
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const submissionId = res.data.id;
      pollResult(submissionId);
    } catch (err) {
      setStatus("error");
      setLoading(false);
    }
  };

  const pollResult = (submissionId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/coding-assignments/submissions/${submissionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.data.status !== "pending" && res.data.status !== "running") {
          clearInterval(interval);
          setResult(res.data);
          setStatus(res.data.status === "accepted" ? "success" : "error");
          setLoading(false);
        }
      } catch (err) {
        clearInterval(interval);
        setStatus("error");
        setLoading(false);
      }
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-7xl mx-auto pt-28 pb-20 px-6">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-slate-500 hover:text-white mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-250px)]">
          {/* PROBLEM DESCRIPTION */}
          <div className="glass-card p-8 overflow-y-auto space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <Code2 className="w-5 h-5 text-blue-400" />
              </div>
              <h1 className="text-2xl font-bold text-white">Coding Assignment</h1>
            </div>

            <div className="prose prose-invert max-w-none">
              <h3 className="text-white">Problem Statement</h3>
              <p className="text-slate-400">
                Implement a function that returns the sum of all prime numbers up to a given integer N.
              </p>
              <h3 className="text-white mt-6">Example</h3>
              <div className="bg-slate-900 p-4 rounded-xl font-mono text-sm border border-white/5">
                Input: N = 10<br/>
                Output: 17 (2 + 3 + 5 + 7)
              </div>
              <h3 className="text-white mt-6">Constraints</h3>
              <ul className="text-slate-400 list-disc pl-5">
                <li>1 ≤ N ≤ 10^6</li>
                <li>Time Limit: 2.0s</li>
              </ul>
            </div>
          </div>

          {/* EDITOR & OUTPUT */}
          <div className="flex flex-col gap-6">
            <div className="glass-card flex-grow p-0 overflow-hidden flex flex-col border-white/10">
              <div className="flex items-center justify-between px-6 py-3 bg-white/5 border-b border-white/5">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500/50" />
                  <span className="w-3 h-3 rounded-full bg-yellow-500/50" />
                  <span className="w-3 h-3 rounded-full bg-green-500/50" />
                  <span className="ml-4 text-xs font-bold text-slate-500 uppercase tracking-widest">solution.py</span>
                </div>
                <select className="bg-transparent border-none text-xs font-bold text-blue-400 outline-none cursor-pointer">
                  <option value="python">Python 3.10</option>
                </select>
              </div>
              
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="flex-grow bg-[#0d1117] text-[#c9d1d9] p-6 font-mono text-sm resize-none focus:outline-none"
                spellCheck={false}
              />

              <div className="px-6 py-4 bg-white/5 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {status === "pending" && <span className="text-xs font-bold text-yellow-400 animate-pulse flex items-center gap-2"><Loader2 className="w-3 h-3 animate-spin" /> Running Tests...</span>}
                  {status === "success" && <span className="text-xs font-bold text-green-400 flex items-center gap-2"><CheckCircle className="w-3 h-3" /> Solution Accepted</span>}
                  {status === "error" && <span className="text-xs font-bold text-red-400 flex items-center gap-2"><XCircle className="w-3 h-3" /> Failed</span>}
                </div>
                <button 
                  onClick={submitCode}
                  disabled={loading}
                  className="btn-primary py-2 px-6 text-sm flex items-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Play className="w-4 h-4 fill-current" /> Run & Submit</>}
                </button>
              </div>
            </div>

            {/* RESULTS PANEL */}
            {result && (
              <div className={`glass-card p-6 animate-fadeIn ${result.status === "accepted" ? "border-green-500/20" : "border-red-500/20"}`}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-slate-500" /> Test Results
                  </h3>
                  <span className={`text-[10px] font-bold px-2 py-1 rounded uppercase tracking-widest ${
                    result.status === "accepted" ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                  }`}>
                    {result.status}
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <ResultMetric label="Score" value={`${result.score}/100`} />
                  <ResultMetric label="Passed" value={result.passed_cases} />
                  <ResultMetric label="Total Cases" value={result.total_cases} />
                </div>

                {result.error && (
                  <div className="mt-4 p-3 bg-red-500/5 border border-red-500/10 rounded-lg font-mono text-xs text-red-400 whitespace-pre-wrap">
                    {result.error}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function ResultMetric({ label, value }: any) {
  return (
    <div className="bg-slate-900/50 p-3 rounded-xl border border-white/5">
      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">{label}</p>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}
