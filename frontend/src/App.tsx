import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { LoadingPage } from './pages/LoadingPage';
import { ItineraryPage } from './pages/ItineraryPage';
import { MyTripsPage } from './pages/MyTripsPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/loading" element={<LoadingPage />} />
          <Route path="/itinerary" element={<ItineraryPage />} />
          <Route path="/my-trips" element={<MyTripsPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;