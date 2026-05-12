import React from 'react';

interface ProcessingOverlayProps {
  step: string;
  progress: number;
}

export const ProcessingOverlay: React.FC<ProcessingOverlayProps> = ({ step, progress }) => {
  return (
    <div className="overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      animation: 'fadeIn 0.3s ease-out'
    }}>
      <div className="loading-spinner" style={{ marginBottom: '2rem' }}></div>
      <h2 style={{ marginBottom: '1rem', color: 'var(--text-main)' }}>{step}</h2>
      <div className="progress-bar-container" style={{
        width: '300px',
        height: '8px',
        background: 'var(--glass)',
        borderRadius: '4px',
        overflow: 'hidden',
        border: '1px solid var(--glass-border)'
      }}>
        <div className="progress-bar-fill" style={{
          width: `${progress}%`,
          height: '100%',
          background: 'var(--primary)',
          transition: 'width 0.3s ease-out',
          boxShadow: '0 0 10px var(--primary)'
        }}></div>
      </div>
      <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
        Analyzing dataset and solving questions using AI...
      </p>
    </div>
  );
};
