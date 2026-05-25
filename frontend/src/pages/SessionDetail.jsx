import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../api'

export default function SessionDetail() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    api.get(`/sessions/${sessionId}`)
      .then((res) => {
        setSession(res.data)
        if (res.data.has_analysis) {
          return api.get(`/sessions/${sessionId}/analysis`)
            .then((aRes) => setAnalysis(aRes.data))
        }
      })
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [sessionId])

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      const res = await api.post(`/sessions/${sessionId}/analyze`)
      setAnalysis(res.data.analysis)
      setSession({ ...session, has_analysis: true })
    } catch (err) {
      alert(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) return <div className="page-loading">Loading...</div>
  if (!session) return <div className="page-loading">Session not found</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/clients" className="btn-link">&larr; Back</Link>
          <h2>{session.title || 'Untitled Session'}</h2>
          <p className="text-muted">
            {new Date(session.session_date).toLocaleDateString()}
          </p>
        </div>
        {!session.has_analysis && (
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing}>
            {analyzing ? 'Analyzing...' : '🔍 Analyze with AI'}
          </button>
        )}
      </div>

      {/* Session Notes */}
      <div className="card">
        <div className="card-header"><h3>Session Notes</h3></div>
        <div className="session-notes-content">
          {session.notes.split('\n').map((line, i) => (
            <p key={i}>{line || <br />}</p>
          ))}
        </div>
      </div>

      {/* AI Insights */}
      {session.has_analysis && analysis ? (
        <InsightsDisplay analysis={analysis} />
      ) : session.has_analysis ? (
        <div className="card"><p className="empty-state">Loading analysis...</p></div>
      ) : (
        <div className="card">
          <p className="empty-state">
            Click "Analyze with AI" to extract insights from this session.
          </p>
        </div>
      )}
    </div>
  )
}

function InsightsDisplay({ analysis }) {
  return (
    <>
      {/* Session Prep Summary */}
      {analysis.session_prep && (
        <div className="card card-highlight">
          <div className="card-header"><h3>📋 Session Prep Summary</h3></div>
          <p className="prep-summary">{analysis.session_prep.summary}</p>
          {analysis.session_prep.key_topics && (
            <div className="topics-list">
              <strong>Key Topics:</strong>
              <div className="tags">
                {analysis.session_prep.key_topics.map((t, i) => (
                  <span key={i} className="tag">{t}</span>
                ))}
              </div>
            </div>
          )}
          {analysis.session_prep.recommended_focus && (
            <div className="focus-box">
              <strong>Recommended Focus:</strong>
              <p>{analysis.session_prep.recommended_focus}</p>
            </div>
          )}
        </div>
      )}

      {/* Goal Progress */}
      {analysis.goal_progress?.length > 0 && (
        <div className="card">
          <div className="card-header"><h3>🎯 Goal Progress</h3></div>
          <div className="goals-list">
            {analysis.goal_progress.map((g, i) => (
              <div key={i} className="goal-item">
                <div className="goal-header">
                  <strong>{g.goal}</strong>
                  <span className={`badge badge-${g.status === 'on_track' ? 'success' : g.status === 'completed' ? 'success' : 'warning'}`}>
                    {g.status.replace('_', ' ')}
                  </span>
                </div>
                <p className="goal-progress">{g.progress}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Emotional Patterns */}
      {analysis.emotional_patterns?.length > 0 && (
        <div className="card">
          <div className="card-header"><h3>❤️ Emotional Patterns</h3></div>
          <div className="emotions-grid">
            {analysis.emotional_patterns.map((e, i) => (
              <div key={i} className="emotion-item">
                <div className="emotion-name">{e.emotion}</div>
                <div className="emotion-bar-container">
                  <div
                    className="emotion-bar"
                    style={{
                      width: `${(e.intensity / 10) * 100}%`,
                      backgroundColor: e.intensity > 7 ? '#ef4444' : e.intensity > 4 ? '#f59e0b' : '#10b981',
                    }}
                  />
                </div>
                <div className="emotion-intensity">{e.intensity}/10</div>
                <p className="emotion-context">{e.context}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Flags */}
      {analysis.risk_flags?.length > 0 && (
        <div className="card">
          <div className="card-header"><h3>⚠️ Risk Flags</h3></div>
          <div className="risks-list">
            {analysis.risk_flags.map((r, i) => (
              <div key={i} className={`risk-item risk-${r.severity}`}>
                <div className="risk-header">
                  <span className={`badge badge-${r.severity === 'high' ? 'danger' : r.severity === 'medium' ? 'warning' : 'info'}`}>
                    {r.severity.toUpperCase()}
                  </span>
                  <strong>{r.risk}</strong>
                </div>
                <p className="risk-suggestion">{r.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}