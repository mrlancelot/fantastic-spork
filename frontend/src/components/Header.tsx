import React from 'react';
import { MapPin } from 'lucide-react';

interface HeaderProps {
  showLogo?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ showLogo = true }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {showLogo && (
            <div className="flex items-center space-x-2">
              <MapPin className="h-8 w-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">Waypoint</span>
            </div>
          )}
          
          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Discover
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              My Trips
            </a>
            <a href="#" className="text-gray-700 hover:text-primary-600 font-medium">
              Help
            </a>
          </nav>
          
          <div className="flex items-center space-x-4">
            <button className="btn-secondary">
              Sign In
            </button>
            <button className="btn-primary">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};