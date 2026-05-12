import React, { useCallback, useState } from 'react';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface FileUploadProps {
  label: string;
  accept: string;
  onChange: (file: File | null) => void;
  fileName?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({ label, accept, onChange, fileName }) => {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onChange(e.dataTransfer.files[0]);
    }
  }, [onChange]);

  return (
    <div className="file-upload-container">
      <p style={{ marginBottom: '0.5rem', fontWeight: '500', fontSize: '0.9rem', color: 'var(--text-muted)' }}>{label}</p>
      <div 
        className={`upload-zone ${isDragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById(`file-input-${label}`)?.click()}
      >
        <input 
          id={`file-input-${label}`}
          type="file" 
          accept={accept}
          style={{ display: 'none' }}
          onChange={(e) => e.target.files && onChange(e.target.files[0])}
        />
        
        {fileName ? (
          <div className="file-info" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', justifyContent: 'center' }}>
            <div style={{ color: 'var(--success)' }}><CheckCircle size={24} /></div>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: '600' }}>{fileName}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>File ready</div>
            </div>
            <button 
              onClick={(e) => { e.stopPropagation(); onChange(null); }}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', marginLeft: '1rem' }}
            >
              <X size={18} />
            </button>
          </div>
        ) : (
          <div className="upload-prompt">
            <Upload size={32} style={{ marginBottom: '0.5rem', color: 'var(--primary)' }} />
            <div>
              <span style={{ color: 'var(--primary)', fontWeight: '600' }}>Click to upload</span> or drag and drop
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{accept.toUpperCase()} files supported</div>
          </div>
        )}
      </div>
    </div>
  );
};
