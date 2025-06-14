import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Projects from './pages/Projects';
import Project from './pages/Project';
import Pipeline from './pages/Pipeline';
import Experiments from './pages/Experiments';
import Home from './pages/Home';
import ProjectPage from './pages/ProjectPage';
import './App.css';

// Create a client
const queryClient = new QueryClient();

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Home />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/project/:id/data" element={<Project />} />
            <Route path="/project/:id/pipeline" element={<Pipeline />} />
            <Route path="/project/:id/models" element={<div>Models Page</div>} />
            <Route path="/project/:id/experiments" element={<Experiments />} />
            <Route path="/project-page" element={<ProjectPage />} />
            {/* Add more routes as needed */}
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
