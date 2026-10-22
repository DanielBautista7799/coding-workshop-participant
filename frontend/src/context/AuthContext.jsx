import {
  useState,
} from 'react'

import {
  login as apiLogin,
  register as apiRegister,
} from '../services/api'

import AuthContext from './auth-context'


function getStoredUser() {
  const storedUser = localStorage.getItem('user')

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(storedUser)
  } catch {
    return null
  }
}


export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser)


  async function login(email, password) {
    const data = await apiLogin(
      email,
      password,
    )

    localStorage.setItem(
      'access_token',
      data.access_token,
    )

    localStorage.setItem(
      'refresh_token',
      data.refresh_token,
    )

    localStorage.setItem(
      'user',
      JSON.stringify(data.user),
    )

    setUser(data.user)

    return data.user
  }


  async function register(
    fullName,
    email,
    password,
  ) {
    await apiRegister(
      fullName,
      email,
      password,
    )

    return login(
      email,
      password,
    )
  }


  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    setUser(null)
  }


  const value = {
    user,
    login,
    register,
    logout,
    isAuthenticated: Boolean(user),
  }


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
