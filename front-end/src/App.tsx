import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Projects from './pages/Projects';
import Experiments from './pages/Experiments';

const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/project-data" replace />} />
          <Route path="/project-data" element={<Projects />} />
          <Route path="/models" element={<div>Models Page</div>} />
          <Route path="/experiments" element={<Experiments />} />
          {/* Add more routes as needed */}
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
