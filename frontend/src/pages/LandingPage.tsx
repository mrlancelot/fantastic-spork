import React from 'react';
import { MapPin } from 'lucide-react';
import { SearchForm } from '../components/SearchForm';

export const LandingPage: React.FC = () => {
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
      <main className="max-w-5xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-semibold text-neutral-900 mb-2">Where to next?</h1>
          <p className="text-neutral-600">Search flights and create your perfect itinerary</p>
        </div>

        {/* Search Form Component */}
        <SearchForm />
      </main>
    </div>
  );
};