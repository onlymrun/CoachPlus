import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../api'

export default function ClientDetail() {
  const { clientId } = useParams()
  const navigate = useNavigate()
  const [client, setClient] = useState(null)
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ title: '', notes: '' })
  const [saving, setSaving] = useState(false)

  const loadData = () => {
    Promise.all([
      api.get(`/clients/${clientId}`),
      api.get(`/sessions?client_id=${clientId}`),
    ]).then(([clientRes, sessionsRes]) => {
      setClient(clientRes.data)
      setSessions(sessionsRes.data)
    }).catch(() => {
      navigate('/clients')
    }).finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [clientId])

  const handleCreateSession = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/sessions', { client_id: clientId, ...form })
      setForm({ title: '', notes: '' })
      setShowForm(false)
      loadData()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create session')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="page-loading">Loading...</div>
  if (!client) return <div className="page-loading">Client not found</div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/clients" className="btn-link">&larr; Back to Clients</Link>
          <h2>{client.full_name}</h2>
          {client.email && <p className="text-muted">{client.email}</p>}
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ New Session'}
        </button>
      </div>

      {showForm && (
        <div className="card form-card">
          <h3>New Session Note</h3>
          <form onSubmit={handleCreateSession}>
            <div className="form-group">
              <label>Title</label>
              <input
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="Session 3 - Progress Check"
              />
            </div>
            <div className="form-group">
              <label>Session Notes *</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={8}
                placeholder="Write your session notes here. Be detailed — CoachPlus AI will analyze them for insights..."
                required
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Session & Analyze'}
            </button>
          </form>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="card"><p className="empty-state">No sessions recorded for this client.</p></div>
      ) : (
        <>
          <h3 className="section-title">Sessions ({sessions.length})</h3>
          {sessions.map((s) => (
            <Link to={`/sessions/${s.id}`} key={s.id} className="card session-card">
              <div className="session-card-header">
                <div>
                  <h4>{s.title || 'Untitled Session'}</h4>
                  <p className="text-muted">{new Date(s.session_date).toLocaleDateString()}</p>
                </div>
                <div className="session-badges">
                  {s.has_analysis && <span className="badge badge-success">AI Analyzed</span>}
                </div>
              </div>
              <p className="session-notes-preview">{s.notes?.slice(0, 200)}...</p>
            </Link>
          ))}
        </>
      )}
    </div>
  )
}