import { useState, useEffect } from 'react'
import axios from 'axios'
import './ResultsDisplay.css'

function ResultsDisplay({ apiUrl, jobId, onNewAnalysis }) {
  const [jobData, setJobData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [pollingInterval, setPollingInterval] = useState(null)

  useEffect(() => {
    if (!jobId) return

    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/result/${jobId}`)
        const data = response.data

        setJobData(data)

        // If completed or failed, stop polling
        if (data.status === 'completed' || data.status === 'failed') {
          setLoading(false)
          if (pollingInterval) {
            clearInterval(pollingInterval)
            setPollingInterval(null)
          }
        }
      } catch (err) {
        // If status is 202 (still processing), keep polling
        if (err.response?.status === 202) {
          setJobData({ status: err.response.data.detail.includes('pending') ? 'pending' : 'processing' })
        } else {
          setError(err.response?.data?.detail || 'Failed to fetch results')
          setLoading(false)
        }
      }
    }

    // Initial fetch
    fetchStatus()

    // Poll every 3 seconds for updates
    const interval = setInterval(fetchStatus, 3000)
    setPollingInterval(interval)

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [jobId, apiUrl])

  if (error) {
    return (
      <div className="results-container fade-in">
        <div className="card error-card">
          <h2>❌ Error</h2>
          <p>{error}</p>
          <button onClick={onNewAnalysis} className="btn btn-primary">
            Try Another Video
          </button>
        </div>
      </div>
    )
  }

  if (loading || !jobData || jobData.status === 'pending' || jobData.status === 'processing') {
    return (
      <div className="results-container fade-in">
        <div className="card loading-card">
          <div className="spinner"></div>
          <h2>Analyzing Video...</h2>
          <p className="loading-status">
            {jobData?.status === 'pending' ? '⏳ Job queued...' : '🔄 Processing video...'}
          </p>
          <div className="loading-steps">
            <div className="step">📥 Downloading video</div>
            <div className="step">🎵 Extracting audio</div>
            <div className="step">🎤 Transcribing with Whisper AI</div>
            <div className="step">🤖 Analyzing with AI</div>
          </div>
          <p className="loading-note">This may take a few minutes depending on video length</p>
        </div>
      </div>
    )
  }

  if (jobData.status === 'failed') {
    return (
      <div className="results-container fade-in">
        <div className="card error-card">
          <h2>❌ Analysis Failed</h2>
          <p>{jobData.error_message || 'An error occurred during analysis'}</p>
          <button onClick={onNewAnalysis} className="btn btn-primary">
            Try Another Video
          </button>
        </div>
      </div>
    )
  }

  // Completed successfully
  const result = jobData.result
  const videoInfo = result.video_info
  const transcription = result.transcription
  const analysis = result.analysis

  return (
    <div className="results-container fade-in">
      {/* Header with New Analysis button */}
      <div className="results-header">
        <h2>✅ Analysis Complete</h2>
        <button onClick={onNewAnalysis} className="btn btn-primary">
          🔍 Analyze Another
        </button>
      </div>

      {/* Video Info Card */}
      <div className="card video-info-card">
        <h3>📹 Video Information</h3>
        <div className="video-details">
          <div className="detail-row">
            <strong>Title:</strong>
            <span>{videoInfo.title}</span>
          </div>
          <div className="detail-row">
            <strong>Channel:</strong>
            <span>{videoInfo.uploader}</span>
          </div>
          <div className="detail-row">
            <strong>Duration:</strong>
            <span>{Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}</span>
          </div>
          <div className="detail-row">
            <strong>Language:</strong>
            <span>{transcription.language.toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* AI Detection Results */}
      <div className="card ai-detection-card">
        <h3>🤖 AI Content Detection</h3>
        
        <div className="score-display">
          <div className="score-circle" data-score={analysis.ai_generated_score}>
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="45" className="score-bg"></circle>
              <circle 
                cx="50" 
                cy="50" 
                r="45" 
                className="score-progress"
                style={{
                  strokeDashoffset: `${282.7 - (282.7 * analysis.ai_generated_score) / 100}`
                }}
              ></circle>
            </svg>
            <div className="score-text">
              <div className="score-number">{analysis.ai_generated_score}%</div>
              <div className="score-label">AI Score</div>
            </div>
          </div>
          
          <div className="score-info">
            <div className="confidence-badge">
              Confidence: {analysis.confidence}%
            </div>
            
            {analysis.ai_indicators.length > 0 && (
              <div className="indicators">
                <strong>AI Indicators:</strong>
                <ul>
                  {analysis.ai_indicators.map((indicator, idx) => (
                    <li key={idx}>{indicator}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dangerous Content Results */}
      <div className={`card danger-card ${analysis.dangerous_content ? 'danger-detected' : 'safe'}`}>
        <h3>
          {analysis.dangerous_content ? '⚠️ Dangerous Content Detected' : '✅ No Dangerous Content'}
        </h3>
        
        {analysis.dangerous_content ? (
          <div className="danger-details">
            <div className="severity-badge severity-{analysis.danger_severity}">
              Severity: {analysis.danger_severity.toUpperCase()}
            </div>
            
            <div className="danger-categories">
              <strong>Categories:</strong>
              <div className="category-tags">
                {analysis.danger_categories.map((category, idx) => (
                  <span key={idx} className="category-tag">{category}</span>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p>This video appears to be safe and does not contain harmful content.</p>
        )}
      </div>

      {/* Explanation */}
      <div className="card explanation-card">
        <h3>📝 Analysis Explanation</h3>
        <p>{analysis.explanation}</p>
      </div>

      {/* Transcription */}
      <div className="card transcription-card">
        <h3>📄 Full Transcription</h3>
        <div className="transcription-text">
          {transcription.text}
        </div>
        {transcription.segments && transcription.segments.length > 0 && (
          <details className="segments-details">
            <summary>View Timestamped Segments</summary>
            <div className="segments-list">
              {transcription.segments.map((segment, idx) => (
                <div key={idx} className="segment-item">
                  <span className="timestamp">
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                  </span>
                  <span className="segment-text">{segment.text}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  )
}

// Helper function to format seconds to MM:SS
function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${String(secs).padStart(2, '0')}`
}

export default ResultsDisplay
