import React, { useState, useEffect } from 'react'
import { Search, Filter, Eye, Database, Copy } from 'lucide-react'
import { projectsAPI } from '../services/api'
import JSONFormatter, { extractJSONContent, parseComplexStructure } from '../components/JSONFormatter'

const Traces = () => {
  const [traces, setTraces] = useState([])
  const [filteredTraces, setFilteredTraces] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedTrace, setSelectedTrace] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState('all') // all, project, session, user
  const [groupBy, setGroupBy] = useState('none') // none, project, session, user
  const [projects, setProjects] = useState([])
  const [copiedField, setCopiedField] = useState(null) // Track which field was copied
  const [viewMode, setViewMode] = useState({}) // Track view mode for each field (json vs original)

  // Fetch traces from API
  const fetchTraces = async () => {
    setLoading(true)
    try {
      // Get all projects first
      const projectsResponse = await projectsAPI.getAll()
      const projectsData = projectsResponse.data
      setProjects(projectsData.projects || [])

      // Get all traces from all projects
      const allTraces = []
      for (const project of projectsData.projects || []) {
        try {
          const projectResponse = await projectsAPI.getById(project.id)
          const projectData = projectResponse.data
          
          // Add project info to each trace
          const tracesWithProject = (projectData.traces || []).map(trace => ({
            ...trace,
            project_name: project.name,
            project_id: project.id
          }))
          
          allTraces.push(...tracesWithProject)
        } catch (error) {
          console.warn(`Failed to fetch traces for project ${project.name}:`, error)
        }
      }

      setTraces(allTraces)
      setFilteredTraces(allTraces)
    } catch (error) {
      console.error('Error fetching traces:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter and search traces
  useEffect(() => {
    let filtered = traces

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(trace => 
        trace.trace_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        trace.project_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        trace.session_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        trace.user_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(trace.input_data || {}).toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(trace.output_data || {}).toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Apply project filter
    if (filterBy !== 'all') {
      if (filterBy.startsWith('project_')) {
        const projectId = parseInt(filterBy.split('_')[1])
        filtered = filtered.filter(trace => trace.project_id === projectId)
      }
    }

    setFilteredTraces(filtered)
  }, [traces, searchTerm, filterBy])

  // Group traces
  const groupedTraces = () => {
    if (groupBy === 'none') {
      return { 'All Traces': filteredTraces }
    }

    return filteredTraces.reduce((groups, trace) => {
      let key
      switch (groupBy) {
        case 'project':
          key = trace.project_name || 'Unknown Project'
          break
        case 'session':
          key = trace.session_name || trace.session_id || 'No Session'
          break
        case 'user':
          key = trace.user_id || 'Unknown User'
          break
        default:
          key = 'All Traces'
      }

      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(trace)
      return groups
    }, {})
  }

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown'
    try {
      return new Date(timestamp).toLocaleString()
    } catch (error) {
      return 'Invalid date'
    }
  }

  // Copy to clipboard function
  const copyToClipboard = async (text, fieldName) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedField(fieldName)
      // Reset the copied state after 2 seconds
      setTimeout(() => setCopiedField(null), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = text
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      setCopiedField(fieldName)
      setTimeout(() => setCopiedField(null), 2000)
    }
  }

  useEffect(() => {
    fetchTraces()
  }, [])

  const grouped = groupedTraces()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Traces</h1>
          <p className="text-gray-600">View and analyze all traces across projects</p>
        </div>
        <div className="text-sm text-gray-500">
          Total: {filteredTraces.length} traces
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search traces..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter by Project */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Projects</option>
              {projects.map(project => (
                <option key={project.id} value={`project_${project.id}`}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>

          {/* Group by */}
          <div className="relative">
            <Database className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <select
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="none">No Grouping</option>
              <option value="project">Group by Project</option>
              <option value="session">Group by Session</option>
              <option value="user">Group by User</option>
            </select>
          </div>

          {/* Refresh button */}
          <button
            onClick={fetchTraces}
            disabled={loading}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <Database className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Traces Table */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8">
            <Database className="w-8 h-8 animate-spin mx-auto text-gray-400 mb-2" />
            <p className="text-gray-500">Loading traces...</p>
          </div>
        ) : (
          Object.entries(grouped).map(([groupName, groupTraces]) => (
            <div key={groupName} className="bg-white rounded-lg shadow-md border border-gray-200">
              {groupBy !== 'none' && (
                <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
                  <h3 className="text-lg font-medium text-gray-900">{groupName}</h3>
                  <p className="text-sm text-gray-600">{groupTraces.length} traces</p>
                </div>
              )}
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 table-fixed w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                        ID
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-28">
                        Project
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                        Session
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
                        User
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                        Timestamp
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                        Duration
                      </th>
                      <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {groupTraces.map((trace) => (
                      <tr key={trace.id} className="hover:bg-gray-50">
                        <td className="px-3 py-4 whitespace-nowrap w-20 text-center">
                          <span className="text-sm font-mono text-gray-900">
                            {trace.id}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-28 text-center">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 truncate max-w-full">
                            {trace.project_name}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-32 text-center truncate">
                          <span className="text-xs text-gray-900 truncate">
                            {trace.session_name || trace.session_id || 'No session'}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-24 text-center truncate">
                          <span className="text-xs text-gray-900 truncate">
                            {trace.user_external_name || trace.user_id || 'Unknown'}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-32 text-center">
                          <span className="text-xs text-gray-900 truncate">
                            {new Date(trace.timestamp || trace.created_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-20 text-center">
                          <span className="text-xs text-gray-900">
                            {trace.duration_ms ? `${(trace.duration_ms / 1000).toFixed(2)}s` : 'N/A'}
                          </span>
                        </td>
                        <td className="px-3 py-4 whitespace-nowrap w-20 text-center">
                          <button
                            onClick={() => setSelectedTrace(trace)}
                            className="inline-flex items-center px-2 py-1 border border-transparent text-xs leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          >
                            <Eye className="w-3 h-3 mr-1" />
                            Ver
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Trace Detail Modal */}
      {selectedTrace && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedTrace(null)}
        >
          <div 
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  Trace Details: {selectedTrace.trace_id || selectedTrace.id}
                </h3>
                <button
                  onClick={() => setSelectedTrace(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="space-y-6">
                {/* Metadata Section - Full Width */}
                <div className="space-y-4">
                  <h4 className="text-lg font-medium text-gray-900">Metadata</h4>
                  <div className="bg-gray-50 rounded-md p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div><strong>Project:</strong> {selectedTrace.project_name}</div>
                    <div><strong>Session:</strong> {selectedTrace.session_name || selectedTrace.session_id || 'N/A'}</div>
                    <div><strong>User ID:</strong> {selectedTrace.user_id || 'N/A'}</div>
                    <div><strong>User Name:</strong> {selectedTrace.user_external_name || 'N/A'}</div>
                    <div><strong>Model Provider:</strong> {selectedTrace.model_provider || 'N/A'}</div>
                    <div><strong>Model Name:</strong> {selectedTrace.model_name || 'N/A'}</div>
                    <div><strong>Timestamp:</strong> {formatTimestamp(selectedTrace.timestamp)}</div>
                    <div><strong>Duration:</strong> {selectedTrace.duration_ms ? `${(selectedTrace.duration_ms / 1000).toFixed(2)}s` : 'N/A'}</div>
                    <div><strong>Type:</strong> {selectedTrace.type || 'N/A'}</div>
                    {selectedTrace.call_cost && <div><strong>Cost:</strong> ${selectedTrace.call_cost}</div>}
                    {(selectedTrace.input_tokens || selectedTrace.output_tokens) && (
                      <div><strong>Tokens:</strong> {(selectedTrace.input_tokens || 0) + (selectedTrace.output_tokens || 0)} ({selectedTrace.input_tokens || 0} in, {selectedTrace.output_tokens || 0} out)</div>
                    )}
                    <div><strong>Status:</strong> {selectedTrace.status || 'Completed'}</div>
                  </div>
                </div>

                {/* Input and Output Data - Two Columns */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Input Data - Siempre formateado legible */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-medium text-gray-900">Input Data</h4>
                      <button
                        onClick={() => {
                          const formattedInput = (() => {
                            try {
                              // Si es string, intentar parsearlo primero
                              if (typeof selectedTrace.input_data === 'string') {
                                const parsed = JSON.parse(selectedTrace.input_data)
                                return JSON.stringify(parsed, null, 2)
                              }
                              // Si ya es objeto, formatearlo directamente
                              return JSON.stringify(selectedTrace.input_data, null, 2)
                            } catch (e) {
                              // Si falla el parsing, devolver como string
                              return selectedTrace.input_data
                            }
                          })()
                          copyToClipboard(formattedInput, 'input')
                        }}
                        className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md transition-colors ${
                          copiedField === 'input' 
                            ? 'text-green-700 bg-green-100 border border-green-300' 
                            : 'text-gray-600 bg-gray-100 hover:bg-gray-200 border border-gray-300'
                        }`}
                        title="Copy input data to clipboard"
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        {copiedField === 'input' ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      <div className="bg-gray-50 rounded-md p-4">
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
                          {(() => {
                            try {
                              // Si es string, intentar parsearlo y formatearlo
                              if (typeof selectedTrace.input_data === 'string') {
                                const parsed = JSON.parse(selectedTrace.input_data)
                                return JSON.stringify(parsed, null, 2)
                              }
                              // Si ya es objeto, formatearlo directamente
                              return JSON.stringify(selectedTrace.input_data, null, 2)
                            } catch (e) {
                              // Si falla el parsing, mostrar como string
                              return selectedTrace.input_data
                            }
                          })()}
                        </pre>
                      </div>
                    </div>
                  </div>

                  {/* Output Data - Original y JSON (Smart View) */}
                  <div className="space-y-4">
                    {(() => {
                      const currentView = viewMode['output'] || 'original'
                      
                      const extractedContent = extractJSONContent(selectedTrace.output_data)
                      
                      const displayContent = currentView === 'json'
                        ? (extractedContent || 'ERROR: Could not parse - ' + JSON.stringify(selectedTrace.output_data, null, 2))
                        : JSON.stringify(selectedTrace.output_data, null, 2)
                      
                      // Function to render JSON with proper formatting
                      const renderFormattedContent = (content) => {
                        if (currentView === 'json') {
                          try {
                            // First check if we have extracted content from Message() parsing
                            if (extractedContent) {
                              const parsed = typeof extractedContent === 'string' 
                                ? JSON.parse(extractedContent) 
                                : extractedContent
                              
                              // Check if this is a message structure with content array
                              if (parsed.content && Array.isArray(parsed.content)) {
                                // Create a copy of the parsed structure to modify
                                const structureToShow = JSON.parse(JSON.stringify(parsed))
                                
                                // Look for text content that might be JSON and parse it
                                structureToShow.content = structureToShow.content.map(item => {
                                  if (item.type === 'text' && item.text) {
                                    try {
                                      // Try to parse the text content as JSON
                                      const innerJSON = JSON.parse(item.text)
                                      
                                      // Replace the string with the parsed object
                                      return {
                                        ...item,
                                        text: innerJSON  // This will be an object, not a string
                                      }
                                    } catch (innerParseError) {
                                      // If text is not JSON, keep it as is
                                      return item
                                    }
                                  }
                                  return item
                                })
                                
                                // Return the full structure with parsed text content
                                return (
                                  <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                    {JSON.stringify(structureToShow, null, 2)}
                                  </pre>
                                )
                              }
                              
                              // Default: show the parsed structure
                              return (
                                <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                  {JSON.stringify(parsed, null, 2)}
                                </pre>
                              )
                            }
                            
                            // If no extracted content, try to parse the original output_data directly
                            let dataToFormat = selectedTrace.output_data
                            
                            // If it's already an object, format it
                            if (typeof dataToFormat === 'object' && dataToFormat !== null) {
                              return (
                                <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                  {JSON.stringify(dataToFormat, null, 2)}
                                </pre>
                              )
                            }
                            
                            // If it's a string, try to parse it as JSON
                            if (typeof dataToFormat === 'string') {
                              try {
                                const parsed = JSON.parse(dataToFormat)
                                return (
                                  <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                    {JSON.stringify(parsed, null, 2)}
                                  </pre>
                                )
                              } catch (parseError) {
                                // If it's not valid JSON, show as formatted text
                                return (
                                  <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                    {dataToFormat}
                                  </pre>
                                )
                              }
                            }
                            
                            // Fallback
                            return (
                              <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                {JSON.stringify(dataToFormat, null, 2)}
                              </pre>
                            )
                            
                          } catch (e) {
                            // If anything fails, show the display content
                            return (
                              <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                                {displayContent}
                              </pre>
                            )
                          }
                        } else {
                          // Original view
                          return (
                            <pre className="whitespace-pre-wrap break-words text-sm text-gray-800 font-mono leading-relaxed">
                              {displayContent}
                            </pre>
                          )
                        }
                      }
                      
                      return (
                        <>
                          <div className="flex items-center justify-between">
                            <h4 className="text-lg font-medium text-gray-900">Output Data</h4>
                            <div className="flex items-center space-x-2">
                              <div className="flex rounded-md border border-gray-300">
                                <button
                                  onClick={() => setViewMode(prev => ({ ...prev, output: 'original' }))}
                                  className={`px-2 py-1 text-xs font-medium rounded-l-md transition-colors ${
                                    currentView === 'original'
                                      ? 'bg-blue-100 text-blue-700 border-blue-300'
                                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                                  }`}
                                >
                                  Original
                                </button>
                                <button
                                  onClick={() => setViewMode(prev => ({ ...prev, output: 'json' }))}
                                  className={`px-2 py-1 text-xs font-medium rounded-r-md border-l transition-colors ${
                                    currentView === 'json'
                                      ? 'bg-green-100 text-green-700 border-green-300'
                                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                                  }`}
                                >
                                  JSON
                                </button>
                              </div>
                              <button
                                onClick={() => copyToClipboard(displayContent, 'output')}
                                className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md transition-colors ${
                                  copiedField === 'output' 
                                    ? 'text-green-700 bg-green-100 border border-green-300' 
                                    : 'text-gray-600 bg-gray-100 hover:bg-gray-200 border border-gray-300'
                                }`}
                                title="Copy output data to clipboard"
                              >
                                <Copy className="w-3 h-3 mr-1" />
                                {copiedField === 'output' ? 'Copied!' : 'Copy'}
                              </button>
                            </div>
                          </div>
                          <div className="max-h-96 overflow-y-auto">
                            <div className="bg-gray-50 rounded-md p-4">
                              {renderFormattedContent(displayContent)}
                            </div>
                          </div>
                        </>
                      )
                    })()}
                  </div>
                </div>

                {/* Error Data (if exists) - Full Width - Solo vista original */}
                {selectedTrace.error_data && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-medium text-red-700">Error Data</h4>
                      <button
                        onClick={() => copyToClipboard(JSON.stringify(selectedTrace.error_data, null, 2), 'error')}
                        className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-md transition-colors ${
                          copiedField === 'error' 
                            ? 'text-green-700 bg-green-100 border border-green-300' 
                            : 'text-red-600 bg-red-100 hover:bg-red-200 border border-red-300'
                        }`}
                        title="Copy error data to clipboard"
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        {copiedField === 'error' ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <div className="max-h-48 overflow-y-auto">
                      <div className="bg-red-50 border border-red-200 rounded-md p-4">
                        <pre className="text-sm text-red-700 whitespace-pre-wrap overflow-x-auto">
                          {JSON.stringify(selectedTrace.error_data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Traces
