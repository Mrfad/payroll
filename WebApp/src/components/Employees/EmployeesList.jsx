import { useState, useEffect } from 'react'
import { Search, Plus, Edit2, Trash2, UserX, RefreshCcw } from 'lucide-react'
import { apiFetch } from '../../utils/api'
import EmployeeModal from './EmployeeModal'

export default function EmployeesList({ lastWsEvent, onRowClick }) {
  const [employees, setEmployees] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState(null)
  const [showDeleted, setShowDeleted] = useState(false)

  const fetchEmployees = async () => {
    setIsLoading(true)
    try {
      const url = showDeleted ? '/employees/employees/?show_deleted=true' : '/employees/employees/';

      const data = await apiFetch(url)
      setEmployees(data.results || data)
    } catch (e) {
      console.error('Failed to fetch employees', e)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchEmployees()
  }, [showDeleted])

  useEffect(() => {
    if (lastWsEvent && ['Employee', 'Department', 'Company'].includes(lastWsEvent.model)) {
      fetchEmployees()
    }
  }, [lastWsEvent])

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return

    try {
      await apiFetch(`/payroll/employees/${id}/`, { method: 'DELETE' })
      fetchEmployees()
    } catch (e) {
      alert('Failed to delete: ' + e.message)
    }
  }

  const handleRestore = async (id) => {
    try {
      await apiFetch(`/payroll/employees/${id}/restore/?show_deleted=true`, { method: 'POST' })
      fetchEmployees()
    } catch (e) {
      alert('Failed to restore: ' + e.message)
    }
  }

  const handleOpenModal = (emp = null) => {
    setSelectedEmployee(emp)
    setIsModalOpen(true)
  }

  const handleModalSaved = () => {
    setIsModalOpen(false)
    fetchEmployees()
  }

  const filtered = employees.filter(e => {
    const term = searchTerm.toLowerCase()
    return (
      (e.first_name || '').toLowerCase().includes(term) ||
      (e.last_name || '').toLowerCase().includes(term) ||
      (e.employee_id || '').toLowerCase().includes(term) ||
      (e.designation || '').toLowerCase().includes(term)
    )
  })

  return (
    <div className="list-container">
      <div className="list-header">
        <div>
          <h2>Team Members</h2>
          <p className="text-muted">Manage your employees, roles, and access.</p>
        </div>
        <div className="list-actions">
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
            <input
              type="checkbox"
              checked={showDeleted}
              onChange={(e) => setShowDeleted(e.target.checked)}
            />
            Show Deleted
          </label>
          <div className="input-with-icon" style={{ width: '250px' }}>
            <Search size={18} className="input-icon" />
            <input
              type="text"
              placeholder="Search employees..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="btn-primary" onClick={() => handleOpenModal()}>
            <Plus size={18} />
            <span>Add Employee</span>
          </button>
        </div>
      </div>

      <div className="glass-panel table-container">
        {isLoading ? (
          <div className="loading-state">Loading employees...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Company</th>
                <th>Designation</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-state">No employees found.</td>
                </tr>
              ) : (
                filtered.map(emp => (
                  <tr key={emp.id} className="clickable-row" onClick={() => onRowClick && onRowClick(emp)}>
                    <td>{emp.employee_id}</td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{emp.first_name} {emp.last_name}</div>
                      <div className="text-muted" style={{ fontSize: '0.8rem' }}>{emp.username}</div>
                    </td>
                    <td>{emp.company_name}</td>
                    <td>{emp.designation || '-'}</td>
                    <td>
                      <span className={`status-badge ${emp.is_active ? 'active' : 'inactive'}`}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div className="row-actions">
                        {emp.is_deleted ? (
                          <button className="btn-icon small success" style={{ color: '#22c55e' }} onClick={(e) => { e.stopPropagation(); handleRestore(emp.id); }} title="Restore">
                            <RefreshCcw size={16} />
                          </button>
                        ) : (
                          <>
                            <button className="btn-icon small" onClick={(e) => { e.stopPropagation(); handleOpenModal(emp); }} title="Edit">
                              <Edit2 size={16} />
                            </button>
                            <button className="btn-icon small danger" onClick={(e) => { e.stopPropagation(); handleDelete(emp.id); }} title="Delete">
                              <Trash2 size={16} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      <EmployeeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSaved={handleModalSaved}
        employee={selectedEmployee}
      />
    </div>
  )
}
