import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus,
  BookOpen,
  Edit3,
  Trash2,
  ArrowRight,
  Check,
  X,
  Star,
  Layers,
  Sparkles,
} from 'lucide-react'
import { api } from '../lib/api'

interface BoardItem {
  id: string
  name: string
  description?: string
  tile_count: number
  categories?: string[]
  is_default?: boolean
}

interface CustomTile {
  id: string
  label: string
  category?: string
  symbol_uri?: string
  color?: string
}

const BOARD_ACCENTS = [
  'bg-[#5145E9]',
  'bg-[#009F9A]',
  'bg-[#E8A33D]',
  'bg-[#35BD91]',
  'bg-[#6366F1]',
]

const ALL_CATEGORIES = [
  'Basic needs',
  'Everyday',
  'Health',
  'Feelings',
  'People',
  'Actions',
  'Comfort',
]

export default function Vocabulary() {
  const navigate = useNavigate()

  const [boards, setBoards] = useState<BoardItem[]>([])
  const [loading, setLoading] = useState(true)

  // Modal / Form state for Add / Edit
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBoard, setEditingBoard] = useState<BoardItem | null>(null)
  const [boardName, setBoardName] = useState('')
  const [boardDescription, setBoardDescription] = useState('')
  const [boardCategories, setBoardCategories] = useState<string[]>(['Basic needs', 'Everyday'])
  const [isDefault, setIsDefault] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // Custom Tiles state
  const [selectedBoardForTiles, setSelectedBoardForTiles] = useState<BoardItem | null>(null)
  const [boardTiles, setBoardTiles] = useState<CustomTile[]>([])
  const [isAddingTile, setIsAddingTile] = useState(false)
  const [tileLabel, setTileLabel] = useState('')
  const [tileCategory, setTileCategory] = useState('Basic needs')

  // Load boards from backend
  const loadBoards = async () => {
    setLoading(true)
    try {
      const data = await api.get<any[]>('/boards')
      if (Array.isArray(data)) {
        setBoards(
          data.map((b) => ({
            id: String(b.id || b._id),
            name: b.name,
            description: b.description,
            tile_count: b.tile_count ?? 0,
            categories: b.categories || [],
            is_default: b.is_default ?? false,
          }))
        )
      } else {
        setBoards([])
      }
    } catch (err: any) {
      console.error('Failed to load boards:', err)
      setBoards([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBoards()
  }, [])

  // Open Create Board Modal
  const handleOpenCreateModal = () => {
    setEditingBoard(null)
    setBoardName('')
    setBoardDescription('')
    setBoardCategories(['Basic needs', 'Everyday'])
    setIsDefault(false)
    setFormError(null)
    setIsModalOpen(true)
  }

  // Open Edit Board Modal
  const handleOpenEditModal = (board: BoardItem) => {
    setEditingBoard(board)
    setBoardName(board.name)
    setBoardDescription(board.description || '')
    setBoardCategories(board.categories && board.categories.length > 0 ? board.categories : ['Everyday'])
    setIsDefault(board.is_default || false)
    setFormError(null)
    setIsModalOpen(true)
  }

  // Toggle Category selection in Form
  const toggleCategory = (cat: string) => {
    setBoardCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    )
  }

  // Create or Update Board Submit Handler
  const handleSaveBoard = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!boardName.trim()) {
      setFormError('Please enter a board name.')
      return
    }

    setIsSubmitting(true)
    setFormError(null)

    try {
      if (editingBoard) {
        // UPDATE EXISTING BOARD via PATCH /boards/{id}
        const updated = await api.patch<any>(`/boards/${editingBoard.id}`, {
          name: boardName.trim(),
          description: boardDescription.trim() || undefined,
          categories: boardCategories,
          is_default: isDefault,
        })

        setBoards((prev) =>
          prev.map((b) => {
            if (b.id === editingBoard.id) {
              return {
                ...b,
                name: updated.name,
                description: updated.description,
                categories: updated.categories || boardCategories,
                is_default: updated.is_default ?? isDefault,
              }
            }
            // If new board was set as default, others are no longer default
            return isDefault ? { ...b, is_default: false } : b
          })
        )
        setIsModalOpen(false)
      } else {
        // CREATE NEW BOARD via POST /boards
        const created = await api.post<any>('/boards', {
          name: boardName.trim(),
          description: boardDescription.trim() || undefined,
          categories: boardCategories,
          is_default: isDefault,
        })

        const newBoardItem: BoardItem = {
          id: String(created.id || created._id),
          name: created.name,
          description: created.description,
          tile_count: created.tile_count ?? 0,
          categories: created.categories || boardCategories,
          is_default: created.is_default ?? isDefault,
        }

        setBoards((prev) => [
          ...prev.map((b) => (isDefault ? { ...b, is_default: false } : b)),
          newBoardItem,
        ])
        setIsModalOpen(false)
      }
    } catch (err: any) {
      setFormError(err.message || 'Failed to save board. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Delete Board via DELETE /boards/{id}
  const handleDeleteBoard = async (board: BoardItem) => {
    if (!window.confirm(`Are you sure you want to delete "${board.name}"?`)) return

    try {
      await api.delete(`/boards/${board.id}`)
      setBoards((prev) => prev.filter((b) => b.id !== board.id))
      if (selectedBoardForTiles?.id === board.id) {
        setSelectedBoardForTiles(null)
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete board.')
    }
  }

  // View / Manage Board Tiles
  const handleOpenBoardTiles = async (board: BoardItem) => {
    setSelectedBoardForTiles(board)
    try {
      const tiles = await api.get<any[]>(`/boards/${board.id}/vocabulary`)
      if (Array.isArray(tiles)) {
        setBoardTiles(
          tiles.map((t) => ({
            id: String(t.id || t._id),
            label: t.label,
            category: t.category,
            color: t.color,
          }))
        )
        return
      }
    } catch {
      setBoardTiles([])
    }
  }

  // Add tile to board via POST /boards/{id}/vocabulary
  const handleAddTile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tileLabel.trim() || !selectedBoardForTiles) return

    try {
      const res = await api.post<any>(`/boards/${selectedBoardForTiles.id}/vocabulary`, {
        label: tileLabel.trim(),
        category: tileCategory,
        position: boardTiles.length,
      })

      const newTile: CustomTile = {
        id: String(res.id || res._id),
        label: res.label || tileLabel.trim(),
        category: res.category || tileCategory,
      }

      setBoardTiles((prev) => [...prev, newTile])
      setBoards((prev) =>
        prev.map((b) =>
          b.id === selectedBoardForTiles.id ? { ...b, tile_count: b.tile_count + 1 } : b
        )
      )
      setTileLabel('')
      setIsAddingTile(false)
    } catch (err: any) {
      alert(err.message || 'Failed to add tile.')
    }
  }

  // Delete tile via DELETE /vocabulary/{id}
  const handleDeleteTile = async (tileId: string) => {
    try {
      await api.delete(`/vocabulary/${tileId}`)
      setBoardTiles((prev) => prev.filter((t) => t.id !== tileId))
      if (selectedBoardForTiles) {
        setBoards((prev) =>
          prev.map((b) =>
            b.id === selectedBoardForTiles.id
              ? { ...b, tile_count: Math.max(0, b.tile_count - 1) }
              : b
          )
        )
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete tile.')
    }
  }

  // Open Board in Communicator Page
  const handleOpenInCommunicator = (board: BoardItem) => {
    navigate('/communicate', { state: { boardId: board.id } })
  }

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-10">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold tracking-widest text-teal uppercase mb-1">
            PERSONALIZE YOUR BOARD
          </p>
          <h1 className="text-3xl font-extrabold text-navy tracking-tight">Vocabulary boards</h1>
          <p className="text-sm text-text-secondary mt-1">
            Create, manage and organize symbols tailored to different settings, routines, and needs.
          </p>
        </div>
        <button
          onClick={handleOpenCreateModal}
          className="btn-primary shadow-md shadow-purple/20 self-start sm:self-auto flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Create board
        </button>
      </div>

      {/* Boards Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {boards.map((board, idx) => {
          const accentColor = BOARD_ACCENTS[idx % BOARD_ACCENTS.length]

          return (
            <div
              key={board.id}
              className="card overflow-hidden flex flex-col justify-between hover:shadow-card-hover transition-all group border border-border"
            >
              {/* Colored Header Banner */}
              <div
                className={`h-24 ${accentColor} p-4 flex items-center justify-between text-white relative select-none`}
              >
                <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-xs flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <div className="flex items-center gap-1.5">
                  {board.is_default && (
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-white/25 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <Star className="w-3 h-3 fill-white" /> Default
                    </span>
                  )}
                  <span className="text-xs font-bold uppercase tracking-wider bg-black/20 px-2.5 py-1 rounded-full">
                    Board {idx + 1}
                  </span>
                </div>
              </div>

              {/* Board Details */}
              <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-lg font-bold text-navy tracking-tight">{board.name}</h3>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleOpenEditModal(board)}
                        className="p-1.5 rounded-lg text-text-secondary hover:text-navy hover:bg-bg transition-colors"
                        title="Edit board"
                        aria-label={`Edit ${board.name}`}
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteBoard(board)}
                        className="p-1.5 rounded-lg text-text-secondary hover:text-red-500 hover:bg-red-50 transition-colors"
                        title="Delete board"
                        aria-label={`Delete ${board.name}`}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-text-secondary mt-1 line-clamp-2">
                    {board.description || 'Custom vocabulary symbol board'}
                  </p>

                  {/* Category Pills */}
                  {board.categories && board.categories.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {board.categories.slice(0, 3).map((cat) => (
                        <span
                          key={cat}
                          className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-bg text-text-secondary"
                        >
                          {cat}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer Metadata & Actions */}
                <div className="pt-3 border-t border-border flex items-center justify-between">
                  <span className="text-xs font-semibold px-2 py-0.5 bg-bg rounded-md text-text-secondary">
                    {board.tile_count} {board.tile_count === 1 ? 'symbol' : 'symbols'}
                  </span>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleOpenBoardTiles(board)}
                      className="text-xs font-semibold text-text-secondary hover:text-navy transition-colors flex items-center gap-1"
                    >
                      <Layers className="w-3.5 h-3.5" /> Tiles
                    </button>
                    <button
                      onClick={() => handleOpenInCommunicator(board)}
                      className="text-xs font-bold text-purple hover:text-purple-hover inline-flex items-center gap-1 transition-colors"
                    >
                      Open board <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )
        })}

        {/* Create New Board Card Button */}
        <button
          onClick={handleOpenCreateModal}
          className="card border-2 border-dashed border-border hover:border-purple/60 hover:bg-purple-light/20 flex flex-col items-center justify-center p-8 transition-all min-h-60 group text-center select-none"
        >
          <div className="w-12 h-12 rounded-2xl bg-purple-light text-purple flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
            <Plus className="w-6 h-6" />
          </div>
          <span className="text-sm font-bold text-navy group-hover:text-purple transition-colors">
            New board
          </span>
          <span className="text-xs text-text-secondary mt-1">
            Create custom categorized board
          </span>
        </button>
      </div>

      {/* Selected Board Vocabulary Tiles Section */}
      {selectedBoardForTiles && (
        <div className="card p-6 md:p-8 space-y-6 border-2 border-teal/30 bg-teal-light/10 animate-in fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border">
            <div>
              <span className="text-xs font-bold tracking-widest text-teal uppercase">
                BOARD SYMBOLS
              </span>
              <h2 className="text-2xl font-bold text-navy">
                Symbols in "{selectedBoardForTiles.name}"
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsAddingTile(true)}
                className="btn-primary bg-teal hover:bg-[#008782] text-xs py-2 flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" /> Add symbol tile
              </button>
              <button
                onClick={() => setSelectedBoardForTiles(null)}
                className="btn-secondary text-xs py-2"
              >
                Close
              </button>
            </div>
          </div>

          {/* Add Tile Form */}
          {isAddingTile && (
            <form onSubmit={handleAddTile} className="card p-5 bg-white space-y-3 shadow-xs">
              <h4 className="text-xs font-bold uppercase text-navy">Add new symbol word</h4>
              <div className="grid sm:grid-cols-2 gap-3">
                <input
                  autoFocus
                  type="text"
                  required
                  value={tileLabel}
                  onChange={(e) => setTileLabel(e.target.value)}
                  placeholder="Symbol label e.g. Blanket"
                  className="input text-xs"
                />
                <select
                  value={tileCategory}
                  onChange={(e) => setTileCategory(e.target.value)}
                  className="input text-xs"
                >
                  <option value="Basic needs">Basic needs</option>
                  <option value="Health">Health</option>
                  <option value="Feelings">Feelings</option>
                  <option value="Actions">Actions</option>
                  <option value="People">People</option>
                  <option value="Everyday">Everyday</option>
                  <option value="Comfort">Comfort</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn-primary text-xs py-2">
                  Save symbol
                </button>
                <button
                  type="button"
                  onClick={() => setIsAddingTile(false)}
                  className="btn-secondary text-xs py-2"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Tile Grid */}
          {boardTiles.length === 0 ? (
            <p className="text-xs text-text-secondary py-4 text-center">
              No custom tiles added to this board yet. Click "Add symbol tile" above to add vocabulary words.
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {boardTiles.map((tile) => (
                <div
                  key={tile.id}
                  className="p-3 rounded-xl bg-white border border-border shadow-xs flex flex-col justify-between hover:border-teal/40 transition-all"
                >
                  <div className="text-2xl mb-1">💬</div>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-navy truncate">{tile.label}</p>
                    <p className="text-[10px] text-teal truncate mt-0.5">{tile.category}</p>
                  </div>
                  <div className="pt-2 mt-2 border-t border-border flex justify-end">
                    <button
                      onClick={() => handleDeleteTile(tile.id)}
                      className="text-text-secondary hover:text-red-500 transition-colors p-0.5"
                      title="Delete tile"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* CREATE / EDIT BOARD MODAL DIALOG */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy/50 backdrop-blur-xs animate-in fade-in">
          <div
            className="card p-6 md:p-8 max-w-lg w-full bg-surface shadow-2xl border border-border space-y-6 relative animate-in zoom-in-95"
            role="dialog"
            aria-modal="true"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-purple-light text-purple flex items-center justify-center">
                  <BookOpen className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-navy">
                    {editingBoard ? `Edit "${editingBoard.name}"` : 'Create New Board'}
                  </h3>
                  <p className="text-xs text-text-secondary">
                    {editingBoard
                      ? 'Update board title, description and categories'
                      : 'Set up a new tailored vocabulary symbol board'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-text-secondary hover:bg-bg hover:text-navy transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Error Banner */}
            {formError && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-600">
                {formError}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSaveBoard} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  Board Title <span className="text-red-500">*</span>
                </label>
                <input
                  autoFocus
                  type="text"
                  required
                  value={boardName}
                  onChange={(e) => setBoardName(e.target.value)}
                  placeholder="e.g. Daily needs, Hospital care, Work & Meetings"
                  className="input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  Description (optional)
                </label>
                <input
                  type="text"
                  value={boardDescription}
                  onChange={(e) => setBoardDescription(e.target.value)}
                  placeholder="e.g. Words and symbols for everyday communication"
                  className="input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-navy uppercase tracking-wider mb-1.5">
                  Categories
                </label>
                <p className="text-xs text-text-secondary mb-2">
                  Select which symbol categories to organize on this board:
                </p>
                <div className="flex flex-wrap gap-2">
                  {ALL_CATEGORIES.map((cat) => {
                    const isSelected = boardCategories.includes(cat)
                    return (
                      <button
                        type="button"
                        key={cat}
                        onClick={() => toggleCategory(cat)}
                        className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all flex items-center gap-1.5 ${
                          isSelected
                            ? 'bg-purple text-white shadow-xs'
                            : 'bg-bg text-text-secondary border border-border hover:border-purple/40 hover:text-navy'
                        }`}
                      >
                        {isSelected && <Check className="w-3 h-3" />}
                        {cat}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Default Board Checkbox */}
              <div className="pt-2">
                <label className="flex items-center gap-3 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={isDefault}
                    onChange={(e) => setIsDefault(e.target.checked)}
                    className="w-4 h-4 rounded text-purple focus:ring-purple border-border"
                  />
                  <div>
                    <span className="text-xs font-semibold text-navy">
                      Set as primary default board
                    </span>
                    <p className="text-[11px] text-text-secondary">
                      Opens automatically when navigating to the communication board.
                    </p>
                  </div>
                </label>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-border">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isSubmitting}
                  className="btn-secondary text-xs px-4 py-2.5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !boardName.trim()}
                  className="btn-primary text-xs px-5 py-2.5 shadow-md shadow-purple/20"
                >
                  {isSubmitting
                    ? 'Saving...'
                    : editingBoard
                    ? 'Save Changes'
                    : 'Create Board'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
