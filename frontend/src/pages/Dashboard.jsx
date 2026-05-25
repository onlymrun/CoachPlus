import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

export default function Dashboard() {
  const [clients, setClients] = useState([])
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ clients: 0, sessions: 0, analyzed: 0 })

  useEffect(() => {
    Promise.all([
      api.get('/clients?limit=5'),
      api.get('/sessions?limit=10'),
    ]).then(([clientsRes, sessionsRes]) => {
      const c = clientsRes.data
      const s = sessionsRes.data
      setClients(c)
      setSessions(s)
      setStats({
        clients: c.length,
        sessions: s.length,
        analyzed: s.filter((sess) => sess.has_analysis).length,
      })
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loading">Loading dashboard...</div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Dashboard</h2>
        <Link to="/clients" className="btn btn-primary">+ New Client</Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.clients}</div>
          <div className="stat-label">Clients</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.sessions}</div>
          <div className="stat-label">Sessions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.analyzed}</div>
          <div className="stat-label">AI Analyzed</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Recent Clients</h3>
          <Link to="/clients" className="btn-link">View all</Link>
        </div>
        {clients.length === 0 ? (
          <p className="empty-state">No clients yet. <Link to="/clients">Add your first client</Link></p>
        ) : (
          <div className="client-list">
            {clients.map((c) => (
              <Link to={`/clients/${c.id}`} key={c.id} className="client-row">
                <div className="client-avatar">{c.full_name?.charAt(0)}</div>
                <div className="client-info">
                  <strong>{c.full_name}</strong>
                  <span>{c.session_count || 0} sessions</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Recent Sessions</h3>
        </div>
        {sessions.length === 0 ? (
          <p className="empty-state">No sessions recorded yet.</p>
        ) : (
          <div className="session-list">
            {sessions.map((s) => (
              <Link to={`/sessions/${s.id}`} key={s.id} className="session-row">
                <div className="session-meta">
                  <strong>{s.title || 'Untitled Session'}</strong>
                  <span className="session-date">
                    {new Date(s.session_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="session-badges">
                  {s.has_analysis && <span className="badge badge-success">AI Analyzed</span>}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}