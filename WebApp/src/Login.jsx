import { useState } from 'react'
import { Briefcase, Lock, User, Loader2 } from 'lucide-react'

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/v1/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (response.ok && data.access) {
        localStorage.setItem('token', data.access)
        if (data.refresh) {
          localStorage.setItem('refresh', data.refresh)
        }
        onLoginSuccess()
      } else {
        setError(data.detail || 'Invalid credentials. Please try again.')
      }
    } catch (err) {
      setError('Failed to connect to the server. Please ensure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card glass-panel">
        <div className="login-header">
          <div className="login-logo">
            <Briefcase size={36} color="white" />
          </div>
          <h1>Welcome Back</h1>
          <p>Sign in to your ShieldPay dashboard</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <div className="input-with-icon">
              <User size={18} className="input-icon" />
              <input 
                type="text" 
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <div className="input-with-icon">
              <Lock size={18} className="input-icon" />
              <input 
                type="password" 
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-primary login-btn" disabled={isLoading}>
            {isLoading ? <Loader2 size={20} className="spinner" /> : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
