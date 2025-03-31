import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'
import HomePage from './pages/HomePage.tsx'
import FamilyPage from './pages/FamilyPage.tsx'
import ProfilePage from './pages/ProfilePage.tsx'
import AssessmentsPage from './pages/AssessmentsPage.tsx'
import BlogPage from './pages/BlogPage.tsx'
import Login from './pages/Login.tsx'
import Register from './pages/Register.tsx'
import Layout from './components/Layout.tsx'
import { AuthProvider } from './context/AuthContext.tsx'
import ProtectedRoute from './components/ProtectedRoute.tsx'

const container = document.getElementById('root')
const root = createRoot(container!)

// Create a layout route wrapper
const AppLayout = () => (
  <Layout>
    <Outlet />
  </Layout>
);

root.render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected routes */}
            <Route path="/family" element={
              <ProtectedRoute>
                <FamilyPage />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
            <Route path="/assessments" element={
              <ProtectedRoute>
                <AssessmentsPage />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
) 