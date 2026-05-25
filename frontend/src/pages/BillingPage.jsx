import { useState, useEffect } from 'react'
import api from '../api'
import { useAuth } from '../context/AuthContext'
import '../billing.css'

const PLANS = [
  { id: 'starter', name: 'Starter', price: 29, clients: 10, features: ['Up to 10 clients', 'AI session analysis', 'Session prep summaries', 'Email support'] },
  { id: 'pro', name: 'Pro', price: 59, clients: 50, features: ['Up to 50 clients', 'AI session analysis', 'Advanced analytics', 'Priority support', 'Export data'] },
  { id: 'agency', name: 'Agency', price: 99, clients: 'Unlimited', features: ['Unlimited clients', 'AI session analysis', 'Team collaboration', 'White-label reports', 'API access', 'Dedicated support'] },
]

export default function BillingPage() {
  const { user, login } = useAuth()
  const [usage, setUsage] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [showConfirm, setShowConfirm] = useState(false)
  const [upgrading, setUpgrading] = useState(false)

  useEffect(() => {
    api.get('/auth/usage')
      .then((res) => setUsage(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleUpgrade = async (planId) => {
    setSelectedPlan(planId)
    setShowConfirm(true)
  }

  const confirmUpgrade = async () => {
    setUpgrading(true)
    try {
      const res = await api.patch('/auth/plan', { plan: selectedPlan })
      setUsage(null)
      setLoading(true)
      // Refresh usage
      const usageRes = await api.get('/auth/usage')
      setUsage(usageRes.data)
      // Update user context
      login(user?.email, '')
      setShowConfirm(false)
    } catch (err) {
      alert(err.response?.data?.detail || 'Upgrade failed')
    } finally {
      setUpgrading(false)
    }
  }

  if (loading) return <div className="page-loading">Loading billing info...</div>

  const currentPlanId = usage?.plan || user?.subscription_tier || 'starter'

  return (
    <div className="page">
      <div className="page-header">
        <h2>Subscription & Billing</h2>
      </div>

      {/* Current Usage */}
      {usage && (
        <div className="card">
          <div className="card-header"><h3>Current Usage</h3></div>
          <div className="usage-stats">
            <div className="usage-item">
              <div className="usage-label">Plan: <strong className="plan-badge plan-badge-{usage.plan}">{usage.plan_display_name}</strong></div>
              <div className="usage-label" style={{ marginTop: 4 }}>${usage.plan_price}/mo</div>
            </div>
            <div className="usage-item">
              <div className="usage-label">Clients</div>
              <div className="usage-bar-container">
                <div
                  className="usage-bar"
                  style={{ width: `${Math.min(usage.clients.percent || 0, 100)}%` }}
                />
              </div>
              <div className="usage-numbers">
                {usage.clients.used} / {usage.clients.unlimited ? '∞' : usage.clients.limit} used
                {!usage.clients.unlimited && usage.clients.remaining > 0 && (
                  <span className="text-muted"> ({usage.clients.remaining} remaining)</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Plan Cards */}
      <h3 className="section-title">Available Plans</h3>
      <div className="plan-cards">
        {PLANS.map((plan) => {
          const isCurrent = plan.id === currentPlanId
          return (
            <div key={plan.id} className={`card plan-card ${isCurrent ? 'plan-current' : ''}`}>
              <div className="plan-card-header">
                {isCurrent && <span className="badge badge-success">Current Plan</span>}
                <h3>{plan.name}</h3>
                <div className="plan-price">
                  <span className="plan-price-value">${plan.price}</span>
                  <span className="plan-price-period">/mo</span>
                </div>
                <div className="plan-client-limit">
                  {plan.clients === 'Unlimited' ? 'Unlimited clients' : `Up to ${plan.clients} clients`}
                </div>
              </div>
              <ul className="plan-features">
                {plan.features.map((f, i) => (
                  <li key={i} className="plan-feature">✓ {f}</li>
                ))}
              </ul>
              <button
                className={`btn ${isCurrent ? 'btn-disabled' : 'btn-primary'} btn-full`}
                disabled={isCurrent}
                onClick={() => handleUpgrade(plan.id)}
              >
                {isCurrent ? 'Current Plan' : plan.price < (usage?.plan_price || 999) ? 'Downgrade' : 'Upgrade'}
              </button>
            </div>
          )
        })}
      </div>

      {/* Confirm Modal */}
      {showConfirm && (
        <div className="modal-overlay" onClick={() => setShowConfirm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Plan Change</h3>
            <p>Switch to the <strong>{PLANS.find(p => p.id === selectedPlan)?.name}</strong> plan?</p>
            <p className="text-muted">This is a mock upgrade — no payment will be processed.</p>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowConfirm(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={confirmUpgrade} disabled={upgrading}>
                {upgrading ? 'Updating...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
