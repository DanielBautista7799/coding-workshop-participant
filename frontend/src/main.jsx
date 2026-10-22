import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import {
  CssBaseline,
  ThemeProvider,
} from '@mui/material'

import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import theme from './theme.js'

import './index.css'


createRoot(
  document.getElementById('root'),
).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />

        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)

if (
  'serviceWorker' in navigator
  && import.meta.env.PROD
) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .catch((error) => {
        console.error(
          'Service worker registration failed:',
          error,
        )
      })
  })
}
