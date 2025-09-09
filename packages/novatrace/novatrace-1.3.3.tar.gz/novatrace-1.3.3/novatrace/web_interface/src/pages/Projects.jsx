import React, { useState, useEffect } from 'react'
import { Search, Filter, Plus, MoreVertical, Play, Pause, Square, Folder } from 'lucide-react'
import { projectsAPI } from '../services/api'

const Projects = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [filter, setFilter] = useState('all')
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true)
        const response = await projectsAPI.getAll()
        const projectsData = response.data.projects.map(project => ({
          id: project.id,
          name: project.name,
          description: project.description || `Project with ${project.metrics.total_traces} traces and $${project.metrics.total_cost.toFixed(4)} total cost`,
          status: project.status,
          type: project.type,
          created: project.created,
          lastModified: project.lastModified,
          cpu: Math.min(project.metrics.recent_activity * 5, 100), // Convert activity to CPU %
          memory: Math.min(project.metrics.total_traces * 2, 1000), // Convert traces to memory MB
          metrics: project.metrics
        }))
        setProjects(projectsData)
        setError(null)
      } catch (err) {
        console.error('Error fetching projects:', err)
        setError(err.message)
        // Fallback to empty array
        setProjects([])
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchProjects, 30000)
    return () => clearInterval(interval)
  }, [])

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filter === 'all' || project.status === filter
    return matchesSearch && matchesFilter
  })

  const getStatusBadge = (status) => {
    const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full'
    switch (status) {
      case 'running':
      case 'active':
        return `${baseClasses} text-green-700 bg-green-100`
      case 'stopped':
      case 'inactive':
        return `${baseClasses} text-red-700 bg-red-100`
      case 'idle':
        return `${baseClasses} text-yellow-700 bg-yellow-100`
      default:
        return `${baseClasses} text-gray-700 bg-gray-100`
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
      case 'active':
        return <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      case 'stopped':
      case 'inactive':
        return <div className="w-2 h-2 bg-red-500 rounded-full" />
      case 'idle':
        return <div className="w-2 h-2 bg-yellow-500 rounded-full" />
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />
    }
  }

  const getRelativeTime = (isoString) => {
    try {
      const date = new Date(isoString)
      const now = new Date()
      const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      
      if (diffInDays === 0) return 'Today'
      if (diffInDays === 1) return 'Yesterday'
      if (diffInDays < 7) return `${diffInDays} days ago`
      if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`
      return date.toLocaleDateString()
    } catch {
      return 'Unknown'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
            <p className="text-gray-600">Manage and monitor your active projects</p>
          </div>
        </div>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading projects...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600">Manage and monitor your active projects</p>
          {error && (
            <p className="text-sm text-red-600 mt-1">
              ⚠️ API connection issue - showing cached data
            </p>
          )}
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="running">Running</option>
            <option value="active">Active</option>
            <option value="idle">Idle</option>
            <option value="stopped">Stopped</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <div key={project.id} className="bg-white rounded-lg shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2 flex-1 min-w-0">
                {getStatusIcon(project.status)}
                <h3 className="text-lg font-medium text-gray-900 truncate">{project.name}</h3>
              </div>
              <button className="text-gray-400 hover:text-gray-600 ml-2">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>

            <p className="text-gray-600 text-sm mb-4 line-clamp-2">{project.description}</p>

            <div className="flex items-center justify-between mb-4">
              <span className={getStatusBadge(project.status)}>{project.status}</span>
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {project.type}
              </span>
            </div>

            {/* Real Metrics */}
            {project.metrics && (
              <div className="space-y-2 mb-4 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Traces</span>
                  <span className="text-gray-900 font-medium">{project.metrics.total_traces}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Cost</span>
                  <span className="text-gray-900 font-medium">${project.metrics.total_cost.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tokens</span>
                  <span className="text-gray-900 font-medium">{project.metrics.total_tokens.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Duration</span>
                  <span className="text-gray-900 font-medium">{project.metrics.avg_duration_ms.toFixed(0)}ms</span>
                </div>
              </div>
            )}

            {/* Resource Usage */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Activity</span>
                <span className="text-gray-900">{project.cpu}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-blue-600 h-1.5 rounded-full"
                  style={{ width: `${Math.min(project.cpu, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Data</span>
                <span className="text-gray-900">{project.memory} MB</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-green-600 h-1.5 rounded-full"
                  style={{ width: `${Math.min(project.memory / 10, 100)}%` }}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">
                Modified {getRelativeTime(project.lastModified)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {filteredProjects.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Folder className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-600">
            {projects.length === 0 ? (
              <>
                No projects created yet.{' '}
              </>
            ) : (
              'Try adjusting your search or filter criteria'
            )}
          </p>
        </div>
      )}
    </div>
  )
}

export default Projects
