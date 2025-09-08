import { useState, useEffect } from 'react'
import { systemAPI } from '../services/api'

export const useSystemMetrics = (refreshInterval = 30000) => {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const response = await systemAPI.getMetrics()
      setMetrics(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching system metrics:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchMetrics, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [refreshInterval])

  return { metrics, loading, error, refetch: fetchMetrics }
}

export const useSystemStatus = () => {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await systemAPI.getStatus()
        setStatus(response.data)
        setError(null)
      } catch (err) {
        setError(err.message)
        console.error('Error fetching system status:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()
  }, [])

  return { status, loading, error }
}
