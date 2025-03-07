import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import PhotoSearchPage from './features/photoSearch/PhotoSearchPage.tsx';
import FaceAnnotationPage from './features/faceAnnotation/FaceAnnotationPage.tsx';
import './App.css';

function App() {
  const location = useLocation();
  
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">
          <h1>NaoRaamat</h1>
        </div>
        <nav className="app-nav">
          <Link 
            to="/photos" 
            className={`nav-link ${location.pathname === '/photos' ? 'active' : ''}`}
          >
            Photo Search
          </Link>
          <Link 
            to="/annotate" 
            className={`nav-link ${location.pathname === '/annotate' ? 'active' : ''}`}
          >
            Face Annotation
          </Link>
        </nav>
      </header>
      
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/photos" replace />} />
          <Route path="/photos" element={<PhotoSearchPage />} />
          <Route path="/annotate" element={<FaceAnnotationPage />} />
        </Routes>
      </main>
      
      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} NaoRaamat - Photo Search Application</p>
      </footer>
    </div>
  );
}

export default App;