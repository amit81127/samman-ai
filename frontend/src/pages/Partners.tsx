import { useEffect, useState } from 'react'
import { Plus, Trash2, ShieldAlert, Check, X, ShieldCheck } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../store/auth'

interface PartnerItem {
  id: string
  name: string
  relationship: string
  permissions: string[]
  is_active: boolean
  expires_at?: string
}

export default function Partners() {
  const [partners, setPartners] = useState<PartnerItem[]>([])
  const [loading, setLoading] = useState(true)

  // Grant access modal / form
  const [isGranting, setIsGranting] = useState(false)
  const [partnerName, setPartnerName] = useState('')
  const [relationship, setRelationship] = useState('Family member')
  const [grantError, setGrantError] = useState<string | null>(null)
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([
    'view_history',
    'assist_compose',
  ])

  // Manage access modal
  const [managingPartner, setManagingPartner] = useState<PartnerItem | null>(null)

  // Load partners from backend
  const loadPartners = async () => {
    setLoading(true)
    try {
      const data = await api.get<any[]>('/partners')
      if (Array.isArray(data)) {
        setPartners(
          data.map((p) => ({
            id: String(p.id || p._id),
            name: p.partner_name || p.partner_email || p.partner_id || 'Care Partner',
            relationship: p.relationship || 'Family member',
            permissions: p.permissions || ['view_history'],
            is_active: p.is_active ?? true,
            expires_at: p.expires_at,
          }))
        )
      } else {
        setPartners([])
      }
    } catch {
      setPartners([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPartners()
  }, [])

  const handleGrant = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!partnerName.trim()) return
    setGrantError(null)

    try {
      const expiry = new Date()
      expiry.setFullYear(expiry.getFullYear() + 1)

      await api.post<any>('/partners', {
        partner_id: partnerName.trim(),
        partner_name: partnerName.trim(),
        relationship: relationship,
        permissions: selectedPermissions,
        expires_at: expiry.toISOString(),
      })
      await loadPartners()
      setPartnerName('')
      setIsGranting(false)
    } catch (err: any) {
      console.error('Failed to grant partner access:', err)
      setGrantError(err?.message || 'Failed to grant partner access. Please verify the input.')
    }
  }

  const handleRevoke = async (id: string) => {
    if (!confirm('Revoke access for this partner?')) return
    setPartners((prev) => prev.filter((p) => p.id !== id))
    try {
      await api.delete(`/partners/${id}`)
      await loadPartners()
    } catch {}
  }

  const togglePermission = (perm: string) => {
    setSelectedPermissions((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm]
    )
  }

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto space-y-8">
      {/* Header matching exact screenshot */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
            SHARED WITH CARE
          </p>
          <h1 className="text-3xl font-extrabold text-navy tracking-tight">Partner access</h1>
          <p className="text-sm text-text-secondary mt-1">
            Choose who can support your communication journey.
          </p>
        </div>
        <button
          onClick={() => setIsGranting(true)}
          className="btn-primary shadow-md shadow-purple/20 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Grant access
        </button>
      </div>

      {/* Partner Permissions Information */}
      <div className="p-5 rounded-2xl bg-surface border border-border flex items-start gap-4">
        <div className="w-8 h-8 rounded-full bg-teal-light flex items-center justify-center text-teal flex-shrink-0 mt-0.5">
          <ShieldCheck className="w-4 h-4 text-teal" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-navy">Delegated Partner Access</h3>
          <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">
            Partners granted access can view approved communication history and assist with custom vocabulary setup based on assigned permissions.
          </p>
        </div>
      </div>

      {/* Grant Access Form */}
      {isGranting && (
        <div className="card p-6 border-2 border-purple/30 bg-purple-light/20 shadow-card animate-in fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-navy flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-purple" /> Grant new partner access
            </h3>
            <button
              onClick={() => setIsGranting(false)}
              className="text-xs text-text-secondary hover:text-navy"
            >
              Cancel
            </button>
          </div>
          {grantError && (
            <div className="p-3 mb-4 rounded-xl bg-red-50 text-red-700 text-xs font-medium border border-red-200">
              {grantError}
            </div>
          )}
          <form onSubmit={handleGrant} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Partner name or email
              </label>
              <input
                autoFocus
                type="text"
                required
                value={partnerName}
                onChange={(e) => setPartnerName(e.target.value)}
                placeholder="e.g. Alex Morgan or doctor@hospital.org"
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-1">
                Relationship
              </label>
              <select
                value={relationship}
                onChange={(e) => setRelationship(e.target.value)}
                className="input"
              >
                <option value="Family member">Family member</option>
                <option value="Care team">Care team</option>
                <option value="Speech therapist">Speech therapist</option>
                <option value="Educator / Teacher">Educator / Teacher</option>
                <option value="Friend">Friend</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-navy uppercase tracking-wider mb-2">
                Permissions granted
              </label>
              <div className="space-y-2">
                {[
                  { id: 'view_history', label: 'View communication history' },
                  { id: 'assist_compose', label: 'Assist with message composition' },
                  { id: 'view_boards', label: 'View vocabulary boards' },
                ].map((perm) => (
                  <label
                    key={perm.id}
                    className="flex items-center gap-2.5 text-xs font-medium text-navy cursor-pointer select-none"
                  >
                    <input
                      type="checkbox"
                      checked={selectedPermissions.includes(perm.id)}
                      onChange={() => togglePermission(perm.id)}
                      className="rounded border-border text-purple focus:ring-purple/30"
                    />
                    <span>{perm.label}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={!partnerName.trim() || selectedPermissions.length === 0}
                className="btn-primary"
              >
                Grant access
              </button>
              <button
                type="button"
                onClick={() => setIsGranting(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Manage Access Modal */}
      {managingPartner && (
        <div className="card p-6 border-2 border-teal/40 bg-teal-light/20 shadow-card animate-in fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-navy">
              Manage permissions for {managingPartner.name}
            </h3>
            <button
              onClick={() => setManagingPartner(null)}
              className="text-xs text-text-secondary hover:text-navy"
            >
              Close
            </button>
          </div>
          <p className="text-xs text-text-secondary mb-4">
            Role: <span className="text-teal font-semibold">{managingPartner.relationship}</span>
          </p>
          <div className="space-y-2 mb-6">
            <div className="flex items-center gap-2 text-xs text-navy">
              <Check className="w-4 h-4 text-success" />
              <span>Can view approved message history</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-navy">
              <Check className="w-4 h-4 text-success" />
              <span>Can suggest candidate concepts</span>
            </div>
          </div>
          <button
            onClick={() => setManagingPartner(null)}
            className="btn-secondary text-xs"
          >
            Done
          </button>
        </div>
      )}

      {/* Partner List matching reference screenshot */}
      <div className="card divide-y divide-border overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-text-secondary text-sm">
            Loading partner permissions...
          </div>
        ) : partners.length === 0 ? (
          <div className="p-10 text-center text-text-secondary text-sm">
            No partner permissions granted yet.
          </div>
        ) : (
          partners.map((partner) => {
            const initial = partner.name.charAt(0).toUpperCase() || 'P'

            return (
              <div
                key={partner.id}
                className="p-5 flex items-center justify-between gap-4 hover:bg-bg/40 transition-colors"
              >
                {/* Left: Avatar, Name & Role */}
                <div className="flex items-center gap-4 min-w-0 flex-1">
                  <div className="w-10 h-10 rounded-full bg-purple-light text-purple font-bold text-sm flex items-center justify-center flex-shrink-0">
                    {initial}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-bold text-navy truncate">{partner.name}</h3>
                    <p className="text-xs text-teal font-medium mt-0.5">{partner.relationship}</p>
                  </div>
                </div>

                {/* Right: Active status, Manage access button, Delete button */}
                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-success">
                    <span className="w-2 h-2 rounded-full bg-success" />
                    <span>Active</span>
                  </div>

                  <button
                    onClick={() => setManagingPartner(partner)}
                    className="btn-secondary text-xs px-4 py-2"
                  >
                    Manage access
                  </button>

                  <button
                    onClick={() => handleRevoke(partner.id)}
                    className="p-2 rounded-lg text-text-secondary hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Remove access"
                    aria-label="Remove access"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
