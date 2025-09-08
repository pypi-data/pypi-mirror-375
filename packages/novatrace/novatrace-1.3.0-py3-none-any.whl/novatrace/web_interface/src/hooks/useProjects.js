import { useState, useEffect } from 'react'
import { projectsAPI } from '../services/api'

export const useProjects = () => {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const response = await projectsAPI.getAll()
      setProjects(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching projects:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const startProject = async (id) => {
    try {
      await projectsAPI.start(id)
      await fetchProjects() // Refresh the list
    } catch (err) {
      console.error('Error starting project:', err)
      throw err
    }
  }

  const stopProject = async (id) => {
    try {
      await projectsAPI.stop(id)
      await fetchProjects() // Refresh the list
    } catch (err) {
      console.error('Error stopping project:', err)
      throw err
    }
  }

  const pauseProject = async (id) => {
    try {
      await projectsAPI.pause(id)
      await fetchProjects() // Refresh the list
    } catch (err) {
      console.error('Error pausing project:', err)
      throw err
    }
  }

  const deleteProject = async (id) => {
    try {
      await projectsAPI.delete(id)
      await fetchProjects() // Refresh the list
    } catch (err) {
      console.error('Error deleting project:', err)
      throw err
    }
  }

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
    startProject,
    stopProject,
    pauseProject,
    deleteProject,
  }
}

export const useProject = (id) => {
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!id) return

    const fetchProject = async () => {
      try {
        const response = await projectsAPI.getById(id)
        setProject(response.data)
        setError(null)
      } catch (err) {
        setError(err.message)
        console.error('Error fetching project:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProject()
  }, [id])

  return { project, loading, error }
}
