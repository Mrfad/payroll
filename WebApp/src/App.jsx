import { useState, useEffect } from 'react'
import { 
  Sun, Moon, LayoutDashboard, Users, 
  CreditCard, Settings, Menu, Bell, 
  DollarSign, Briefcase, TrendingUp, LogOut
} from 'lucide-react'
import './index.css'
import Login from './Login'
import EmployeesList from './components/Employees/EmployeesList'
import EmployeeProfile from './components/Employees/EmployeeProfile'

function App() {
  const [theme, setTheme] = useState('light')
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedProfileEmployee, setSelectedProfileEmployee] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'))
  const [userId, setUserId] = useState(null)
  const [lastWsEvent, setLastWsEvent] = useState(null)
  const API_URL = 'http://localhost:8000/api/v1/payroll/user-profile/me/'
  const WS_URL = 'ws://localhost:8000/ws/updates/'

  // Initialize theme from backend or fallback to local storage
  useEffect(() => {
    if (!isAuthenticated) return;
    const fetchTheme = async () => {
      const token = localStorage.getItem('token')
      let backendTheme = null
      
      if (token) {
        try {
          const res = await fetch(API_URL, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (res.ok) {
            const data = await res.json()
            if (data.user_id) {
              setUserId(data.user_id)
            }
            if (data.theme) {
              backendTheme = data.theme
            }
          } else if (res.status === 401) {
            localStorage.removeItem('token')
            localStorage.removeItem('refresh')
            setIsAuthenticated(false)
            return
          }
        } catch (e) {
          console.error('Failed to fetch theme from backend', e)
        }
      }

      const savedTheme = backendTheme || localStorage.getItem('theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      
      setTheme(savedTheme)
      localStorage.setItem('theme', savedTheme)
      document.documentElement.setAttribute('data-theme', savedTheme)
    }

    fetchTheme()
  }, [isAuthenticated])

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!userId) return;

    const ws = new WebSocket(WS_URL)
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastWsEvent(data)
        
        if (data.model === 'userprofile' && data.action === 'theme_updated' && data.user_id === userId) {
          const newTheme = data.theme
          setTheme(newTheme)
          localStorage.setItem('theme', newTheme)
          document.documentElement.setAttribute('data-theme', newTheme)
        }
      } catch (e) {
        console.error('Error parsing WebSocket message', e)
      }
    }

    return () => {
      ws.close()
    }
  }, [userId])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    setIsAuthenticated(false)
  }

  const toggleTheme = async () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)

    const token = localStorage.getItem('token')
    if (token) {
      try {
        await fetch(API_URL, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ theme: newTheme })
        })
      } catch (e) {
        console.error('Failed to save theme to backend', e)
      }
    }
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="stat-icon" style={{ marginBottom: 0 }}>
            <Briefcase size={28} />
          </div>
          <span className="sidebar-brand">ShieldPay</span>
        </div>
        <nav className="sidebar-nav">
          <button className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </button>
          <button className={`nav-item ${activeTab === 'employees' ? 'active' : ''}`} onClick={() => { setActiveTab('employees'); setSelectedProfileEmployee(null); }}>
            <Users size={20} />
            <span>Employees</span>
          </button>
          <button className={`nav-item ${activeTab === 'payroll' ? 'active' : ''}`} onClick={() => setActiveTab('payroll')}>
            <CreditCard size={20} />
            <span>Payroll</span>
          </button>
          <div style={{ flex: 1 }}></div>
          <button className="nav-item">
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button className="btn-icon">
              <Menu size={20} />
            </button>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Overview</h2>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button className="btn-icon" onClick={toggleTheme} aria-label="Toggle Theme">
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>
            <button className="btn-icon" aria-label="Notifications">
              <Bell size={20} />
            </button>
            <button className="btn-icon" aria-label="Logout" onClick={handleLogout} style={{ color: '#ef4444' }}>
              <LogOut size={20} />
            </button>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '50%', 
              backgroundColor: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}>
              FA
            </div>
          </div>
        </header>

        {/* Dashboard Area */}
        <div className="content-area">
          {activeTab === 'employees' && !selectedProfileEmployee && (
            <EmployeesList 
              lastWsEvent={lastWsEvent} 
              onRowClick={(emp) => setSelectedProfileEmployee(emp)} 
            />
          )}

          {activeTab === 'employees' && selectedProfileEmployee && (
            <EmployeeProfile 
              employee={selectedProfileEmployee} 
              onBack={() => setSelectedProfileEmployee(null)} 
              lastWsEvent={lastWsEvent}
            />
          )}
          
          {activeTab === 'dashboard' && (
            <>
              <div className="dashboard-grid">
            {/* Stat Card 1 */}
            <div className="glass-panel stat-card">
              <div className="stat-icon">
                <DollarSign size={24} />
              </div>
              <div>
                <div className="stat-label">Total Payroll</div>
                <div className="stat-value">$124,500</div>
              </div>
            </div>

            {/* Stat Card 2 */}
            <div className="glass-panel stat-card">
              <div className="stat-icon">
                <Users size={24} />
              </div>
              <div>
                <div className="stat-label">Active Employees</div>
                <div className="stat-value">42</div>
              </div>
            </div>

            {/* Stat Card 3 */}
            <div className="glass-panel stat-card">
              <div className="stat-icon">
                <TrendingUp size={24} />
              </div>
              <div>
                <div className="stat-label">Next Processing</div>
                <div className="stat-value" style={{ fontSize: '1.5rem', marginTop: '0.5rem' }}>July 1st</div>
              </div>
            </div>
          </div>

          <div className="dashboard-section glass-panel" style={{ padding: '2rem' }}>
            <h2>Recent Activity</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
              {[1, 2, 3].map((i) => (
                <div key={i} style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  padding: '1rem',
                  borderBottom: i !== 3 ? '1px solid var(--color-border)' : 'none'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--color-primary)' }}></div>
                    <div>
                      <div style={{ fontWeight: 500 }}>Payroll Approved</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>June 15th Payroll cycle completed</div>
                    </div>
                  </div>
                  <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>2 hours ago</span>
                </div>
              ))}
            </div>
            
            <div style={{ marginTop: '2rem' }}>
              <button className="btn-primary">View All Activity</button>
            </div>
          </div>
          </>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
