import React, { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, CreditCard, Users, Calendar, RefreshCw } from 'lucide-react'
import { projectsAPI } from '../services/api'

const Cost = () => {
  const [costData, setCostData] = useState({
    totalCost: 0,
    projects: [],
    sessions: [],
    users: []
  })
  const [loading, setLoading] = useState(false)
  const [viewBy, setViewBy] = useState('project') // project, session, user, trace
  const [timeRange, setTimeRange] = useState('all') // all, today, week, month

  // Fetch cost data from API
  const fetchCostData = async () => {
    setLoading(true)
    try {
      // Get all projects first
      const projectsResponse = await projectsAPI.getAll()
      const projectsData = projectsResponse.data

      let totalCost = 0
      const projectsCost = []
      const sessionsCost = {}
      const usersCost = {}
      const allTraces = []

      // Get detailed data from each project
      for (const project of projectsData.projects || []) {
        try {
          const projectResponse = await projectsAPI.getById(project.id)
          const projectData = projectResponse.data
          
          const traces = projectData.traces || []
          const projectCost = traces.reduce((sum, trace) => sum + (trace.cost || 0), 0)
          totalCost += projectCost

          // Project cost
          projectsCost.push({
            id: project.id,
            name: project.name,
            totalCost: projectCost,
            traceCount: traces.length,
            avgCostPerTrace: traces.length > 0 ? projectCost / traces.length : 0,
            maxCostTrace: Math.max(...traces.map(t => t.cost || 0), 0),
            minCostTrace: traces.length > 0 ? Math.min(...traces.map(t => t.cost || 0).filter(c => c > 0)) : 0
          })

          // Collect all traces for further analysis
          traces.forEach(trace => {
            allTraces.push({
              ...trace,
              project_name: project.name,
              project_id: project.id
            })

            // Session cost
            const sessionKey = trace.session_name || trace.session_id || 'No Session'
            if (!sessionsCost[sessionKey]) {
              sessionsCost[sessionKey] = {
                name: sessionKey,
                totalCost: 0,
                traceCount: 0,
                projects: new Set(),
                costs: []
              }
            }
            sessionsCost[sessionKey].totalCost += trace.cost || 0
            sessionsCost[sessionKey].traceCount += 1
            sessionsCost[sessionKey].projects.add(project.name)
            sessionsCost[sessionKey].costs.push(trace.cost || 0)

            // User cost
            const userKey = trace.user_name || trace.user_id || 'Unknown User'
            if (!usersCost[userKey]) {
              usersCost[userKey] = {
                name: userKey,
                totalCost: 0,
                traceCount: 0,
                projects: new Set(),
                costs: []
              }
            }
            usersCost[userKey].totalCost += trace.cost || 0
            usersCost[userKey].traceCount += 1
            usersCost[userKey].projects.add(project.name)
            usersCost[userKey].costs.push(trace.cost || 0)
          })

        } catch (error) {
          console.warn(`Failed to fetch cost for project ${project.name}:`, error)
        }
      }

      // Convert objects to arrays and calculate additional metrics
      const sessionsArray = Object.values(sessionsCost)
        .map(session => ({
          ...session,
          projects: Array.from(session.projects),
          avgCostPerTrace: session.traceCount > 0 ? session.totalCost / session.traceCount : 0,
          maxCostTrace: Math.max(...session.costs, 0),
          minCostTrace: session.costs.length > 0 ? Math.min(...session.costs.filter(c => c > 0)) : 0
        }))
        .sort((a, b) => b.totalCost - a.totalCost)

      const usersArray = Object.values(usersCost)
        .map(user => ({
          ...user,
          projects: Array.from(user.projects),
          avgCostPerTrace: user.traceCount > 0 ? user.totalCost / user.traceCount : 0,
          maxCostTrace: Math.max(...user.costs, 0),
          minCostTrace: user.costs.length > 0 ? Math.min(...user.costs.filter(c => c > 0)) : 0
        }))
        .sort((a, b) => b.totalCost - a.totalCost)

      setCostData({
        totalCost,
        projects: projectsCost.sort((a, b) => b.totalCost - a.totalCost),
        sessions: sessionsArray,
        users: usersArray,
        traces: allTraces.sort((a, b) => (b.cost || 0) - (a.cost || 0))
      })

    } catch (error) {
      console.error('Error fetching cost data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCostData()
  }, [])

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 6
    }).format(amount || 0)
  }

  // Format numbers with commas
  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num || 0)
  }

  // Get current data based on view
  const getCurrentData = () => {
    switch (viewBy) {
      case 'project':
        return costData.projects
      case 'session':
        return costData.sessions
      case 'user':
        return costData.users
      case 'trace':
        return costData.traces.slice(0, 50) // Show top 50 traces
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
          <h1 className="text-2xl font-bold text-gray-900">Cost Analysis</h1>
          <p className="text-gray-600">Monitor and analyze costs across projects, sessions, and users</p>
        </div>
        <button
          onClick={fetchCostData}
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
            <DollarSign className="w-8 h-8 text-green-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Cost</h3>
              <p className="text-2xl font-bold text-gray-900">{formatCurrency(costData.totalCost)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <CreditCard className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Avg Cost/Project</h3>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(costData.projects.length > 0 ? costData.totalCost / costData.projects.length : 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-purple-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Active Users</h3>
              <p className="text-2xl font-bold text-gray-900">{costData.users.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-orange-500" />
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Highest Session</h3>
              <p className="text-2xl font-bold text-gray-900">
                {costData.sessions.length > 0 ? formatCurrency(costData.sessions[0]?.totalCost || 0) : formatCurrency(0)}
              </p>
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
            Costs by {viewBy.charAt(0).toUpperCase() + viewBy.slice(1)}
          </h3>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">Loading cost data...</p>
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
                    Total Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Traces
                  </th>
                  {viewBy !== 'trace' && (
                    <>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Cost/Trace
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Max Cost
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Min Cost
                      </th>
                    </>
                  )}
                  {viewBy === 'trace' && (
                    <>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tokens
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Model
                      </th>
                    </>
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
                        {formatCurrency(item.totalCost || item.cost || 0)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {viewBy === 'trace' ? '1' : formatNumber(item.traceCount)}
                      </div>
                    </td>
                    {viewBy !== 'trace' && (
                      <>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 font-mono">
                            {formatCurrency(item.avgCostPerTrace || 0)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 font-mono">
                            {formatCurrency(item.maxCostTrace || 0)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 font-mono">
                            {formatCurrency(item.minCostTrace || 0)}
                          </div>
                        </td>
                      </>
                    )}
                    {viewBy === 'trace' && (
                      <>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 font-mono">
                            {formatNumber(item.tokens || 0)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {item.model_name || 'N/A'}
                          </div>
                          {item.model_provider && (
                            <div className="text-xs text-gray-500">{item.model_provider}</div>
                          )}
                        </td>
                      </>
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

export default Cost
