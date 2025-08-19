import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, ChevronLeft, ChevronRight } from 'lucide-react';
import { RetroWindow, Button, Input, Select, Tag, theme } from '../components/retro';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    tripType: 'round',
    from: '',
    to: '',
    departure: '',
    return: '',
    passengers: '1',
    class: 'economy',
    interests: [] as string[]
  });

  const interests = ['Food tours', 'Museums', 'Outdoor activities', 'Nightlife', 'Shopping', 'Historical sites', 'Local culture', 'Art galleries'];

  const toggleInterest = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/loading');
  };

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-3xl mx-auto">
        <RetroWindow variant="default" title="Create Itinerary" icon={<Plane className="w-4 h-4" />}>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="flex gap-2 p-1 bg-gray-100 rounded-[8px] border-2 border-[#222222]">
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, tripType: 'round' }))}
                className={`flex-1 py-2 px-3 rounded-[6px] font-medium transition-all ${
                  formData.tripType === 'round' ? 'bg-[#4A90E2] text-white' : ''
                }`}
              >
                ROUND TRIP
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, tripType: 'one' }))}
                className={`flex-1 py-2 px-3 rounded-[6px] font-medium transition-all ${
                  formData.tripType === 'one' ? 'bg-[#4A90E2] text-white' : ''
                }`}
              >
                ONE WAY
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 flex gap-2 items-end">
                <div className="flex-1">
                  <Input
                    label="From"
                    value={formData.from}
                    onChange={(e) => setFormData(prev => ({ ...prev, from: e.target.value }))}
                    placeholder="New York"
                    required
                  />
                </div>
                <Button variant="secondary" className="mb-0">
                  <ChevronLeft className="w-4 h-4 inline mr-1" />
                  <ChevronRight className="w-4 h-4 inline" />
                </Button>
                <div className="flex-1">
                  <Input
                    label="To"
                    value={formData.to}
                    onChange={(e) => setFormData(prev => ({ ...prev, to: e.target.value }))}
                    placeholder="Tokyo"
                    required
                  />
                </div>
              </div>

              <Input
                label="Departure"
                type="date"
                value={formData.departure}
                onChange={(e) => setFormData(prev => ({ ...prev, departure: e.target.value }))}
                required
              />
              
              {formData.tripType === 'round' && (
                <Input
                  label="Return"
                  type="date"
                  value={formData.return}
                  onChange={(e) => setFormData(prev => ({ ...prev, return: e.target.value }))}
                  required
                />
              )}

              <Select
                label="Passengers"
                value={formData.passengers}
                onChange={(e) => setFormData(prev => ({ ...prev, passengers: e.target.value }))}
                options={[
                  { value: '1', label: '1 Passenger' },
                  { value: '2', label: '2 Passengers' },
                  { value: '3', label: '3 Passengers' },
                  { value: '4+', label: '4+ Passengers' }
                ]}
              />

              <Select
                label="Class"
                value={formData.class}
                onChange={(e) => setFormData(prev => ({ ...prev, class: e.target.value }))}
                options={[
                  { value: 'economy', label: 'Economy' },
                  { value: 'premium', label: 'Premium Economy' },
                  { value: 'business', label: 'Business' },
                  { value: 'first', label: 'First' }
                ]}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">What interests you?</label>
              <div className="flex flex-wrap gap-2">
                {interests.map(interest => (
                  <Tag
                    key={interest}
                    selected={formData.interests.includes(interest)}
                    onClick={() => toggleInterest(interest)}
                  >
                    {interest}
                  </Tag>
                ))}
              </div>
            </div>

            <Button type="submit" className="w-full">
              Create itinerary →
            </Button>
          </form>
        </RetroWindow>
      </div>
    </div>
  );
};