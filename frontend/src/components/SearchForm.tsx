import React, { useState } from 'react';
import { Search, Calendar, Users, DollarSign, Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { SearchFormData } from '../types';
import { interests } from '../data/mockData';

export const SearchForm: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<SearchFormData>({
    destination: '',
    startDate: null,
    endDate: null,
    travelers: 2,
    budget: 'moderate',
    interests: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would save the form data to context/state
    navigate('/loading');
  };

  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  return (
    <div className="scale-100 origin-top">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-7">
        {/* Flight Search - All fields on same line */}
        <div className="grid grid-cols-6 gap-2">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">FROM</label>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <input
                type="text"
                placeholder="Where from?"
                className="input-field pl-7 text-sm h-10"
                value={formData.destination}
                onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">TO</label>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <input
                type="text"
                placeholder="Where to?"
                className="input-field pl-7 text-sm h-10"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">DEPARTURE</label>
            <div className="relative">
              <Calendar className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <input
                type="date"
                className="input-field pl-7 text-sm h-10"
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  startDate: e.target.value ? new Date(e.target.value) : null 
                }))}
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">RETURN</label>
            <div className="relative">
              <Calendar className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <input
                type="date"
                className="input-field pl-7 text-sm h-10"
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  endDate: e.target.value ? new Date(e.target.value) : null 
                }))}
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">PASSENGERS</label>
            <div className="relative">
              <Users className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <select
                className="input-field pl-7 text-sm h-10"
                value={formData.travelers}
                onChange={(e) => setFormData(prev => ({ ...prev, travelers: parseInt(e.target.value) }))}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                  <option key={num} value={num}>
                    {num} {num === 1 ? 'adult' : 'adults'}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">CLASS</label>
            <select className="input-field text-sm h-10">
              <option>Economy</option>
              <option>Premium Economy</option>
              <option>Business</option>
              <option>First</option>
            </select>
          </div>
        </div>

        {/* Budget */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">Budget Range</label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { value: 'budget', label: 'Budget', desc: 'Under $100/day', icon: DollarSign },
              { value: 'moderate', label: 'Moderate', desc: '$100-250/day', icon: DollarSign },
              { value: 'luxury', label: 'Luxury', desc: '$250+/day', icon: DollarSign },
            ].map(budget => (
              <label key={budget.value} className="cursor-pointer">
                <input
                  type="radio"
                  name="budget"
                  value={budget.value}
                  checked={formData.budget === budget.value}
                  onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
                  className="sr-only"
                />
                <div className={`card p-3 text-center transition-all duration-200 ${
                  formData.budget === budget.value
                    ? 'border-primary-500 bg-primary-50'
                    : 'hover:border-gray-300'
                }`}>
                  <budget.icon className="h-6 w-6 mx-auto mb-1 text-gray-600" />
                  <div className="text-sm font-medium text-gray-900">{budget.label}</div>
                  <div className="text-xs text-gray-500">{budget.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Interests */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            What are you interested in? (Select all that apply)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            {interests.map(interest => (
              <button
                key={interest}
                type="button"
                onClick={() => handleInterestToggle(interest)}
                className={`p-2 rounded-lg text-xs font-medium transition-all duration-200 ${
                  formData.interests.includes(interest)
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Heart className={`h-3 w-3 mx-auto mb-1 ${
                  formData.interests.includes(interest) ? 'fill-current' : ''
                }`} />
                {interest}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            className="btn-primary text-base px-10 py-3 rounded-xl"
            disabled={!formData.destination}
          >
            Plan My Trip
          </button>
        </div>
      </form>
    </div>
  );
};