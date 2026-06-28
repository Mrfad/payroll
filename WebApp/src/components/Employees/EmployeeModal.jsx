import { useState, useEffect } from 'react'
import { X, Loader2 } from 'lucide-react'
import { apiFetch } from '../../utils/api'

export default function EmployeeModal({ isOpen, onClose, onSaved, employee }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    company: '',
    department: '',
    employee_id: '',
    designation: '',
    phone: '',
    base_salary: '',
    hire_date: ''
  })
  
  const [companies, setCompanies] = useState([])
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const isEdit = !!employee

  useEffect(() => {
    if (isOpen) {
      fetchRefs()
      if (employee) {
        setFormData({
          username: employee.username || '',
          email: employee.email || '',
          first_name: employee.first_name || '',
          last_name: employee.last_name || '',
          password: '',
          company: employee.company || '',
          department: employee.department || '',
          employee_id: employee.employee_id || '',
          designation: employee.designation || '',
          phone: employee.phone || '',
          base_salary: employee.base_salary || '',
          hire_date: employee.hire_date || ''
        })
      } else {
        setFormData({
          username: '', email: '', first_name: '', last_name: '', password: '',
          company: '', department: '', employee_id: '', designation: '', phone: '', base_salary: '', hire_date: ''
        })
      }
      setError('')
    }
  }, [isOpen, employee])

  const fetchRefs = async () => {
    try {
      const comps = await apiFetch('/payroll/companies/')
      setCompanies(comps.results || comps)
      
      const depts = await apiFetch('/payroll/departments/')
      setDepartments(depts.results || depts)
    } catch (e) {
      console.error('Failed to fetch refs', e)
    }
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const payload = { ...formData }
      if (!payload.department) delete payload.department
      if (!payload.base_salary) delete payload.base_salary
      if (!payload.hire_date) delete payload.hire_date
      
      if (isEdit) {
        delete payload.username
        delete payload.password
        delete payload.email
        await apiFetch(`/payroll/employees/${employee.id}/`, {
          method: 'PATCH',
          body: JSON.stringify(payload)
        })
      } else {
        await apiFetch('/payroll/employees/enroll/', {
          method: 'POST',
          body: JSON.stringify(payload)
        })
      }
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content glass-panel">
        <div className="modal-header">
          <h2>{isEdit ? 'Edit Employee' : 'Enroll New Employee'}</h2>
          <button className="btn-icon" onClick={onClose}><X size={20} /></button>
        </div>

        {error && <div className="login-error" style={{ marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>

          {!isEdit && (
            <div className="form-row">
              <div className="form-group">
                <label>Username</label>
                <input type="text" name="username" value={formData.username} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" name="email" value={formData.email} onChange={handleChange} required />
              </div>
            </div>
          )}

          {!isEdit && (
            <div className="form-row">
              <div className="form-group">
                <label>Temporary Password</label>
                <input type="password" name="password" value={formData.password} onChange={handleChange} required />
              </div>
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label>Company</label>
              <select name="company" value={formData.company} onChange={handleChange} required>
                <option value="">Select Company</option>
                {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Department</label>
              <select name="department" value={formData.department} onChange={handleChange}>
                <option value="">Select Department (Optional)</option>
                {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Designation / Role</label>
              <input type="text" name="designation" value={formData.designation} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Employee ID (Optional)</label>
              <input type="text" name="employee_id" value={formData.employee_id} onChange={handleChange} placeholder="Auto-generated if blank" />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Phone</label>
              <input type="text" name="phone" value={formData.phone} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Base Salary</label>
              <input type="number" step="0.01" name="base_salary" value={formData.base_salary} onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Hire Date</label>
              <input type="date" name="hire_date" value={formData.hire_date || ''} onChange={handleChange} />
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={isLoading}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? <Loader2 size={18} className="spinner" /> : 'Save Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}