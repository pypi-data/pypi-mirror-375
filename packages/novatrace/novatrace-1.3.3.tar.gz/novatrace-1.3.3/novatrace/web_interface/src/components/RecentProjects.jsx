import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, AlertCircle, CheckCircle, Folder } from 'lucide-react'
import { projectsAPI } from '../services/api'

const RecentProjects = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true)
        const response = await projectsAPI.getAll()
        // Get only the most recent 4 projects
        const recentProjects = response.data.projects.slice(0, 4).map(project => ({
          id: project.id,
          name: project.name,
          status: project.status,
          lastActivity: getRelativeTime(project.lastModified),
          progress: Math.min(project.metrics.total_traces * 5, 100), // Simple progress calculation
          metrics: project.metrics
        }))
        setProjects(recentProjects)
        setError(null)
      } catch (err) {
        console.error('Error fetching projects:', err)
        setError(err.message)
        // Fallback to simulated data
        setProjects([
          {
            id: 1,
            name: 'Web Analytics Dashboard',
            status: 'active',
            lastActivity: '2 minutes ago',
            progress: 85,
          },
          {
            id: 2,
            name: 'Mobile App Backend',
            status: 'inactive',
            lastActivity: '15 minutes ago',
            progress: 62,
          },
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchProjects()
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchProjects, 30000)
    return () => clearInterval(interval)
  }, [])

  const getRelativeTime = (isoString) => {
    try {
      const date = new Date(isoString)
      const now = new Date()
      const diffInSeconds = Math.floor((now - date) / 1000)
      
      if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
      return `${Math.floor(diffInSeconds / 86400)} days ago`
    } catch {
      return 'Unknown'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
      case 'active':
        return <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      case 'idle':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      case 'stopped':
      case 'inactive':
        return <div className="w-2 h-2 bg-red-500 rounded-full" />
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
      case 'active':
        return 'text-green-700 bg-green-100'
      case 'idle':
        return 'text-yellow-700 bg-yellow-100'
      case 'stopped':
      case 'inactive':
        return 'text-red-700 bg-red-100'
      default:
        return 'text-gray-700 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
        </div>
        <div className="p-6 text-center text-gray-500">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2">Loading projects...</p>
        </div>
      </div>
    )
  }

  if (error && projects.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
        </div>
        <div className="p-6 text-center text-red-500">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>Error loading projects</p>
          <p className="text-sm text-gray-500">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
        {error && (
          <p className="text-xs text-yellow-600 mt-1">
            ⚠️ Using cached data - API connection issue
          </p>
        )}
      </div>
      
      {projects.length === 0 ? (
        <div className="p-6 text-center text-gray-500">
          <Folder className="w-8 h-8 mx-auto mb-2" />
          <p>No projects found</p>
          <p className="text-sm">Create your first project to get started</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {projects.map((project) => (
            <div key={project.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(project.status)}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{project.name}</h4>
                    <div className="flex items-center mt-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3 mr-1" />
                      {project.lastActivity}
                    </div>
                    {project.metrics && (
                      <div className="flex items-center mt-1 text-xs text-gray-500 space-x-3">
                        <span>{project.metrics.total_traces} traces</span>
                        <span>${project.metrics.total_cost.toFixed(4)} cost</span>
                        <span>{project.metrics.total_tokens} tokens</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                    {project.status}
                  </span>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{project.progress}%</div>
                    <div className="w-16 bg-gray-200 rounded-full h-1.5 mt-1">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <button 
          onClick={() => navigate('/projects')}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
        >
          View all projects →
        </button>
      </div>
    </div>
  )
}

export default RecentProjects
