import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './components/Login'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Traces from './pages/Traces'
import Usage from './pages/Usage'
import Cost from './pages/Cost'
import Settings from './pages/Settings'
import Docs from './pages/Docs'

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

// Login Route Component
const LoginRoute = () => {
  const { isAuthenticated, login, isLoading } = useAuth()
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  return <Login onLogin={login} isLoading={isLoading} />
}

function AppContent() {
  return (
    <Routes>
      <Route path="/login" element={<LoginRoute />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/projects" element={
        <ProtectedRoute>
          <Layout>
            <Projects />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/traces" element={
        <ProtectedRoute>
          <Layout>
            <Traces />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/usage" element={
        <ProtectedRoute>
          <Layout>
            <Usage />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/cost" element={
        <ProtectedRoute>
          <Layout>
            <Cost />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Layout>
            <Settings />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/docs" element={
        <ProtectedRoute>
          <Layout>
            <Docs />
          </Layout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  )
}

export default App
