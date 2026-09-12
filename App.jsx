import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import ComparePage from './pages/ComparePage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/dashboard/:id" element={<DashboardPage />} />
          <Route path="/compare" element={<ComparePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
