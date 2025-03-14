import React from 'react'
import { createRoot } from 'react-dom/client'
import HomePage from './pages/HomePage.tsx'

const container = document.getElementById('root')
const root = createRoot(container!)
root.render(
  <React.StrictMode>
    <HomePage />
  </React.StrictMode>
) 