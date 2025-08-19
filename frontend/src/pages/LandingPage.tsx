import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, ArrowUpDown, ArrowRight, ArrowLeftRight } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [tripType, setTripType] = useState<'roundtrip' | 'oneway'>('roundtrip');
  const [interests, setInterests] = useState('');
  const [formData, setFormData] = useState({
    from: '',
    to: '',
    departure: '',
    return: '',
    travelers: '1 adult',
    class: 'Economy'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/loading');
  };

  const swapLocations = () => {
    setFormData(prev => ({
      ...prev,
      from: prev.to,
      to: prev.from
    }));
  };

  const quickSuggestions = [
    'Food tours', 'Museums', 'Outdoor activities', 'Nightlife', 
    'Shopping', 'Historical sites', 'Local culture', 'Art galleries'
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <MapPin className="h-7 w-7 text-primary-600" />
              <span className="text-lg font-semibold text-neutral-900">Waypoint</span>
            </div>
            <div className="flex items-center space-x-8">
              <a href="#" className="text-neutral-700 hover:text-primary-600">My trips</a>
              <a href="#" className="text-neutral-700 hover:text-primary-600">Sign in</a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-neutral-900 mb-2">Where to next?</h1>
          <p className="text-neutral-600">Search flights and create your perfect itinerary</p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Segmented control */}
          <div className="flex justify-center mb-6">
            <div className="inline-flex p-1 bg-neutral-100 rounded-lg">
              <button
                type="button"
                onClick={() => setTripType('roundtrip')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  tripType === 'roundtrip' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600'
                }`}
              >
                Round trip
              </button>
              <button
                type="button"
                onClick={() => setTripType('oneway')}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  tripType === 'oneway' ? 'bg-white text-neutral-900 shadow-sm' : 'text-neutral-600'
                }`}
              >
                One way
              </button>
            </div>
          </div>

          {/* Main search card */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6">
            {/* First row - From, Swap, To, Departure */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-4">
              <div className="md:col-span-3">
                <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">FROM</label>
                <input
                  type="text"
                  placeholder="Where from?"
                  value={formData.from}
                  onChange={(e) => setFormData(prev => ({ ...prev, from: e.target.value }))}
                  className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
              <div className="md:col-span-1 flex items-end justify-center">
                <button
                  type="button"
                  onClick={swapLocations}
                  className="w-10 h-10 rounded-lg border border-neutral-300 flex items-center justify-center text-neutral-400 hover:text-primary-600 hover:border-primary-300 hover:bg-neutral-50 transition-all"
                  aria-label="Swap locations"
                >
                  <ArrowLeftRight className="w-4 h-4" />
                </button>
              </div>
              <div className="md:col-span-3">
                <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">TO</label>
                <input
                  type="text"
                  placeholder="Where to?"
                  value={formData.to}
                  onChange={(e) => setFormData(prev => ({ ...prev, to: e.target.value }))}
                  className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">DEPARTURE</label>
                <input
                  type="date"
                  value={formData.departure}
                  onChange={(e) => setFormData(prev => ({ ...prev, departure: e.target.value }))}
                  className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
              {tripType === 'roundtrip' && (
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">RETURN</label>
                  <input
                    type="date"
                    value={formData.return}
                    onChange={(e) => setFormData(prev => ({ ...prev, return: e.target.value }))}
                    className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>
              )}
            </div>

            {/* Third row - Passengers and Class */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="md:col-span-1">
                <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">PASSENGERS</label>
                <select
                  value={formData.travelers}
                  onChange={(e) => setFormData(prev => ({ ...prev, travelers: e.target.value }))}
                  className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none cursor-pointer"
                >
                  <option>1 adult</option>
                  <option>2 adults</option>
                  <option>3 adults</option>
                  <option>4 adults</option>
                </select>
              </div>
              <div className="md:col-span-1">
                <label className="block text-xs font-medium text-neutral-500 uppercase mb-2">CLASS</label>
                <select
                  value={formData.class}
                  onChange={(e) => setFormData(prev => ({ ...prev, class: e.target.value }))}
                  className="w-full px-3 py-2.5 text-base bg-white border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none cursor-pointer"
                >
                  <option>Economy</option>
                  <option>Business</option>
                  <option>First Class</option>
                </select>
              </div>
            </div>
          </div>

          {/* Interests card */}
          <div className="bg-white rounded-xl border border-neutral-200 p-6 mt-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">What interests you?</h3>
              <p className="text-sm text-neutral-600 mb-1">Help us personalize your itinerary by sharing your travel interests and preferences</p>
              <p className="text-xs text-neutral-500">Examples: Food tours, museums, outdoor activities, nightlife, shopping, historical sites, local culture...</p>
            </div>
            <textarea
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="Tell us what you'd like to experience..."
              rows={4}
              className="w-full px-4 py-3 text-base border border-neutral-300 rounded-lg placeholder:text-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />

            <div className="mt-4">
              <p className="text-xs font-medium text-neutral-500 uppercase mb-3">QUICK SUGGESTIONS</p>
              <div className="flex flex-wrap gap-2">
                {quickSuggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => {
                      const newInterests = interests ? `${interests}, ${suggestion}` : suggestion;
                      setInterests(newInterests);
                    }}
                    className="px-3 py-1.5 text-sm bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors border border-neutral-200"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <div className="flex justify-center mt-8">
            <button 
              type="submit" 
              className="inline-flex items-center gap-2 px-8 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors shadow-sm"
            >
              <span>Create itinerary</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </form>
      </main>
    </div>
  );
};