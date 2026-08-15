import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import WebApp from '@twa-dev/sdk'

import './index.css'
import App from './App'

import { ThemeProvider } from './theme/ThemeContext'
import { AuthProvider } from './context/AuthContext'


WebApp.ready()
WebApp.expand()


createRoot(
  document.getElementById('root')!,
).render(
  <StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </StrictMode>,
)