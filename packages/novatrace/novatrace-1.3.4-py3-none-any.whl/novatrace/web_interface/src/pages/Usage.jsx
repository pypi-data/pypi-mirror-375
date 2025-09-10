import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Hash, Users, Calendar, RefreshCw } from 'lucide-react'
import { projectsAPI } from '../services/api'

const Usage = () => {
  const [usageData, setUsageData] = useState({
    totalTokens: 0,
    projects: [],
    sessions: [],
    users: []
  })
  const [loading, setLoading] = useState(false)
  const [viewBy, setViewBy] = useState('project') // project, session, user, trace
  const [timeRange, setTimeRange] = useState('all') // all, today, week, month

  // Fetch usage data from API
  const fetchUsageData = async () => {
    setLoading(true)
    try {
      // Get all projects first
      const projectsResponse = await projectsAPI.getAll()
      const projectsData = projectsResponse.data

      let totalTokens = 0
      const projectsUsage = []
      const sessionsUsage = {}
      const usersUsage = {}
      const allTraces = []

      // Get detailed data from each project
      for (const project of projectsData.projects || []) {
        try {
          const projectResponse = await projectsAPI.getById(project.id)
          const projectData = projectResponse.data
          
          const traces = projectData.traces || []
          const projectTokens = traces.reduce((sum, trace) => sum + (trace.tokens || 0), 0)
          totalTokens += projectTokens

          // Project usage
          projectsUsage.push({
            id: project.id,
            name: project.name,
            totalTokens: projectTokens,
            inputTokens: traces.reduce((sum, trace) => sum + (trace.input_tokens || 0), 0),
            outputTokens: traces.reduce((sum, trace) => sum + (trace.output_tokens || 0), 0),
            traceCount: traces.length,
            avgTokensPerTrace: traces.length > 0 ? Math.round(projectTokens / traces.length) : 0
          })

          // Collect all traces for further analysis
          traces.forEach(trace => {
            allTraces.push({
              ...trace,
              project_name: project.name,
              project_id: project.id
            })

            // Session usage
            const sessionKey = trace.session_name || trace.session_id || 'No Session'
            if (!sessionsUsage[sessionKey]) {
              sessionsUsage[sessionKey] = {
                name: sessionKey,
                totalTokens: 0,
                inputTokens: 0,
                outputTokens: 0,
                traceCount: 0,
                projects: new Set()
              }
            }
            sessionsUsage[sessionKey].totalTokens += trace.tokens || 0
            sessionsUsage[sessionKey].inputTokens += trace.input_tokens || 0
            sessionsUsage[sessionKey].outputTokens += trace.output_tokens || 0
            sessionsUsage[sessionKey].traceCount += 1
            sessionsUsage[sessionKey].projects.add(project.name)

            // User usage
            const userKey = trace.user_name || trace.user_id || 'Unknown User'
            if (!usersUsage[userKey]) {
              usersUsage[userKey] = {
                name: userKey,
                totalTokens: 0,
                inputTokens: 0,
                outputTokens: 0,
                traceCount: 0,
                projects: new Set()
              }
            }
            usersUsage[userKey].totalTokens += trace.tokens || 0
            usersUsage[userKey].inputTokens += trace.input_tokens || 0
            usersUsage[userKey].outputTokens += trace.output_tokens || 0
            usersUsage[userKey].traceCount += 1
            usersUsage[userKey].projects.add(project.name)
          })

        } catch (error) {
          console.warn(`Failed to fetch usage for project ${project.name}:`, error)
        }
      }

      // Convert objects to arrays and sort
      const sessionsArray = Object.values(sessionsUsage)
        .map(session => ({
          ...session,
          projects: Array.from(session.projects)
        }))
        .sort((a, b) => b.totalTokens - a.totalTokens)

      const usersArray = Object.values(usersUsage)
        .map(user => ({
          ...user,
          projects: Array.from(user.projects)
        }))
        .sort((a, b) => b.totalTokens - a.totalTokens)

      setUsageData({
        totalTokens,
        projects: projectsUsage.sort((a, b) => b.totalTokens - a.totalTokens),
        sessions: sessionsArray,
        users: usersArray,
        traces: allTraces.sort((a, b) => (b.tokens || 0) - (a.tokens || 0))
      })

    } catch (error) {
      console.error('Error fetching usage data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsageData()
  }, [])

  // Format numbers with commas
  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num || 0)
  }

  // Get current data based on view
  const getCurrentData = () => {
    switch (viewBy) {
      case 'project':
        return usageData.projects
      case 'session':
        return usageData.sessions
      case 'user':
        return usageData.users
      case 'trace':
        return usageData.traces.slice(0, 50) // Show top 50 traces
      default:
        return []
    }
  }

  const currentData = getCurrentData()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Token Usage</h1>
          <p className="text-gray-600">Analyze token consumption across projects, sessions, and users</p>
        </div>
        <button
          onClick={fetchUsageData}
          disabled={loading}
          className="btn-primary flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <Hash className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Tokens</h3>
              <p className="text-2xl font-bold text-gray-900">{formatNumber(usageData.totalTokens)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-green-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Active Projects</h3>
              <p className="text-2xl font-bold text-gray-900">{usageData.projects.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-purple-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Users</h3>
              <p className="text-2xl font-bold text-gray-900">{usageData.users.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <Calendar className="w-8 h-8 text-orange-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Sessions</h3>
              <p className="text-2xl font-bold text-gray-900">{usageData.sessions.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">View by</label>
            <select
              value={viewBy}
              onChange={(e) => setViewBy(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="project">Project</option>
              <option value="session">Session</option>
              <option value="user">User</option>
              <option value="trace">Individual Traces</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Usage by {viewBy.charAt(0).toUpperCase() + viewBy.slice(1)}
          </h3>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">Loading usage data...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Input Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Output Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Traces
                  </th>
                  {viewBy !== 'trace' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Tokens/Trace
                    </th>
                  )}
                  {(viewBy === 'session' || viewBy === 'user') && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Projects
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentData.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {viewBy === 'trace' ? (
                          <span className="font-mono">{item.trace_id || `trace_${item.id}`}</span>
                        ) : (
                          item.name
                        )}
                      </div>
                      {viewBy === 'trace' && (
                        <div className="text-sm text-gray-500">{item.project_name}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 font-mono">
                        {formatNumber(item.totalTokens || item.tokens || 0)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 font-mono">
                        {formatNumber(item.inputTokens || item.input_tokens || 0)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 font-mono">
                        {formatNumber(item.outputTokens || item.output_tokens || 0)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {viewBy === 'trace' ? '1' : formatNumber(item.traceCount)}
                      </div>
                    </td>
                    {viewBy !== 'trace' && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {formatNumber(item.avgTokensPerTrace || 0)}
                        </div>
                      </td>
                    )}
                    {(viewBy === 'session' || viewBy === 'user') && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {item.projects ? item.projects.join(', ') : 'N/A'}
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default Usage
