import { useState, useEffect } from 'react'
import { 
  ArrowLeft, Clock, Receipt, Fingerprint, 
  ChevronRight, Building, Phone, AlertCircle,
  Calendar, FileText, User, DollarSign
} from 'lucide-react'
import { apiFetch } from '../../utils/api'

export default function EmployeeProfile({ employee, onBack, lastWsEvent }) {
  const [activeTab, setActiveTab] = useState('profile')
  // Attendance
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })
  const [attendance, setAttendance] = useState([])
  const [loadingAtt, setLoadingAtt] = useState(true)
  // Payslips
  const [payslips, setPayslips] = useState([])
  const [loadingPay, setLoadingPay] = useState(true)
  // Leave
  const [leaveBalances, setLeaveBalances] = useState([])
  const [leaveRequests, setLeaveRequests] = useState([])
  const [loadingLeave, setLoadingLeave] = useState(true)
  // Salary Structure
  const [salaryStructures, setSalaryStructures] = useState([])
  const [loadingSalary, setLoadingSalary] = useState(true)

  const [selectedPayslip, setSelectedPayslip] = useState(null)

  // ---- Data Fetching ----
  const fetchAttendanceForMonth = async (month) => {
    if (!month) return
    setLoadingAtt(true)
    try {
      const start = `${month}-01`
      const endDate = new Date(month + '-01')
      endDate.setMonth(endDate.getMonth() + 1)
      endDate.setDate(0)
      const end = endDate.toISOString().split('T')[0]
      const url = `/attendance/attendance-records/?employee=${employee.id}&start_date=${start}&end_date=${end}`
      const data = await apiFetch(url)
      setAttendance(data.results || data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingAtt(false)
    }
  }

  const fetchPayslips = async () => {
    try {
      const data = await apiFetch(`/payroll/payroll-entries/?employee=${employee.id}`)
      setPayslips(data.results || data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingPay(false)
    }
  }

  const fetchLeave = async () => {
    try {
      const [balances, requests] = await Promise.all([
        apiFetch(`/attendance/leave-balances/?employee=${employee.id}`),
        apiFetch(`/attendance/leave-requests/?employee=${employee.id}`)
      ])
      setLeaveBalances(balances.results || balances)
      setLeaveRequests(requests.results || requests)
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingLeave(false)
    }
  }

  const fetchSalaryStructures = async () => {
    try {
      const data = await apiFetch(`/payroll/employee-salary-structures/?employee=${employee.id}`)
      setSalaryStructures(data.results || data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoadingSalary(false)
    }
  }

  useEffect(() => {
    fetchAttendanceForMonth(selectedMonth)
    fetchPayslips()
    fetchLeave()
    fetchSalaryStructures()
  }, [employee.id])

  useEffect(() => {
    fetchAttendanceForMonth(selectedMonth)
  }, [selectedMonth])

  // Refresh on WebSocket events
  useEffect(() => {
    if (lastWsEvent) {
      if (lastWsEvent.model === 'AttendanceRecord') fetchAttendanceForMonth(selectedMonth)
      else if (lastWsEvent.model === 'PayrollEntry') fetchPayslips()
      else if (lastWsEvent.model === 'LeaveBalance' || lastWsEvent.model === 'LeaveRequest') fetchLeave()
      else if (lastWsEvent.model === 'EmployeeSalaryStructure') fetchSalaryStructures()
    }
  }, [lastWsEvent, selectedMonth])

  // ---- Helpers ----
  const formatTime = (isoString) => {
    if (!isoString) return '--:--'
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatDate = (dateStr) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatDuration = (totalSecs) => {
    const h = Math.floor(totalSecs / 3600)
    const m = Math.floor((totalSecs % 3600) / 60)
    if (h === 0 && m === 0) return '0h'
    if (h === 0) return `${m}m`
    return `${h}h ${m}m`
  }

  const handlePunch = async () => {
    try {
      await apiFetch(`/employees/employees/${employee.id}/punch/`, { method: 'POST' })
      alert('Punch recorded successfully!')
    } catch (e) {
      alert('Failed to punch: ' + e.message)
    }
  }

  // ---- Monthly summary from current attendance list ----
  const monthSummary = attendance.reduce((acc, record) => {
    if (record.status === 'present') acc.present++
    else if (record.status === 'absent') acc.absent++
    else if (record.status === 'half_day') acc.half_day++
    acc.totalSecs += record.total_work_seconds || 0
    return acc
  }, { present: 0, absent: 0, half_day: 0, totalSecs: 0 })

  return (
    <div className="profile-container">
      <button className="btn-icon" onClick={onBack} style={{ alignSelf: 'flex-start', marginBottom: '1rem' }}>
        <ArrowLeft size={24} />
      </button>

      {/* Header Card */}
      <div className="glass-panel profile-header">
        {/* ============ AVATAR BLOCK ============ */}
        <div className="avatar-large">
          {(() => {
            // Debug: log the value to browser console
            console.log('Profile picture value:', employee.profile_picture);
            
            // Check if profile_picture exists and is a non-empty string
            const hasPicture = employee.profile_picture && 
                               typeof employee.profile_picture === 'string' && 
                               employee.profile_picture.trim() !== '';
            
            if (hasPicture) {
              // If the picture already starts with 'http', use it directly; otherwise prepend base URL
              const imageUrl = employee.profile_picture.startsWith('http')
                ? employee.profile_picture
                : `http://localhost:8000/media/${employee.profile_picture}`;
              
              return (
                <img 
                  src={imageUrl} 
                  alt="Profile" 
                  style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} 
                  onError={(e) => {
                    // Fallback to initials if image fails to load
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML = employee.first_name 
                      ? employee.first_name[0] 
                      : employee.username[0].toUpperCase();
                  }}
                />
              );
            } else {
              // No picture: show initials
              return employee.first_name ? employee.first_name[0] : employee.username[0].toUpperCase();
            }
          })()}
        </div>
        {/* ==================================== */}
        <div className="profile-info">
          <h2>{employee.first_name} {employee.last_name}</h2>
          <p className="designation">{employee.designation || 'No Designation'}</p>
          <div className="profile-meta">
            <span><Building size={14} /> {employee.department_name || employee.company_name}</span>
            {employee.phone && <span><Phone size={14} /> {employee.phone}</span>}
            <span><User size={14} /> ID: {employee.employee_id}</span>
          </div>
        </div>
        <div className="profile-status">
          <span className={`status-badge ${employee.is_active ? 'active' : 'inactive'}`}>
            {employee.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <button className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => setActiveTab('profile')}>
          <FileText size={18} /> Profile
        </button>
        <button className={`tab-button ${activeTab === 'attendance' ? 'active' : ''}`} onClick={() => setActiveTab('attendance')}>
          <Clock size={18} /> Attendance
        </button>
        <button className={`tab-button ${activeTab === 'payslips' ? 'active' : ''}`} onClick={() => setActiveTab('payslips')}>
          <Receipt size={18} /> Payslips
        </button>
        <button className={`tab-button ${activeTab === 'leave' ? 'active' : ''}`} onClick={() => setActiveTab('leave')}>
          <Calendar size={18} /> Leave
        </button>
        <button className={`tab-button ${activeTab === 'salary' ? 'active' : ''}`} onClick={() => setActiveTab('salary')}>
          <DollarSign size={18} /> Salary
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'profile' && (
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3>Employee Details</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }}>
              <div>
                <label style={{ fontWeight: 500 }}>First Name</label>
                <div>{employee.first_name}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Last Name</label>
                <div>{employee.last_name}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Username</label>
                <div>{employee.username}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Email</label>
                <div>{employee.email || 'N/A'}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Employee ID</label>
                <div>{employee.employee_id}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Hire Date</label>
                <div>
                  {employee.hire_date 
                    ? new Date(employee.hire_date).toLocaleDateString() 
                    : (employee.created_at 
                        ? new Date(employee.created_at).toLocaleDateString() + ' (created)' 
                        : 'N/A')}
                </div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Designation</label>
                <div>{employee.designation || 'N/A'}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Phone</label>
                <div>{employee.phone || 'N/A'}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Base Salary</label>
                <div>${employee.base_salary ? parseFloat(employee.base_salary).toFixed(2) : 'N/A'}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Company</label>
                <div>{employee.company_name}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Department</label>
                <div>{employee.department_name || 'N/A'}</div>
              </div>
              <div>
                <label style={{ fontWeight: 500 }}>Status</label>
                <div><span className={`status-badge ${employee.is_active ? 'active' : 'inactive'}`}>
                  {employee.is_active ? 'Active' : 'Inactive'}
                </span></div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="attendance-view">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
              <label style={{ fontWeight: 500 }}>Select Month:</label>
              <input 
                type="month" 
                value={selectedMonth} 
                onChange={(e) => setSelectedMonth(e.target.value)}
                style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}
              />
            </div>

            <div className="metrics-grid">
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: 'var(--color-primary)' }}>{formatDuration(monthSummary.totalSecs)}</div>
                <div className="metric-label">Total Hours</div>
              </div>
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: '#22c55e' }}>{monthSummary.present} days</div>
                <div className="metric-label">Present</div>
              </div>
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: '#ef4444' }}>{monthSummary.absent} days</div>
                <div className="metric-label">Absent</div>
              </div>
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: '#f59e0b' }}>{monthSummary.half_day} days</div>
                <div className="metric-label">Half Days</div>
              </div>
            </div>

            <div className="history-header">
              <h3>Daily Records</h3>
              <button className="btn-primary" onClick={handlePunch}>
                <Fingerprint size={18} /> Punch
              </button>
            </div>

            {loadingAtt ? <p>Loading attendance...</p> : attendance.length === 0 ? (
              <p>No attendance records for this month.</p>
            ) : (
              <div className="records-list">
                {attendance.map(record => (
                  <div key={record.id} className="glass-panel record-card">
                    <div className="record-main">
                      <h4>{formatDate(record.date)}</h4>
                      <div className="record-times">
                        <span className="time-in">In: {formatTime(record.first_in)}</span>
                        <span className="time-out">Out: {formatTime(record.last_out)}</span>
                      </div>
                      {record.is_anomaly && record.anomaly_reason && (
                        <div className="anomaly-warning">
                          <AlertCircle size={14} /> {record.anomaly_reason}
                        </div>
                      )}
                    </div>
                    <div className="record-stats">
                      <span className={`status-badge ${record.status === 'present' ? 'active' : 'inactive'}`}>
                        {record.status.toUpperCase()}
                      </span>
                      <div className="duration">{formatDuration(record.total_work_seconds)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'payslips' && (
          <div className="payslips-view">
            {loadingPay ? <p>Loading payslips...</p> : payslips.length === 0 ? <p>No payslips found.</p> : (
              <div className="records-list">
                {payslips.map(entry => (
                  <div key={entry.id} className="glass-panel payslip-card" onClick={() => setSelectedPayslip(entry)}>
                    <div className="payslip-icon"><Receipt size={24} /></div>
                    <div className="payslip-info">
                      <div className="period-label">Salary / Month</div>
                      <h4>{entry.period_start} to {entry.period_end}</h4>
                    </div>
                    <div className="payslip-amount">
                      <div className="net-pay">${parseFloat(entry.net_pay).toFixed(2)}</div>
                      <div className="view-details">
                        View details <ChevronRight size={14} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'leave' && (
          <div className="leave-view">
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
              <h3>Leave Balances</h3>
              {loadingLeave ? <p>Loading balances...</p> : leaveBalances.length === 0 ? (
                <p className="text-muted">No leave balances assigned.</p>
              ) : (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '1rem' }}>
                  {leaveBalances.map(bal => (
                    <div key={bal.id} className="glass-panel" style={{ padding: '1rem', minWidth: '150px', flex: '1' }}>
                      <div style={{ fontWeight: 600 }}>{bal.leave_type_name || bal.leave_type}</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                        {bal.current_balance} days
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="glass-panel" style={{ padding: '1.5rem' }}>
              <h3>Leave Requests</h3>
              {loadingLeave ? <p>Loading requests...</p> : leaveRequests.length === 0 ? (
                <p className="text-muted">No leave requests found.</p>
              ) : (
                <div className="records-list">
                  {leaveRequests.map(req => (
                    <div key={req.id} className="glass-panel record-card" style={{ padding: '1rem' }}>
                      <div className="record-main">
                        <h4>{req.leave_type_name || req.leave_type}</h4>
                        <div className="record-times">
                          <span>{req.start_date} → {req.end_date}</span>
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                          {req.reason}
                        </div>
                      </div>
                      <div className="record-stats">
                        <span className={`status-badge ${
                          req.status === 'approved' ? 'active' :
                          req.status === 'rejected' ? 'inactive' : ''
                        }`}>
                          {req.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'salary' && (
          <div className="salary-view">
            <div className="glass-panel" style={{ padding: '1.5rem' }}>
              <h3>Base Salary & Components</h3>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--color-border)' }}>
                  <span style={{ fontWeight: 600 }}>Base Salary</span>
                  <span>${employee.base_salary ? parseFloat(employee.base_salary).toFixed(2) : 'N/A'}</span>
                </div>
              </div>

              <h4 style={{ marginTop: '1.5rem' }}>Additional Components</h4>
              {loadingSalary ? <p>Loading salary structure...</p> : salaryStructures.length === 0 ? (
                <p className="text-muted">No additional salary components configured.</p>
              ) : (
                <div className="records-list">
                  {salaryStructures.map(structure => (
                    <div key={structure.id} className="glass-panel record-card" style={{ padding: '1rem' }}>
                      <div className="record-main">
                        <h4>{structure.component_name || structure.component}</h4>
                        <div className="record-times">
                          Effective: {structure.effective_date}
                          {structure.end_date && ` → ${structure.end_date}`}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                          {structure.percentage ? `${structure.percentage}%` : 'Fixed amount'}
                        </div>
                      </div>
                      <div className="record-stats">
                        <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>
                          ${parseFloat(structure.amount).toFixed(2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Payslip Modal */}
      {selectedPayslip && (
        <div className="modal-overlay" onClick={() => setSelectedPayslip(null)}>
          <div className="modal-content glass-panel payslip-modal" onClick={e => e.stopPropagation()}>
            <div className="receipt-header">
              <p>PAYSLIP</p>
              <h3>{selectedPayslip.period_start} to {selectedPayslip.period_end}</h3>
            </div>
            <div className="receipt-section">
              <h4 className="earnings-title">EARNINGS</h4>
              <hr />
              {selectedPayslip.details?.earnings?.map((e, idx) => (
                <div key={idx} className="receipt-row">
                  <span>{e.name}</span>
                  <span>${parseFloat(e.amount).toFixed(2)}</span>
                </div>
              ))}
              <hr />
              <div className="receipt-row bold">
                <span>Gross Earnings</span>
                <span className="earnings-value">${parseFloat(selectedPayslip.gross_earnings).toFixed(2)}</span>
              </div>
            </div>
            <div className="receipt-section">
              <h4 className="deductions-title">DEDUCTIONS</h4>
              <hr />
              {selectedPayslip.details?.deductions?.map((d, idx) => (
                <div key={idx} className="receipt-row">
                  <span>{d.name}</span>
                  <span>${parseFloat(d.amount).toFixed(2)}</span>
                </div>
              ))}
              <hr />
              <div className="receipt-row bold">
                <span>Total Deductions</span>
                <span className="deductions-value">${parseFloat(selectedPayslip.total_deductions).toFixed(2)}</span>
              </div>
            </div>
            <div className="receipt-net">
              <span>NET PAY</span>
              <h2>${parseFloat(selectedPayslip.net_pay).toFixed(2)}</h2>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}