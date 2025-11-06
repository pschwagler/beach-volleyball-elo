import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Router from './Router.jsx'
import { DataProvider } from './contexts/DataContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <DataProvider>
      <Router />
    </DataProvider>
  </StrictMode>,
)
