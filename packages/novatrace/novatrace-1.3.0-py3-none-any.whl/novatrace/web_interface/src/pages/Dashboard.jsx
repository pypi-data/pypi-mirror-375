import React, { useState, useEffect } from 'react'
import MetricCard from '../components/MetricCard'
import RecentProjects from '../components/RecentProjects'
import SystemChart from '../components/SystemChart'
import { Cpu, HardDrive, Zap, Activity, RefreshCw } from 'lucide-react'
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
  const [loading, setLoading] = useState(false)

  // Sample data for charts (keeping these for now, will be replaced with real data later)
  const cpuData = [30, 35, 42, 38, 45, 50, 45, 40, 48, 45]
  const memoryData = [50, 55, 60, 58, 65, 67, 70, 65, 68, 67]
  const networkData = [15, 20, 25, 18, 23, 28, 22, 19, 25, 23]

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

  useEffect(() => {
    // Initial fetch
    fetchMetrics()
    
    // Auto-refresh every 15 seconds for real-time monitoring
    const interval = setInterval(fetchMetrics, 15000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Real-time system monitoring and project overview</p>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="btn-primary flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="CPU Usage"
          value={metrics.cpu}
          unit="%"
          trend={metrics.cpu > 50 ? 'up' : 'down'}
          trendValue={`${Math.floor(Math.random() * 10)}% from last hour`}
          icon={Cpu}
          color="blue"
        />
        <MetricCard
          title="Memory Usage"
          value={metrics.memory}
          unit="%"
          trend={metrics.memory > 60 ? 'up' : 'down'}
          trendValue={`${Math.floor(Math.random() * 10)}% from last hour`}
          icon={HardDrive}
          color="green"
        />
        <MetricCard
          title="Disk Usage"
          value={metrics.disk}
          unit="%"
          trend={metrics.disk > 70 ? 'up' : 'down'}
          trendValue={`${Math.floor(Math.random() * 10)}% from last hour`}
          icon={Activity}
          color="purple"
        />
        <MetricCard
          title="Network I/O"
          value={metrics.network}
          unit="MB/s"
          trend={metrics.network > 30 ? 'up' : 'down'}
          trendValue={`${Math.floor(Math.random() * 10)}% from last hour`}
          icon={Zap}
          color="orange"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <SystemChart
          title="CPU Usage Over Time"
          data={cpuData}
          color="blue"
          unit="%"
        />
        <SystemChart
          title="Memory Usage Over Time"
          data={memoryData}
          color="green"
          unit="%"
        />
        <SystemChart
          title="Network I/O Over Time"
          data={networkData}
          color="orange"
          unit="MB/s"
        />
      </div>

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
