import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// System metrics API
export const systemAPI = {
  // Get current system metrics
  getMetrics: () => api.get('/system/metrics'),
  
  // Get historical metrics data
  getHistoricalMetrics: (timeRange = '1h') => 
    api.get(`/system/metrics/history?range=${timeRange}`),
  
  // Get system status
  getStatus: () => api.get('/system/status'),
  
  // Get system info
  getInfo: () => api.get('/system/info'),
}

// Projects API
export const projectsAPI = {
  // Get all projects
  getAll: () => api.get('/projects'),
  
  // Get project by ID
  getById: (id) => api.get(`/projects/${id}`),
  
  // Create new project
  create: (project) => api.post('/projects', project),
  
  // Update project
  update: (id, project) => api.put(`/projects/${id}`, project),
  
  // Delete project
  delete: (id) => api.delete(`/projects/${id}`),
  
  // Start project
  start: (id) => api.post(`/projects/${id}/start`),
  
  // Stop project
  stop: (id) => api.post(`/projects/${id}/stop`),
  
  // Pause project
  pause: (id) => api.post(`/projects/${id}/pause`),
  
  // Get project metrics
  getMetrics: (id) => api.get(`/projects/${id}/metrics`),
  
  // Get project logs
  getLogs: (id, limit = 100) => api.get(`/projects/${id}/logs?limit=${limit}`),
}

// Settings API
export const settingsAPI = {
  // Get all settings
  getAll: () => api.get('/settings'),
  
  // Update settings
  update: (settings) => api.put('/settings', settings),
  
  // Reset settings to defaults
  reset: () => api.post('/settings/reset'),
  
  // Export settings
  export: () => api.get('/settings/export'),
  
  // Import settings
  import: (settings) => api.post('/settings/import', settings),
}

// Alerts API
export const alertsAPI = {
  // Get all alerts
  getAll: () => api.get('/alerts'),
  
  // Get unread alerts
  getUnread: () => api.get('/alerts/unread'),
  
  // Mark alert as read
  markAsRead: (id) => api.patch(`/alerts/${id}/read`),
  
  // Mark all alerts as read
  markAllAsRead: () => api.patch('/alerts/read-all'),
  
  // Create new alert rule
  createRule: (rule) => api.post('/alerts/rules', rule),
  
  // Update alert rule
  updateRule: (id, rule) => api.put(`/alerts/rules/${id}`, rule),
  
  // Delete alert rule
  deleteRule: (id) => api.delete(`/alerts/rules/${id}`),
}

// WebSocket connection for real-time updates
export class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect() {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws`
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.notifyListeners(data.type, data.payload)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => this.connect(), 5000)
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push(callback)
    
    return () => {
      const callbacks = this.listeners.get(eventType)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
      }
    }
  }

  notifyListeners(eventType, data) {
    const callbacks = this.listeners.get(eventType)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }
}

// Create singleton instance
export const wsService = new WebSocketService()

export default api
