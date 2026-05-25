import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

export default function ClientsPage() {
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', notes: '' })
  const [saving, setSaving] = useState(false)

  const loadClients = () => {
    api.get('/clients').then((res) => {
      setClients(res.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }

  useEffect(() => { loadClients() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.post('/clients', form)
      setForm({ full_name: '', email: '', phone: '', notes: '' })
      setShowForm(false)
      loadClients()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create client')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this client and all their sessions?')) return
    try {
      await api.delete(`/clients/${id}`)
      loadClients()
    } catch (err) {
      alert('Failed to delete')
    }
  }

  const filtered = clients.filter((c) =>
    c.full_name.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) return <div className="page-loading">Loading...</div>

  return (
    <div className="page">
      <div className="page-header">
        <h2>Clients</h2>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add Client'}
        </button>
      </div>

      {showForm && (
        <div className="card form-card">
          <h3>New Client</h3>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </div>
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={3}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Add Client'}
            </button>
          </form>
        </div>
      )}

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search clients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="card"><p className="empty-state">
          {search ? 'No clients match your search.' : 'No clients yet. Add one to get started.'}
        </p></div>
      ) : (
        <div className="client-cards">
          {filtered.map((c) => (
            <div key={c.id} className="card client-card">
              <div className="client-card-header">
                <div className="client-avatar-lg">{c.full_name?.charAt(0)}</div>
                <div>
                  <h3>{c.full_name}</h3>
                  {c.email && <p className="text-muted">{c.email}</p>}
                </div>
              </div>
              <div className="client-card-stats">
                <span>{c.session_count || 0} sessions</span>
              </div>
              <div className="client-card-actions">
                <Link to={`/clients/${c.id}`} className="btn btn-sm">View Details</Link>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(c.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}