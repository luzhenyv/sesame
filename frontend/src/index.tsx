import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom'
import HomePage from './pages/HomePage.tsx'
import FamilyPage from './pages/FamilyPage.tsx'
import ProfilePage from './pages/ProfilePage.tsx'
import AssessmentsPage from './pages/AssessmentsPage.tsx'
import BlogPage from './pages/BlogPage.tsx'
import Layout from './components/Layout.tsx'

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
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/family" element={<FamilyPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/assessments" element={<AssessmentsPage />} />
          <Route path="/blog" element={<BlogPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
) 