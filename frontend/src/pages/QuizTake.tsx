import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, CheckCircle2, ChevronRight, ChevronLeft, Loader2, Trophy, Clock } from "lucide-react";
import axios from "axios";
import Navbar from "../components/Navbar";

export default function QuizTakePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const res = await axios.get(`${API_BASE}/quiz/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setQuiz(res.data);
      } catch (err) {
        console.error("Failed to fetch quiz");
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [id, token]);

  const selectAnswer = (questionId: string, option: string) => {
    setAnswers({ ...answers, [questionId]: option });
  };

  const submitQuiz = async () => {
    setSubmitting(true);
    try {
      const payload = {
        answers: Object.entries(answers).map(([qId, opt]) => ({
          question_id: qId,
          selected_answer: opt
        }))
      };
      const res = await axios.post(`${API_BASE}/quiz/${id}/submit`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setResult(res.data);
    } catch (err) {
      alert("Failed to submit quiz.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center"><Loader2 className="animate-spin text-blue-500" /></div>;

  if (result) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-200">
        <Navbar />
        <main className="max-w-3xl mx-auto pt-32 pb-20 px-6 text-center">
          <div className="glass-card p-12 border-violet-500/20 bg-gradient-to-br from-blue-600/5 to-violet-600/5">
            <div className="w-24 h-24 bg-violet-500/20 rounded-3xl flex items-center justify-center mx-auto mb-8 border border-violet-500/20 shadow-2xl shadow-violet-500/20">
              <Trophy className="w-12 h-12 text-violet-400" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Quiz Completed!</h1>
            <p className="text-slate-400 mb-8">You've successfully finished the assessment.</p>
            
            <div className="grid grid-cols-2 gap-4 max-w-sm mx-auto mb-10">
              <div className="bg-slate-900 p-6 rounded-2xl border border-white/5">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Your Score</p>
                <p className="text-3xl font-bold text-blue-400">{result.score}</p>
              </div>
              <div className="bg-slate-900 p-6 rounded-2xl border border-white/5">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Total Points</p>
                <p className="text-3xl font-bold text-white">{result.total}</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => navigate("/dashboard")}
                className="btn-primary py-3 px-8"
              >
                Go to Dashboard
              </button>
              <button 
                onClick={() => window.location.reload()}
                className="btn-outline py-3 px-8"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const currentQuestion = quiz?.questions?.[currentIdx];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <Navbar />
      
      <main className="max-w-4xl mx-auto pt-28 pb-20 px-6">
        <div className="flex items-center justify-between mb-8">
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Quit Quiz
          </button>
          <div className="flex items-center gap-4 px-4 py-2 bg-white/5 border border-white/10 rounded-xl">
            <Clock className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-bold text-white tabular-nums">14:52</span>
          </div>
        </div>

        <div className="space-y-8">
          <div className="flex items-center gap-4">
            <div className="h-2 flex-grow bg-slate-900 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-violet-500 transition-all duration-500"
                style={{ width: `${((currentIdx + 1) / quiz.questions.length) * 100}%` }}
              />
            </div>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
              Question {currentIdx + 1} of {quiz.questions.length}
            </span>
          </div>

          <div className="glass-card p-10">
            <h2 className="text-2xl font-bold text-white mb-10 leading-relaxed">
              {currentQuestion?.question}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {['a', 'b', 'c', 'd'].map((opt) => {
                const label = opt.toUpperCase();
                const optionText = currentQuestion[`option_${opt}`];
                if (!optionText) return null;
                
                const isSelected = answers[currentQuestion.id] === label;

                return (
                  <button
                    key={opt}
                    onClick={() => selectAnswer(currentQuestion.id, label)}
                    className={`flex items-center gap-4 p-5 rounded-2xl border transition-all text-left ${
                      isSelected 
                      ? 'bg-blue-600/10 border-blue-500 text-white shadow-lg shadow-blue-500/10' 
                      : 'bg-slate-900 border-white/5 text-slate-400 hover:border-white/20'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs border ${
                      isSelected ? 'bg-blue-500 border-blue-400 text-white' : 'bg-slate-800 border-white/5 text-slate-500'
                    }`}>
                      {label}
                    </div>
                    <span className="font-medium">{optionText}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={() => setCurrentIdx(Math.max(0, currentIdx - 1))}
              disabled={currentIdx === 0}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${
                currentIdx === 0 ? 'text-slate-700 cursor-not-allowed' : 'text-slate-400 hover:text-white'
              }`}
            >
              <ChevronLeft className="w-5 h-5" /> Previous
            </button>

            {currentIdx === quiz.questions.length - 1 ? (
              <button
                onClick={submitQuiz}
                disabled={submitting || !answers[currentQuestion.id]}
                className="btn-primary px-10 py-3 flex items-center gap-2"
              >
                {submitting ? <Loader2 className="animate-spin w-5 h-5" /> : <>Finish & Submit <CheckCircle2 className="w-5 h-5" /></>}
              </button>
            ) : (
              <button
                onClick={() => setCurrentIdx(Math.min(quiz.questions.length - 1, currentIdx + 1))}
                disabled={!answers[currentQuestion.id]}
                className={`flex items-center gap-2 px-8 py-3 rounded-xl font-bold transition-all ${
                  !answers[currentQuestion.id] 
                  ? 'bg-slate-800 text-slate-600 cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-500'
                }`}
              >
                Next Question <ChevronRight className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
