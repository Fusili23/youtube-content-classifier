import { useState } from 'react'
import axios from 'axios'
import './AnalyzeForm.css'

function AnalyzeForm({ apiUrl, onSubmit }) {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    
    // Basic URL validation
    if (!youtubeUrl.trim()) {
      setError('Please enter a YouTube URL')
      return
    }
    
    if (!youtubeUrl.includes('youtube.com') && !youtubeUrl.includes('youtu.be')) {
      setError('Please enter a valid YouTube URL')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await axios.post(`${apiUrl}/api/analyze`, {
        youtube_url: youtubeUrl
      })

      const { job_id } = response.data
      onSubmit(job_id)
    } catch (err) {
      console.error('Error submitting analysis:', err)
      setError(err.response?.data?.detail || 'Failed to submit analysis. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="analyze-form-container fade-in">
      <div className="card analyze-form-card">
        <h2>🔍 Analyze YouTube Video</h2>
        <p className="form-description">
          Enter a YouTube URL to analyze the content for AI-generated material and potentially dangerous content.
        </p>

        <form onSubmit={handleSubmit} className="analyze-form">
          <div className="input-group">
            <label htmlFor="youtube-url">YouTube URL</label>
            <input
              id="youtube-url"
              type="text"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              disabled={isSubmitting}
              autoFocus
            />
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <div className="spinner-small"></div>
                Submitting...
              </>
            ) : (
              <>
                🚀 Analyze Video
              </>
            )}
          </button>
        </form>

        <div className="features-grid">
          <div className="feature-item">
            <div className="feature-icon">🤖</div>
            <div className="feature-text">
              <strong>AI Detection</strong>
              <p>Identify AI-generated content</p>
            </div>
          </div>
          
          <div className="feature-item">
            <div className="feature-icon">⚠️</div>
            <div className="feature-text">
              <strong>Safety Check</strong>
              <p>Flag dangerous content</p>
            </div>
          </div>
          
          <div className="feature-item">
            <div className="feature-icon">🎤</div>
            <div className="feature-text">
              <strong>Transcription</strong>
              <p>Whisper AI-powered</p>
            </div>
          </div>
          
          <div className="feature-item">
            <div className="feature-icon">⚡</div>
            <div className="feature-text">
              <strong>Fast Analysis</strong>
              <p>Results in minutes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyzeForm
