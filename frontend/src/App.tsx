import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import WorkflowPage from './pages/WorkflowPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import TestPage from './pages/TestPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workflow" element={<WorkflowPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:projectName" element={<ProjectDetailPage />} />
          <Route path="/test" element={<TestPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App