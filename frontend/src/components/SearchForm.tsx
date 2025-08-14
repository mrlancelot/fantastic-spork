import React, { useState } from 'react';
import { Search, Calendar, Users, DollarSign, Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTripContext } from '../context/TripContext';
import { interests } from '../data/mockData';

export const SearchForm: React.FC = () => {
  const navigate = useNavigate();
  const { setFormData: saveFormData } = useTripContext();
  const [tripType, setTripType] = useState<'roundtrip' | 'oneway'>('roundtrip');
  const [travelClass, setTravelClass] = useState<'economy' | 'premium_economy' | 'business' | 'first'>('economy');
  const [formData, setFormData] = useState({
    fromCity: '',
    destination: '',
    startDate: null as Date | null,
    endDate: null as Date | null,
    travelers: 2,
    budget: 'moderate',
    interests: [] as string[],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.fromCity || !formData.destination || !formData.startDate) {
      alert('Please fill in all required fields');
      return;
    }
    
    // Validate dates for round trip
    if (tripType === 'roundtrip' && formData.endDate && formData.startDate > formData.endDate) {
      alert('Return date must be after departure date');
      return;
    }
    
    // Save form data to context
    saveFormData({
      fromCity: formData.fromCity,
      destination: formData.destination,
      startDate: formData.startDate,
      endDate: tripType === 'roundtrip' ? formData.endDate : null,
      travelers: formData.travelers,
      budget: formData.budget,
      interests: formData.interests,
      tripType,
      travelClass,
    });
    
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
        {/* Trip Type Toggle */}
        <div className="flex justify-center mb-4">
          <div className="inline-flex rounded-lg border border-gray-200 p-1">
            <button
              type="button"
              onClick={() => setTripType('roundtrip')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                tripType === 'roundtrip'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:text-gray-900'
              }`}
            >
              Round Trip
            </button>
            <button
              type="button"
              onClick={() => setTripType('oneway')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                tripType === 'oneway'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:text-gray-900'
              }`}
            >
              One Way
            </button>
          </div>
        </div>

        {/* Flight Search - All fields on same line */}
        <div className="grid grid-cols-6 gap-2">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-700">FROM</label>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-3 w-3 text-gray-400" />
              <input
                type="text"
                placeholder="City or airport"
                className="input-field pl-7 text-sm h-10"
                value={formData.fromCity}
                onChange={(e) => setFormData(prev => ({ ...prev, fromCity: e.target.value }))}
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
                placeholder="City or airport"
                className="input-field pl-7 text-sm h-10"
                value={formData.destination}
                onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
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
                required={tripType === 'roundtrip'}
                disabled={tripType === 'oneway'}
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
            <select 
              className="input-field text-sm h-10"
              value={travelClass}
              onChange={(e) => setTravelClass(e.target.value as any)}
            >
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First</option>
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