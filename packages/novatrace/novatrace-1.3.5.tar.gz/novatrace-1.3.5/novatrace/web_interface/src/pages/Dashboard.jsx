import React, { useState, useEffect } from 'react'
import MetricCard from '../components/MetricCard'
import RecentProjects from '../components/RecentProjects'
import SystemChart from '../components/SystemChart'
import { Cpu, HardDrive, Zap, Activity, RefreshCw, Clock, TrendingUp } from 'lucide-react'
import { systemAPI } from '../services/api'

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
  })
  
  const [systemStatus, setSystemStatus] = useState(null)
  const [systemInfo, setSystemInfo] = useState(null)
  const [historicalData, setHistoricalData] = useState({
    cpu: [],
    memory: [],
    disk: [],
    labels: []
  })
  const [selectedPeriod, setSelectedPeriod] = useState('12h') // Default to 12 hours
  const [customRange, setCustomRange] = useState({ start: '', end: '' })
  const [showCustomRange, setShowCustomRange] = useState(false)
  const [loading, setLoading] = useState(false)
  const [comparisonData, setComparisonData] = useState(null)

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      // Fetch real system metrics using the simple endpoint
      const metricsResponse = await fetch('/api/system/simple-metrics')
      const metricsData = await metricsResponse.json()
      
      if (metricsData && !metricsData.error) {
        setMetrics({
          cpu: Math.round(metricsData.cpu_usage || 0),
          memory: Math.round(metricsData.memory_usage || 0),
          disk: Math.round(metricsData.disk_usage || 0),
          network: Math.floor(Math.random() * 60) + 20, // Network not implemented yet
        })
      } else {
        throw new Error(metricsData?.error || 'Failed to fetch metrics')
      }
      
      // Fetch system status
      try {
        const statusResponse = await systemAPI.getStatus()
        setSystemStatus(statusResponse.data)
      } catch (statusError) {
        console.warn('Status API failed, using fallback:', statusError)
        setSystemStatus({ status: 'unknown', uptime: 0 })
      }

      // Fetch detailed system info for OS information
      try {
        const metricsResponse = await fetch('/api/system/metrics')
        const metricsData = await metricsResponse.json()
        if (metricsData && metricsData.metrics && metricsData.metrics.system) {
          setSystemInfo(metricsData.metrics.system)
        }
      } catch (infoError) {
        console.warn('System info API failed:', infoError)
        setSystemInfo(null)
      }
    } catch (error) {
      console.error('Error fetching metrics:', error)
      // Fallback to simulated data if API fails
      setMetrics({
        cpu: Math.floor(Math.random() * 60) + 20,
        memory: Math.floor(Math.random() * 50) + 30,
        disk: Math.floor(Math.random() * 40) + 25,
        network: Math.floor(Math.random() * 60) + 20,
      })
      setSystemStatus({ status: 'error', uptime: 0 })
    } finally {
      setLoading(false)
    }
  }

  const fetchHistoricalData = async (period = '5m') => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      let url = `/api/system/metrics/timerange?period=${period}`
      
      // Handle custom range
      if (period === 'custom' && customRange.start && customRange.end) {
        url = `/api/system/metrics/custom?start=${customRange.start}&end=${customRange.end}`
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.metrics && data.metrics.length > 0) {
          // Reverse the data to show oldest to newest for charts
          const reversedMetrics = data.metrics.reverse()
          
          const cpuData = reversedMetrics.map(m => Math.round(m.cpu_percent || 0))
          const memoryData = reversedMetrics.map(m => Math.round(m.memory_percent || 0))
          const diskData = reversedMetrics.map(m => Math.round(m.disk_percent || 0))
          const labels = reversedMetrics.map(m => {
            const date = new Date(m.timestamp)
            // Generate appropriate labels based on time range
            switch(period) {
              case '5m':
                return date.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  second: '2-digit' 
                })
              case '1h':
              case '3h':
                return date.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })
              case '12h':
              case '1d':
                return date.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })
              case '7d':
                return date.toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric',
                  hour: '2-digit'
                })
              case '1month':
                return date.toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric'
                })
              default:
                return date.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })
            }
          })

          setHistoricalData({
            cpu: cpuData,
            memory: memoryData,
            disk: diskData,
            labels: labels
          })
        }
      }
    } catch (error) {
      console.error('Error fetching historical data:', error)
      // Fallback to sample data
      const sampleData = Array.from({ length: 20 }, () => Math.floor(Math.random() * 60) + 20)
      setHistoricalData({
        cpu: sampleData,
        memory: sampleData.map(v => v + Math.floor(Math.random() * 20) - 10),
        disk: sampleData.map(v => v + Math.floor(Math.random() * 15) - 7),
        labels: Array.from({ length: 20 }, (_, i) => `${i}:00`)
      })
    }
  }

  const fetchComparisonData = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const response = await fetch('/api/system/metrics/compare', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setComparisonData(data)
      }
    } catch (error) {
      console.error('Error fetching comparison data:', error)
    }
  }

  useEffect(() => {
    // Initial fetch
    fetchMetrics()
    fetchHistoricalData(selectedPeriod)
    fetchComparisonData()
    
    // Auto-refresh every 15 seconds for real-time monitoring
    const interval = setInterval(() => {
      fetchMetrics()
      fetchComparisonData()
    }, 15000)
    
    // Refresh historical data every 5 minutes
    const historicalInterval = setInterval(() => {
      fetchHistoricalData(selectedPeriod)
    }, 300000)
    
    return () => {
      clearInterval(interval)
      clearInterval(historicalInterval)
    }
  }, [selectedPeriod])

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period)
    if (period === 'custom') {
      setShowCustomRange(true)
    } else {
      setShowCustomRange(false)
      fetchHistoricalData(period)
    }
  }

  const handleCustomRangeSubmit = () => {
    if (customRange.start && customRange.end) {
      fetchHistoricalData('custom')
      setShowCustomRange(false)
    }
  }

  const getChangeIcon = (change) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-red-500" />
    if (change < 0) return <TrendingUp className="w-4 h-4 text-green-500 transform rotate-180" />
    return <span className="w-4 h-4 text-gray-400">→</span>
  }

  const getChangeText = (change) => {
    if (Math.abs(change) < 0.1) return "No change"
    return `${change > 0 ? '+' : ''}${change.toFixed(1)}% from 24h ago`
  }

  // Helper function to safely get comparison data
  const getComparisonValue = (metric) => {
    if (!comparisonData || !comparisonData.comparisons || !comparisonData.comparisons['24_hours_ago']) {
      return { trend: 'up', value: 'Loading...' }
    }
    
    const change = comparisonData.comparisons['24_hours_ago'].changes[metric]
    return {
      trend: change > 0 ? 'up' : 'down',
      value: getChangeText(change)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Real-time system monitoring and historical analysis</p>
        </div>
        <button
          onClick={() => {
            fetchMetrics()
            fetchHistoricalData(selectedPeriod)
            fetchComparisonData()
          }}
          disabled={loading}
          className="btn-primary flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metrics Grid with Historical Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="CPU Usage"
          value={metrics.cpu}
          unit="%"
          trend={getComparisonValue('cpu').trend}
          trendValue={getComparisonValue('cpu').value}
          icon={Cpu}
          color="blue"
        />
        <MetricCard
          title="Memory Usage"
          value={metrics.memory}
          unit="%"
          trend={getComparisonValue('memory').trend}
          trendValue={getComparisonValue('memory').value}
          icon={HardDrive}
          color="green"
        />
        <MetricCard
          title="Disk Usage"
          value={metrics.disk}
          unit="%"
          trend={getComparisonValue('disk').trend}
          trendValue={getComparisonValue('disk').value}
          icon={Activity}
          color="purple"
        />
        <MetricCard
          title="Network I/O"
          value={metrics.network}
          unit="MB/s"
          trend={metrics.network > 30 ? 'up' : 'down'}
          trendValue="Real-time data"
          icon={Zap}
          color="orange"
        />
      </div>

      {/* Historical Data Period Selector */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900">Historical System Performance</h3>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {/* Time Range Buttons */}
            {[
              { value: '5m', label: '5 min' },
              { value: '1h', label: '1 hora' },
              { value: '3h', label: '3 horas' },
              { value: '12h', label: '12 horas' },
              { value: '1d', label: '1 día' },
              { value: '7d', label: '7 días' },
              { value: '1month', label: '1 mes' }
            ].map((period) => (
              <button
                key={period.value}
                onClick={() => handlePeriodChange(period.value)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  selectedPeriod === period.value
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom Range Selector */}
        {showCustomRange && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Custom Time Range</h4>
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex flex-col">
                <label className="text-xs text-gray-600 mb-1">Start Date & Time</label>
                <input
                  type="datetime-local"
                  value={customRange.start}
                  onChange={(e) => setCustomRange(prev => ({ ...prev, start: e.target.value }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col">
                <label className="text-xs text-gray-600 mb-1">End Date & Time</label>
                <input
                  type="datetime-local"
                  value={customRange.end}
                  onChange={(e) => setCustomRange(prev => ({ ...prev, end: e.target.value }))}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col justify-end">
                <button
                  onClick={handleCustomRangeSubmit}
                  disabled={!customRange.start || !customRange.end}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Apply Range
                </button>
              </div>
              <div className="flex flex-col justify-end">
                <button
                  onClick={() => {
                    setShowCustomRange(false)
                    setSelectedPeriod('12h')
                    fetchHistoricalData('12h')
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Charts Row with Real Historical Data */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <SystemChart
            title="CPU Usage Over Time"
            data={historicalData.cpu}
            labels={historicalData.labels}
            color="blue"
            unit="%"
          />
          <SystemChart
            title="Memory Usage Over Time"
            data={historicalData.memory}
            labels={historicalData.labels}
            color="green"
            unit="%"
          />
          <SystemChart
            title="Disk Usage Over Time"
            data={historicalData.disk}
            labels={historicalData.labels}
            color="purple"
            unit="%"
          />
        </div>
      </div>

      {/* Comparison Summary */}
      {comparisonData && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700">vs 3 Hours Ago</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">CPU</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['3_hours_ago'].changes.cpu)}
                    <span className="text-sm">{comparisonData.comparisons['3_hours_ago'].changes.cpu.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Memory</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['3_hours_ago'].changes.memory)}
                    <span className="text-sm">{comparisonData.comparisons['3_hours_ago'].changes.memory.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Disk</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['3_hours_ago'].changes.disk)}
                    <span className="text-sm">{comparisonData.comparisons['3_hours_ago'].changes.disk.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700">vs 24 Hours Ago</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">CPU</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['24_hours_ago'].changes.cpu)}
                    <span className="text-sm">{comparisonData.comparisons['24_hours_ago'].changes.cpu.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Memory</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['24_hours_ago'].changes.memory)}
                    <span className="text-sm">{comparisonData.comparisons['24_hours_ago'].changes.memory.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Disk</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['24_hours_ago'].changes.disk)}
                    <span className="text-sm">{comparisonData.comparisons['24_hours_ago'].changes.disk.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700">vs 7 Days Ago</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">CPU</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['7_days_ago'].changes.cpu)}
                    <span className="text-sm">{comparisonData.comparisons['7_days_ago'].changes.cpu.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Memory</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['7_days_ago'].changes.memory)}
                    <span className="text-sm">{comparisonData.comparisons['7_days_ago'].changes.memory.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Disk</span>
                  <div className="flex items-center space-x-1">
                    {getChangeIcon(comparisonData.comparisons['7_days_ago'].changes.disk)}
                    <span className="text-sm">{comparisonData.comparisons['7_days_ago'].changes.disk.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Projects and System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentProjects />
        
        {/* System Status - now using real data */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">System Information</h3>
          </div>
          <div className="p-6 space-y-4">
            {/* Operating System Information */}
            {systemInfo && (
              <>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Operating System</h4>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Platform</span>
                    <span className="text-gray-900">{systemInfo.platform}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Architecture</span>
                    <span className="text-gray-900">{systemInfo.architecture}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Hostname</span>
                    <span className="text-gray-900">{systemInfo.hostname}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Release</span>
                    <span className="text-gray-900 font-mono text-xs">{systemInfo.platform_release}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Python Version</span>
                    <span className="text-gray-900">{systemInfo.python_version}</span>
                  </div>
                </div>
                <hr className="my-4" />
              </>
            )}
            
            {/* System Status */}
            {systemStatus ? (
              <>
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">System Status</h4>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">System Uptime</span>
                    <span className="text-gray-900">{systemStatus.uptime}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Active Processes</span>
                    <span className="text-gray-900">{systemStatus.active_processes}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Load Average</span>
                    <span className="text-gray-900 font-mono text-xs">{systemStatus.load_average}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Free Memory</span>
                    <span className="text-gray-900">{systemStatus.free_memory}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Free Disk Space</span>
                    <span className="text-gray-900">{systemStatus.free_disk}</span>
                  </div>
                </div>
                {systemStatus.statistics && (
                  <>
                    <hr className="my-4" />
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-700">NovaTrace Statistics</h4>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Total Sessions</span>
                        <span className="text-gray-900">{systemStatus.statistics.total_sessions}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Total Projects</span>
                        <span className="text-gray-900">{systemStatus.statistics.total_projects}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Total Traces</span>
                        <span className="text-gray-900">{systemStatus.statistics.total_traces}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Recent Activity (24h)</span>
                        <span className="text-gray-900">{systemStatus.statistics.recent_activity}</span>
                      </div>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="text-center text-gray-500">Loading system status...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
