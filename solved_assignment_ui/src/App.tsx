import React, { useState } from 'react';
import { 
  Terminal, 
  BarChart3, 
  ChevronLeft, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  Download,
  AlertCircle,
  FileCode,
  FileText,
  Layout,
  FileJson
} from 'lucide-react';
import { FileUpload } from './components/FileUpload';
import { ProcessingOverlay } from './components/ProcessingOverlay';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000'; // Update this to your actual backend port

type Mode = 'selection' | 'python' | 'powerbi' | 'result';

interface DownloadUrls {
  notebook?: string;
  summary?: string;
  powerbi_response?: string;
}

interface ProcessingResult {
  success: boolean;
  notebook_file?: string;
  summary_file?: string;
  powerbi_response_file?: string;
  questions_processed?: number;
  visuals_generated?: number;
  download_urls?: DownloadUrls;
}

function App() {
  const [mode, setMode] = useState<Mode>('selection');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [templateFile, setTemplateFile] = useState<File | null>(null);

  const handleDownload = (relativeUrl: string | undefined) => {
    if (!relativeUrl) return;
    
    // Ensure we have an absolute URL
    const absoluteUrl = relativeUrl.startsWith('http') 
      ? relativeUrl 
      : `${BACKEND_URL}${relativeUrl.startsWith('/') ? '' : '/'}${relativeUrl}`;
    
    console.log(`Initiating download for: ${absoluteUrl}`);
    
    // Create a temporary anchor element
    const link = document.createElement('a');
    link.href = absoluteUrl;
    // The 'download' attribute helps hint to the browser to download rather than navigate
    link.setAttribute('download', ''); 
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const simulateProcessing = async (targetMode: 'python' | 'powerbi') => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);

    const steps = [
      { name: 'Uploading files and templates...', progress: 20 },
      { name: 'Extracting questions from PDF...', progress: 40 },
      { name: 'Analyzing dataset and template structure...', progress: 65 },
      { name: 'AI Reasoning & Template Filling...', progress: 85 },
      { name: 'Finalizing downloadable files...', progress: 100 },
    ];

    for (const step of steps) {
      setProcessingStep(step.name);
      await new Promise(r => setTimeout(r, 1200));
      setProgress(step.progress);
    }

    if (targetMode === 'python') {
      setResult({
        success: true,
        questions_processed: 10,
        notebook_file: 'filled_assignment.ipynb',
        summary_file: 'summary.txt',
        download_urls: {
          notebook: `/api/solved-assignment/download/filled_assignment.ipynb?uid=user_1&aid=assign_1`,
          summary: `/api/solved-assignment/download/summary.txt?uid=user_1&aid=assign_1`
        }
      });
    } else {
      setResult({
        success: true,
        visuals_generated: 8,
        powerbi_response_file: 'filled_powerbi_response.json',
        summary_file: 'summary.txt',
        download_urls: {
          powerbi_response: `/api/solved-assignment/download/filled_powerbi_response.json?uid=user_1&aid=assign_1`,
          summary: `/api/solved-assignment/download/summary.txt?uid=user_1&aid=assign_1`
        }
      });
    }

    setIsProcessing(false);
    setMode('result');
  };

  const handleSubmit = () => {
    if (!pdfFile || !datasetFile || !templateFile) {
      setError(`Please upload PDF, Dataset, and ${mode === 'python' ? '.ipynb' : '.json'} template.`);
      return;
    }
    simulateProcessing(mode === 'python' ? 'python' : 'powerbi');
  };

  const resetForm = () => {
    setMode('selection');
    setPdfFile(null);
    setDatasetFile(null);
    setTemplateFile(null);
    setError(null);
  };

  return (
    <div className="app-container">
      {isProcessing && <ProcessingOverlay step={processingStep} progress={progress} />}

      <header>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <Sparkles color="#6366f1" size={32} />
          <span style={{ fontWeight: '700', letterSpacing: '2px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Pro Edition</span>
        </div>
        <h1>Solved Assignment System</h1>
        <p className="subtitle">AI-powered template filling for professional data assignments.</p>
      </header>

      {mode === 'selection' && (
        <div className="modes-grid">
          <div className="card" onClick={() => setMode('python')}>
            <div className="icon-wrapper">
              <Terminal size={32} />
            </div>
            <h2>Python Mode</h2>
            <p>Upload a Jupyter Notebook template and let AI solve the assignment using pandas, injecting code and explanations directly into your file.</p>
            <div className="btn btn-primary">
              Use IPYNB Template <Send size={18} />
            </div>
          </div>

          <div className="card" onClick={() => setMode('powerbi')}>
            <div className="icon-wrapper">
              <BarChart3 size={32} />
            </div>
            <h2>Power BI Mode</h2>
            <p>Fill your Power BI response templates with AI-generated visualization configurations and column mappings.</p>
            <div className="btn btn-primary">
              Use JSON Template <Send size={18} />
            </div>
          </div>
        </div>
      )}

      {(mode === 'python' || mode === 'powerbi') && (
        <div className="form-container" style={{ maxWidth: '700px', margin: '0 auto', animation: 'fadeIn 0.5s ease-out' }}>
          <button onClick={resetForm} className="btn" style={{ background: 'var(--glass)', color: 'var(--text-main)', marginBottom: '2rem' }}>
            <ChevronLeft size={18} /> Back to Selection
          </button>

          <div className="card" style={{ cursor: 'default' }}>
            <h2 style={{ marginTop: 0, marginBottom: '2rem' }}>
              {mode === 'python' ? 'Notebook Template Filler' : 'Power BI Template Filler'}
            </h2>
            
            <FileUpload 
              label="1. Assignment Paper (PDF)" 
              accept=".pdf" 
              onChange={setPdfFile} 
              fileName={pdfFile?.name}
            />
            
            <FileUpload 
              label="2. Source Dataset (CSV / XLSX)" 
              accept=".csv,.xlsx" 
              onChange={setDatasetFile} 
              fileName={datasetFile?.name}
            />

            <FileUpload 
              label={mode === 'python' ? "3. Notebook Template (.ipynb)" : "3. Power BI Template (.json)"}
              accept={mode === 'python' ? ".ipynb" : ".json"}
              onChange={setTemplateFile} 
              fileName={templateFile?.name}
            />

            {error && (
              <div style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px' }}>
                <AlertCircle size={18} /> {error}
              </div>
            )}

            <button 
              className="btn btn-primary" 
              style={{ width: '100%', padding: '1.2rem', fontSize: '1.1rem', marginTop: '1rem' }}
              onClick={handleSubmit}
            >
              Fill Template with AI <Sparkles size={20} />
            </button>
          </div>
        </div>
      )}

      {mode === 'result' && result && (
        <div className="result-container" style={{ maxWidth: '950px', margin: '0 auto', textAlign: 'center', animation: 'fadeInUp 0.6s ease-out' }}>
          <div className="card" style={{ cursor: 'default', background: 'rgba(16, 185, 129, 0.05)', borderColor: 'var(--success)' }}>
            <div style={{ background: 'var(--success)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 2rem', color: 'white' }}>
              <CheckCircle2 size={48} />
            </div>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Templates Filled Successfully!</h2>
            <p style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
              AI has processed your assignment and updated the templates with professional solutions.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginTop: '3rem' }}>
              {result.notebook_file && (
                <div className="card" style={{ padding: '1.5rem', background: 'var(--glass)' }}>
                  <FileCode size={32} color="var(--primary)" style={{ marginBottom: '1rem' }} />
                  <h4 style={{ marginBottom: '0.5rem' }}>Filled Notebook</h4>
                  <p style={{ fontSize: '0.8rem', marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{result.notebook_file}</p>
                  <button 
                    className="btn btn-primary" 
                    style={{ width: '100%' }}
                    onClick={() => handleDownload(result.download_urls?.notebook)}
                  >
                    Download .ipynb
                  </button>
                </div>
              )}
              
              {result.powerbi_response_file && (
                <div className="card" style={{ padding: '1.5rem', background: 'var(--glass)' }}>
                  <FileJson size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                  <h4 style={{ marginBottom: '0.5rem' }}>Filled JSON Template</h4>
                  <p style={{ fontSize: '0.8rem', marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{result.powerbi_response_file}</p>
                  <button 
                    className="btn btn-primary" 
                    style={{ width: '100%', background: 'var(--accent)' }}
                    onClick={() => handleDownload(result.download_urls?.powerbi_response)}
                  >
                    Download JSON
                  </button>
                </div>
              )}

              {result.summary_file && (
                <div className="card" style={{ padding: '1.5rem', background: 'var(--glass)' }}>
                  <FileText size={32} color="#10b981" style={{ marginBottom: '1rem' }} />
                  <h4 style={{ marginBottom: '0.5rem' }}>Detailed AI Summary</h4>
                  <p style={{ fontSize: '0.8rem', marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{result.summary_file}</p>
                  <button 
                    className="btn" 
                    style={{ width: '100%', background: 'var(--glass)', color: 'var(--text-main)' }}
                    onClick={() => handleDownload(result.download_urls?.summary)}
                  >
                    View Summary
                  </button>
                </div>
              )}
            </div>

            <button 
              onClick={resetForm} 
              className="btn" 
              style={{ marginTop: '3rem', background: 'transparent', color: 'var(--text-muted)', textDecoration: 'underline' }}
            >
              Start New Assignment Task
            </button>
          </div>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}} />
    </div>
  );
}

export default App;
