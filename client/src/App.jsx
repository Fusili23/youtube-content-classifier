import { useState } from 'react'
import AnalyzeForm from './components/AnalyzeForm'
import ResultsDisplay from './components/ResultsDisplay'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [currentJobId, setCurrentJobId] = useState(null)
  const [showResults, setShowResults] = useState(false)

  const handleAnalysisSubmit = (jobId) => {
    setCurrentJobId(jobId)
    setShowResults(true)
  }

  const handleNewAnalysis = () => {
    setCurrentJobId(null)
    setShowResults(false)
  }

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header fade-in">
          <div className="logo-container">
            <div className="logo-icon">🎯</div>
            <h1>YouTube AI Detector</h1>
          </div>
          <p className="subtitle">
            Detect AI-generated content and dangerous material from YouTube videos
          </p>
        </header>

        {/* Main Content */}
        <main className="main-content">
          {!showResults ? (
            <AnalyzeForm 
              apiUrl={API_URL} 
              onSubmit={handleAnalysisSubmit} 
            />
          ) : (
            <ResultsDisplay 
              apiUrl={API_URL} 
              jobId={currentJobId}
              onNewAnalysis={handleNewAnalysis}
            />
          )}
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>
            Powered by Whisper AI, Gemini, and FFmpeg | 
            <a href={`${API_URL}/docs`} target="_blank" rel="noopener noreferrer"> API Docs</a>
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
