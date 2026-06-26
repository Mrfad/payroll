import { useState, useEffect } from 'react'
import { 
  ArrowLeft, Clock, Receipt, Fingerprint, 
  ChevronRight, Building, Phone, AlertCircle 
} from 'lucide-react'
import { apiFetch } from '../../utils/api'

export default function EmployeeProfile({ employee, onBack, lastWsEvent }) {
  const [activeTab, setActiveTab] = useState('attendance')
  const [attendance, setAttendance] = useState([])
  const [payslips, setPayslips] = useState([])
  const [loadingAtt, setLoadingAtt] = useState(true)
  const [loadingPay, setLoadingPay] = useState(true)
  const [selectedPayslip, setSelectedPayslip] = useState(null)

  const fetchAttendance = async () => {
    try {
      const data = await apiFetch(`/payroll/attendance-records/?employee=${employee.id}`)
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

  useEffect(() => {
    fetchAttendance()
    fetchPayslips()
  }, [employee.id])

  useEffect(() => {
    if (lastWsEvent) {
      if (lastWsEvent.model === 'AttendanceRecord') {
        fetchAttendance()
      } else if (lastWsEvent.model === 'PayrollEntry') {
        fetchPayslips()
      }
    }
  }, [lastWsEvent])

  const handlePunch = async () => {
    try {
      await apiFetch(`/payroll/employees/${employee.id}/punch/`, { method: 'POST' })
      alert('Punch recorded successfully!')
    } catch (e) {
      alert('Failed to punch: ' + e.message)
    }
  }

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

  // Calculate stats
  let totalWorkSecs = 0, totalOTSecs = 0, absences = 0
  attendance.forEach(r => {
    totalWorkSecs += r.total_work_seconds || 0
    totalOTSecs += r.overtime_seconds || 0
    if (r.status === 'absent') absences++
  })

  return (
    <div className="profile-container">
      <button className="btn-icon" onClick={onBack} style={{ alignSelf: 'flex-start', marginBottom: '1rem' }}>
        <ArrowLeft size={24} />
      </button>

      {/* Header Card */}
      <div className="glass-panel profile-header">
        <div className="avatar-large">
          {employee.first_name ? employee.first_name[0] : employee.username[0].toUpperCase()}
        </div>
        <div className="profile-info">
          <h2>{employee.first_name} {employee.last_name}</h2>
          <p className="designation">{employee.designation || 'No Designation'}</p>
          <div className="profile-meta">
            <span><Building size={14} /> {employee.department_name || employee.company_name}</span>
            {employee.phone && <span><Phone size={14} /> {employee.phone}</span>}
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
        <button className={`tab-button ${activeTab === 'attendance' ? 'active' : ''}`} onClick={() => setActiveTab('attendance')}>
          <Clock size={18} /> Attendance
        </button>
        <button className={`tab-button ${activeTab === 'payslips' ? 'active' : ''}`} onClick={() => setActiveTab('payslips')}>
          <Receipt size={18} /> Payslips
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'attendance' && (
          <div className="attendance-view">
            <div className="metrics-grid">
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: 'var(--color-primary)' }}>{formatDuration(totalWorkSecs)}</div>
                <div className="metric-label">Total Hours</div>
              </div>
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: '#f59e0b' }}>{formatDuration(totalOTSecs)}</div>
                <div className="metric-label">Total OT</div>
              </div>
              <div className="glass-panel metric-card">
                <div className="metric-value" style={{ color: '#ef4444' }}>{absences} days</div>
                <div className="metric-label">Absences</div>
              </div>
            </div>

            <div className="history-header">
              <h3>History</h3>
              <button className="btn-primary" onClick={handlePunch}>
                <Fingerprint size={18} /> Punch
              </button>
            </div>

            {loadingAtt ? <p>Loading attendance...</p> : attendance.length === 0 ? <p>No attendance records.</p> : (
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
