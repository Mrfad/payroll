const BASE_URL = 'http://localhost:8000/api/v1'

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token')
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  // 204 No Content for DELETE
  if (response.status === 204) {
    return null
  }

  const data = await response.json()

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh')
      window.location.reload()
    }
    throw new Error(data.detail || data.message || JSON.stringify(data))
  }

  return data
}
