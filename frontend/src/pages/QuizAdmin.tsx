import { useState } from "react";
import { Plus, Trash2, Upload, Send, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

interface Question {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
}

export default function QuizAdminPage() {
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState<Question[]>([
    {
      question: "",
      option_a: "",
      option_b: "",
      option_c: "",
      option_d: "",
      correct_answer: "A",
    },
  ]);

  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  // Change your backend URL here
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  const handleQuestionChange = (
    index: number,
    field: keyof Question,
    value: string
  ) => {
    const updated = [...questions];
    updated[index][field] = value;
    setQuestions(updated);
  };

  const addQuestion = () => {
    setQuestions([
      ...questions,
      {
        question: "",
        option_a: "",
        option_b: "",
        option_c: "",
        option_d: "",
        correct_answer: "A",
      },
    ]);
  };

  const removeQuestion = (index: number) => {
    const updated = questions.filter((_, i) => i !== index);
    setQuestions(updated);
  };

  // =========================
  // CREATE QUIZ MANUALLY
  // =========================
  const createQuiz = async () => {
    try {
      if (!title) return alert("Please enter a title");
      setLoading(true);

      const token = localStorage.getItem("token");

      const response = await fetch(`${API_BASE}/admin/quiz`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          questions,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to create quiz");
      }

      alert("Quiz created successfully!");

      setTitle("");
      setQuestions([
        {
          question: "",
          option_a: "",
          option_b: "",
          option_c: "",
          option_d: "",
          correct_answer: "A",
        },
      ]);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // PDF UPLOAD
  // =========================
  const uploadPDF = async () => {
    try {
      if (!pdfFile) {
        return alert("Please select a PDF file");
      }
      if (!title) return alert("Please enter a title for the PDF upload");

      setLoading(true);

      const token = localStorage.getItem("token");

      const formData = new FormData();
      formData.append("title", title);
      formData.append("file", pdfFile);

      const response = await fetch(
        `${API_BASE}/admin/quiz/upload`, // Backend has both /upload and /upload-pdf
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "PDF upload failed");
      }

      alert("Quiz uploaded successfully!");

      setTitle("");
      setPdfFile(null);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        <Link to="/admin" className="inline-flex items-center text-slate-400 hover:text-white mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Admin Dashboard
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
              Quiz Admin Panel
            </h1>
            <p className="text-slate-400 mt-1">Create interactive MCQ quizzes manually or via PDF.</p>
          </div>
        </div>

        {/* QUIZ TITLE */}
        <div className="glass-card p-6 mb-8">
          <label className="block text-sm font-semibold text-slate-300 mb-2 uppercase tracking-wider">
            Quiz Title
          </label>
          <input
            type="text"
            placeholder="e.g., Advanced Python Concepts"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input-field text-lg font-medium"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* MANUAL QUESTIONS */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-semibold flex items-center">
              <Send className="w-5 h-5 mr-2 text-blue-400" />
              Manual Questions
            </h2>
            
            {questions.map((q, index) => (
              <div
                key={index}
                className="glass-card p-6 relative group"
              >
                <div className="flex justify-between items-center mb-6">
                  <span className="bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border border-blue-500/20">
                    Question {index + 1}
                  </span>

                  {questions.length > 1 && (
                    <button
                      onClick={() => removeQuestion(index)}
                      className="text-slate-500 hover:text-red-400 p-2 rounded-lg hover:bg-red-400/10 transition-all"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>

                <textarea
                  placeholder="What is the output of '2' + 2 in JavaScript?"
                  value={q.question}
                  onChange={(e) =>
                    handleQuestionChange(
                      index,
                      "question",
                      e.target.value
                    )
                  }
                  className="input-field mb-4 min-h-[100px]"
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(['a', 'b', 'c', 'd'] as const).map((opt) => (
                    <div key={opt} className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-bold uppercase text-xs">
                        {opt}
                      </span>
                      <input
                        type="text"
                        placeholder={`Option ${opt.toUpperCase()}`}
                        value={q[`option_${opt}` as keyof Question]}
                        onChange={(e) =>
                          handleQuestionChange(
                            index,
                            `option_${opt}` as keyof Question,
                            e.target.value
                          )
                        }
                        className="input-field pl-8"
                      />
                    </div>
                  ))}
                </div>

                <div className="mt-6 flex items-center gap-4">
                  <label className="text-sm font-semibold text-slate-400">
                    Correct Answer:
                  </label>
                  <div className="flex gap-2">
                    {['A', 'B', 'C', 'D'].map((label) => (
                      <button
                        key={label}
                        onClick={() => handleQuestionChange(index, "correct_answer", label)}
                        className={`w-10 h-10 rounded-lg font-bold transition-all ${
                          q.correct_answer === label 
                          ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30' 
                          : 'bg-slate-800 text-slate-500 hover:bg-slate-700'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            <button
              onClick={addQuestion}
              className="w-full py-4 border-2 border-dashed border-slate-800 rounded-2xl text-slate-500 hover:text-blue-400 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all flex items-center justify-center font-semibold"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Another Question
            </button>

            <button
              onClick={createQuiz}
              disabled={loading}
              className="btn-primary w-full py-4 text-lg"
            >
              {loading ? "Creating..." : "Publish Quiz"}
            </button>
          </div>

          {/* PDF UPLOAD SIDEBAR */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold flex items-center">
              <Upload className="w-5 h-5 mr-2 text-violet-400" />
              Smart PDF Import
            </h2>
            
            <div className="glass-card p-6">
              <p className="text-sm text-slate-400 mb-6">
                Upload a PDF with MCQs. Our AI will automatically extract questions, options, and correct answers.
              </p>

              <div 
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
                  pdfFile ? 'border-violet-500 bg-violet-500/5' : 'border-slate-800 hover:border-slate-700'
                }`}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (e.dataTransfer.files?.[0]) setPdfFile(e.dataTransfer.files[0]);
                }}
                onClick={() => document.getElementById('pdf-input')?.click()}
              >
                <input
                  id="pdf-input"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <div className="w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Upload className={`w-8 h-8 ${pdfFile ? 'text-violet-400' : 'text-slate-600'}`} />
                </div>
                {pdfFile ? (
                  <p className="text-violet-400 font-medium truncate px-2">{pdfFile.name}</p>
                ) : (
                  <>
                    <p className="text-slate-300 font-medium">Click to upload PDF</p>
                    <p className="text-slate-500 text-xs mt-1">or drag and drop</p>
                  </>
                )}
              </div>

              <button
                onClick={uploadPDF}
                disabled={loading || !pdfFile}
                className={`w-full mt-6 py-3 rounded-xl font-semibold transition-all ${
                  loading || !pdfFile 
                  ? 'bg-slate-800 text-slate-600 cursor-not-allowed' 
                  : 'bg-violet-600 text-white hover:bg-violet-500 shadow-lg shadow-violet-600/20'
                }`}
              >
                {loading ? "Processing..." : "Extract from PDF"}
              </button>
            </div>

            <div className="glass-card p-4 bg-blue-500/5 border-blue-500/10">
              <h3 className="text-blue-400 text-sm font-bold uppercase tracking-widest mb-2">Pro Tip</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ensure your PDF follows the standard format:<br/>
                <span className="text-slate-300">1. Question?<br/>A) Opt 1<br/>B) Opt 2<br/>Answer: A</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
