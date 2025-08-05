import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthWrapper } from './components/AuthWrapper';
import Landing from './components/Landing';
import Itinerary from './components/Itinerary';

function App() {
  return (
    <AuthWrapper>
      <Router>
        <div className="min-h-screen bg-white">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/itinerary" element={<Itinerary />} />
          </Routes>
        </div>
      </Router>
    </AuthWrapper>
  );
}

export default App;