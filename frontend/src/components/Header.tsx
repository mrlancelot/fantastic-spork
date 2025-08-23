import React from 'react';
import { Heart, Bookmark, User } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex justify-end items-center gap-4">
        <button className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">
          <Heart className="w-4 h-4" />
          Save trip
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">
          <Bookmark className="w-4 h-4" />
          My trips
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">
          <User className="w-4 h-4" />
          Sign in
        </button>
      </div>
    </header>
  );
};