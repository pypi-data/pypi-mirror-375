import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, User, Lock, Save, Eye, EyeOff, Check, X, Plus, Trash2, UserCheck, UserX } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const Settings = () => {
  const { user } = useAuth()
  const [userInfo, setUserInfo] = useState(null)
  const [users, setUsers] = useState([])
  const [showCreateUser, setShowCreateUser] = useState(false)
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    is_active: true
  })
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
    newUser: false,
    confirmNewUser: false
  })
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [userMessage, setUserMessage] = useState({ type: '', text: '' })

  const isAdmin = user?.username === 'admin'

  useEffect(() => {
    fetchUserInfo()
    if (isAdmin) {
      fetchUsers()
    }
  }, [isAdmin])

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUserInfo(data)
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
    }
  }

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/users', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setUserMessage({ type: '', text: '' })

    // Validation
    if (!newUser.username || !newUser.password || !newUser.confirmPassword) {
      setUserMessage({ type: 'error', text: 'Please fill in all fields' })
      setIsLoading(false)
      return
    }

    if (newUser.password !== newUser.confirmPassword) {
      setUserMessage({ type: 'error', text: 'Passwords do not match' })
      setIsLoading(false)
      return
    }

    if (newUser.password.length < 6) {
      setUserMessage({ type: 'error', text: 'Password must be at least 6 characters long' })
      setIsLoading(false)
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          username: newUser.username,
          password: newUser.password,
          is_active: newUser.is_active
        })
      })

      if (response.ok) {
        setUserMessage({ type: 'success', text: 'User created successfully' })
        setNewUser({
          username: '',
          password: '',
          confirmPassword: '',
          is_active: true
        })
        setShowCreateUser(false)
        fetchUsers()
      } else {
        const errorData = await response.json()
        setUserMessage({ type: 'error', text: errorData.detail || 'Failed to create user' })
      }
    } catch (error) {
      setUserMessage({ type: 'error', text: 'Network error. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !currentStatus })
      })

      if (response.ok) {
        setUserMessage({ type: 'success', text: 'User status updated successfully' })
        fetchUsers()
      } else {
        const errorData = await response.json()
        setUserMessage({ type: 'error', text: errorData.detail || 'Failed to update user' })
      }
    } catch (error) {
      setUserMessage({ type: 'error', text: 'Network error. Please try again.' })
    }
  }

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setUserMessage({ type: 'success', text: 'User deleted successfully' })
        fetchUsers()
      } else {
        const errorData = await response.json()
        setUserMessage({ type: 'error', text: errorData.detail || 'Failed to delete user' })
      }
    } catch (error) {
      setUserMessage({ type: 'error', text: 'Network error. Please try again.' })
    }
  }

  const handlePasswordChange = (e) => {
    setPasswordForm(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleNewUserChange = (e) => {
    const { name, value, type, checked } = e.target
    setNewUser(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage({ type: '', text: '' })

    // Validation
    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      setMessage({ type: 'error', text: 'Please fill in all fields' })
      setIsLoading(false)
      return
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' })
      setIsLoading(false)
      return
    }

    if (passwordForm.new_password.length < 6) {
      setMessage({ type: 'error', text: 'New password must be at least 6 characters long' })
      setIsLoading(false)
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })
      })

      if (response.ok) {
        setMessage({ type: 'success', text: 'Password changed successfully' })
        setPasswordForm({
          current_password: '',
          new_password: '',
          confirm_password: ''
        })
      } else {
        const errorData = await response.json()
        setMessage({ type: 'error', text: errorData.detail || 'Failed to change password' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' }
    
    let strength = 0
    if (password.length >= 6) strength += 25
    if (password.length >= 8) strength += 25
    if (/[A-Z]/.test(password)) strength += 25
    if (/[0-9]/.test(password)) strength += 25
    
    let label = 'Weak'
    let color = 'bg-red-500'
    
    if (strength >= 75) {
      label = 'Strong'
      color = 'bg-green-500'
    } else if (strength >= 50) {
      label = 'Medium'
      color = 'bg-yellow-500'
    }
    
    return { strength, label, color }
  }

  const passwordStrength = getPasswordStrength(passwordForm.new_password)
  const newUserPasswordStrength = getPasswordStrength(newUser.password)

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <SettingsIcon className="w-6 h-6 text-gray-600 mr-3" />
            <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
          </div>
        </div>

        <div className="p-6 space-y-8">
          {/* User Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <User className="w-5 h-5 mr-2" />
              User Information
            </h2>
            
            {userInfo && (
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Username:</span>
                  <span className="text-sm text-gray-900">{userInfo.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Account Created:</span>
                  <span className="text-sm text-gray-900">
                    {new Date(userInfo.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Last Login:</span>
                  <span className="text-sm text-gray-900">
                    {userInfo.last_login 
                      ? new Date(userInfo.last_login).toLocaleString()
                      : 'Never'
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-500">Status:</span>
                  <span className={`text-sm ${userInfo.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {userInfo.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* User Management - Only for Admin */}
          {isAdmin && (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <User className="w-5 h-5 mr-2" />
                User Management
              </h2>

              {userMessage.text && (
                <div className={`mb-4 p-3 rounded-md flex items-center ${
                  userMessage.type === 'success' 
                    ? 'bg-green-50 border border-green-200 text-green-800' 
                    : 'bg-red-50 border border-red-200 text-red-800'
                }`}>
                  {userMessage.type === 'success' ? (
                    <Check className="w-4 h-4 mr-2" />
                  ) : (
                    <X className="w-4 h-4 mr-2" />
                  )}
                  {userMessage.text}
                </div>
              )}

              <div className="space-y-4">
                {/* Add User Button */}
                <div className="flex justify-between items-center">
                  <h3 className="text-md font-medium text-gray-700">System Users</h3>
                  <button
                    onClick={() => setShowCreateUser(!showCreateUser)}
                    className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add User
                  </button>
                </div>

                {/* Create User Form */}
                {showCreateUser && (
                  <div className="bg-gray-50 rounded-lg p-4 border">
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Create New User</h4>
                    <form onSubmit={handleCreateUser} className="space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Username
                          </label>
                          <input
                            type="text"
                            name="username"
                            value={newUser.username}
                            onChange={handleNewUserChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Enter username"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Status
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              name="is_active"
                              checked={newUser.is_active}
                              onChange={handleNewUserChange}
                              className="mr-2"
                            />
                            <span className="text-sm text-gray-700">Active</span>
                          </label>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPasswords.newUser ? 'text' : 'password'}
                              name="password"
                              value={newUser.password}
                              onChange={handleNewUserChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Enter password"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPasswords(prev => ({ ...prev, newUser: !prev.newUser }))}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                            >
                              {showPasswords.newUser ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                          
                          {/* Password Strength Indicator */}
                          {newUser.password && (
                            <div className="mt-2">
                              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                                <span>Password Strength</span>
                                <span>{newUserPasswordStrength.label}</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full transition-all duration-300 ${newUserPasswordStrength.color}`}
                                  style={{ width: `${newUserPasswordStrength.strength}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPasswords.confirmNewUser ? 'text' : 'password'}
                              name="confirmPassword"
                              value={newUser.confirmPassword}
                              onChange={handleNewUserChange}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Confirm password"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPasswords(prev => ({ ...prev, confirmNewUser: !prev.confirmNewUser }))}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                            >
                              {showPasswords.confirmNewUser ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                          </div>
                          
                          {/* Password Match Indicator */}
                          {newUser.confirmPassword && (
                            <div className="mt-1 text-xs">
                              {newUser.password === newUser.confirmPassword ? (
                                <span className="text-green-600 flex items-center">
                                  <Check className="w-3 h-3 mr-1" /> Passwords match
                                </span>
                              ) : (
                                <span className="text-red-600 flex items-center">
                                  <X className="w-3 h-3 mr-1" /> Passwords do not match
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex justify-end space-x-2">
                        <button
                          type="button"
                          onClick={() => setShowCreateUser(false)}
                          className="px-3 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={isLoading}
                          className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                          <Save className="w-4 h-4 mr-2" />
                          {isLoading ? 'Creating...' : 'Create User'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Users List */}
                <div className="bg-white border rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Created
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Last Login
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-8 w-8">
                                <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                                  <User className="h-4 w-4 text-gray-600" />
                                </div>
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">
                                  {user.username}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              user.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(user.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex justify-end space-x-2">
                              {user.username !== 'admin' && (
                                <>
                                  <button
                                    onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                                    className={`p-1 rounded ${
                                      user.is_active 
                                        ? 'text-orange-600 hover:text-orange-800' 
                                        : 'text-green-600 hover:text-green-800'
                                    }`}
                                    title={user.is_active ? 'Deactivate user' : 'Activate user'}
                                  >
                                    {user.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                                  </button>
                                  <button
                                    onClick={() => handleDeleteUser(user.id)}
                                    className="p-1 text-red-600 hover:text-red-800"
                                    title="Delete user"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Change Password */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Lock className="w-5 h-5 mr-2" />
              Change Password
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              {message.text && (
                <div className={`p-3 rounded-md flex items-center ${
                  message.type === 'success' 
                    ? 'bg-green-50 border border-green-200 text-green-800' 
                    : 'bg-red-50 border border-red-200 text-red-800'
                }`}>
                  {message.type === 'success' ? (
                    <Check className="w-4 h-4 mr-2" />
                  ) : (
                    <X className="w-4 h-4 mr-2" />
                  )}
                  {message.text}
                </div>
              )}

              {/* Current Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.current ? 'text' : 'password'}
                    name="current_password"
                    value={passwordForm.current_password}
                    onChange={handlePasswordChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your current password"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('current')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.new ? 'text' : 'password'}
                    name="new_password"
                    value={passwordForm.new_password}
                    onChange={handlePasswordChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter your new password"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('new')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {passwordForm.new_password && (
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                      <span>Password Strength</span>
                      <span>{passwordStrength.label}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                        style={{ width: `${passwordStrength.strength}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm New Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    type={showPasswords.confirm ? 'text' : 'password'}
                    name="confirm_password"
                    value={passwordForm.confirm_password}
                    onChange={handlePasswordChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Confirm your new password"
                  />
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('confirm')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                
                {/* Password Match Indicator */}
                {passwordForm.confirm_password && (
                  <div className="mt-1 text-xs">
                    {passwordForm.new_password === passwordForm.confirm_password ? (
                      <span className="text-green-600 flex items-center">
                        <Check className="w-3 h-3 mr-1" /> Passwords match
                      </span>
                    ) : (
                      <span className="text-red-600 flex items-center">
                        <X className="w-3 h-3 mr-1" /> Passwords do not match
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {isLoading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
