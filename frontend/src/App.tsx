import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { TripProvider } from './context/TripContext';
import { LandingPage } from './pages/LandingPage';
import { LoadingPage } from './pages/LoadingPage';
import { ItineraryPage } from './pages/ItineraryPage';

function App() {
  return (
    <TripProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/loading" element={<LoadingPage />} />
            <Route path="/itinerary" element={<ItineraryPage />} />
          </Routes>
        </div>
      </Router>
    </TripProvider>
  );
}

export default App;