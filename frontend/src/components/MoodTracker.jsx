import React, { useState } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { Heart, Zap, Frown, Meh, Smile, Laugh, ThumbsUp, MessageSquare, TrendingUp, Cloud, Users } from 'lucide-react';
import { motion } from 'framer-motion';

const moods = [
  { id: 'excited', name: 'Excited', icon: '🤩', color: 'bg-yellow-500', description: 'Feeling amazing!' },
  { id: 'happy', name: 'Happy', icon: '😊', color: 'bg-green-500', description: 'Great vibes' },
  { id: 'neutral', name: 'Neutral', icon: '😐', color: 'bg-gray-500', description: 'Just okay' },
  { id: 'tired', name: 'Tired', icon: '😴', color: 'bg-blue-500', description: 'Need rest' },
  { id: 'stressed', name: 'Stressed', icon: '😰', color: 'bg-red-500', description: 'Feeling overwhelmed' },
];

const energyLevels = [
  { value: 1, label: 'Exhausted', emoji: '🔋' },
  { value: 2, label: 'Very Low', emoji: '🔋' },
  { value: 3, label: 'Low', emoji: '🔋' },
  { value: 4, label: 'Below Average', emoji: '🔋' },
  { value: 5, label: 'Average', emoji: '🔋' },
  { value: 6, label: 'Above Average', emoji: '🔋' },
  { value: 7, label: 'Good', emoji: '🔋' },
  { value: 8, label: 'High', emoji: '🔋' },
  { value: 9, label: 'Very High', emoji: '🔋' },
  { value: 10, label: 'Peak Energy', emoji: '⚡' },
];

function MoodButton({ mood, isSelected, onClick, disabled = false }) {
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      onClick={() => !disabled && onClick(mood.id)}
      disabled={disabled}
      className={`p-4 rounded-xl border-2 transition-all ${
        isSelected
          ? `${mood.color} text-white border-transparent shadow-lg`
          : 'bg-white text-gray-700 border-gray-200 hover:border-gray-300 hover:shadow-md'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <div className="text-3xl mb-2">{mood.icon}</div>
      <div className="text-sm font-medium">{mood.name}</div>
      <div className="text-xs opacity-75 mt-1">{mood.description}</div>
    </motion.button>
  );
}

function EnergySlider({ value, onChange, disabled = false }) {
  const getBatteryColor = (level) => {
    if (level <= 3) return 'text-red-500';
    if (level <= 6) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getBatteryFill = (level) => {
    return Math.max(10, (level / 10) * 100);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">Energy Level</label>
        <div className="flex items-center gap-2">
          <div className={`text-2xl ${getBatteryColor(value)}`}>
            {value >= 8 ? '⚡' : '🔋'}
          </div>
          <span className="text-lg font-semibold text-gray-800">{value}/10</span>
        </div>
      </div>
      
      <div className="relative">
        <input
          type="range"
          min="1"
          max="10"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          disabled={disabled}
          className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #ef4444 0%, #f59e0b 50%, #10b981 100%)`
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>Low</span>
          <span>Medium</span>
          <span>High</span>
        </div>
      </div>
      
      <div className="text-center">
        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
          value >= 8 ? 'bg-green-100 text-green-800' :
          value >= 5 ? 'bg-yellow-100 text-yellow-800' :
          'bg-red-100 text-red-800'
        }`}>
          {energyLevels[value - 1]?.emoji}
          {energyLevels[value - 1]?.label}
        </div>
      </div>
    </div>
  );
}

function MoodAnalytics({ tripId, moodHistory }) {
  if (!moodHistory || moodHistory.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Mood Analytics
        </h3>
        <p className="text-gray-500 text-center py-8">
          Complete a few mood check-ins to see your travel analytics!
        </p>
      </div>
    );
  }

  const analytics = useQuery(api.moodTracking.getMoodAnalytics, { tripId });
  
  if (!analytics) return null;

  const getMoodColor = (moodId) => {
    const mood = moods.find(m => m.id === moodId);
    return mood?.color || 'bg-gray-500';
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5" />
        Your Travel Analytics
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Average Energy */}
        <div className="text-center">
          <div className="text-3xl mb-2">⚡</div>
          <div className="text-2xl font-bold text-gray-800">{analytics.averageEnergy}/10</div>
          <div className="text-sm text-gray-600">Average Energy</div>
        </div>
        
        {/* Dominant Mood */}
        <div className="text-center">
          <div className="text-3xl mb-2">
            {moods.find(m => m.id === analytics.trends.dominantMood)?.icon || '😊'}
          </div>
          <div className="text-lg font-semibold text-gray-800 capitalize">
            {analytics.trends.dominantMood || 'Happy'}
          </div>
          <div className="text-sm text-gray-600">Most Common Mood</div>
        </div>
      </div>
      
      {/* Mood Distribution */}
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Mood Distribution</h4>
        <div className="space-y-2">
          {Object.entries(analytics.moodDistribution).map(([moodId, count]) => {
            const mood = moods.find(m => m.id === moodId);
            const percentage = (count / analytics.totalEntries) * 100;
            
            return (
              <div key={moodId} className="flex items-center gap-3">
                <span className="text-lg">{mood?.icon}</span>
                <span className="text-sm font-medium text-gray-700 w-16">{mood?.name}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${mood?.color}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600 w-12 text-right">
                  {percentage.toFixed(0)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Recommendations */}
      {analytics.recommendations.length > 0 && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-medium text-blue-800 mb-2 flex items-center gap-2">
            <ThumbsUp className="w-4 h-4" />
            Personalized Recommendations
          </h4>
          <ul className="space-y-1">
            {analytics.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-blue-700">
                • {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Impact Factors */}
      <div className="mt-4 grid grid-cols-2 gap-4">
        {analytics.trends.weatherImpact > 0.3 && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Cloud className="w-6 h-6 mx-auto mb-1 text-gray-600" />
            <div className="text-sm text-gray-700">Weather Impact</div>
            <div className="text-xs text-gray-500">
              {(analytics.trends.weatherImpact * 100).toFixed(0)}% of entries
            </div>
          </div>
        )}
        
        {analytics.trends.crowdImpact > 0.3 && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <Users className="w-6 h-6 mx-auto mb-1 text-gray-600" />
            <div className="text-sm text-gray-700">Crowd Impact</div>
            <div className="text-xs text-gray-500">
              {(analytics.trends.crowdImpact * 100).toFixed(0)}% of entries
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function MoodTracker({ slotId, tripId, onMoodTracked, disabled = false }) {
  const [selectedMood, setSelectedMood] = useState(null);
  const [energyLevel, setEnergyLevel] = useState(5);
  const [feedback, setFeedback] = useState('');
  const [weatherImpact, setWeatherImpact] = useState(false);
  const [crowdImpact, setCrowdImpact] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  
  const moodHistory = useQuery(api.moodTracking.getMoodHistory, { tripId, days: 7 });
  const slotMood = useQuery(api.moodTracking.getSlotMood, { slotId });
  const trackMood = useMutation(api.moodTracking.trackMood);

  // Check if mood already tracked for this slot
  const alreadyTracked = !!slotMood;

  const handleSubmitMood = async () => {
    if (!selectedMood || isSubmitting || alreadyTracked) return;
    
    setIsSubmitting(true);
    
    try {
      await trackMood({
        slotId,
        tripId,
        mood: selectedMood,
        energyLevel,
        feedback: feedback.trim() || undefined,
        weatherImpact,
        crowdImpact,
      });
      
      onMoodTracked?.({ 
        mood: selectedMood, 
        energyLevel, 
        feedback 
      });
      
      // Reset form
      setSelectedMood(null);
      setEnergyLevel(5);
      setFeedback('');
      setWeatherImpact(false);
      setCrowdImpact(false);
      
    } catch (error) {
      console.error('Error tracking mood:', error);
      alert('Failed to save mood. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (alreadyTracked) {
    const mood = moods.find(m => m.id === slotMood.mood);
    
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-green-800 flex items-center gap-2">
            <Heart className="w-5 h-5" />
            Mood Tracked!
          </h3>
          <button
            onClick={() => setShowAnalytics(!showAnalytics)}
            className="text-sm text-green-700 hover:text-green-800 underline"
          >
            {showAnalytics ? 'Hide' : 'View'} Analytics
          </button>
        </div>
        
        <div className="flex items-center gap-4 mb-3">
          <div className="text-center">
            <div className="text-2xl mb-1">{mood?.icon}</div>
            <div className="text-sm font-medium text-green-700">{mood?.name}</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl mb-1">⚡</div>
            <div className="text-sm font-medium text-green-700">{slotMood.energyLevel}/10</div>
          </div>
        </div>
        
        {slotMood.feedback && (
          <div className="bg-white rounded p-3 mb-3">
            <p className="text-sm text-gray-700">"{slotMood.feedback}"</p>
          </div>
        )}
        
        {slotMood.suggestions && slotMood.suggestions.length > 0 && (
          <div className="bg-blue-50 rounded p-3">
            <h4 className="text-sm font-medium text-blue-800 mb-2">AI Suggestions:</h4>
            <ul className="space-y-1">
              {slotMood.suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm text-blue-700">• {suggestion}</li>
              ))}
            </ul>
          </div>
        )}
        
        {showAnalytics && (
          <div className="mt-4">
            <MoodAnalytics tripId={tripId} moodHistory={moodHistory} />
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mood Selection */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Heart className="w-5 h-5" />
          How was this activity?
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          {moods.map(mood => (
            <MoodButton
              key={mood.id}
              mood={mood}
              isSelected={selectedMood === mood.id}
              onClick={setSelectedMood}
              disabled={disabled || isSubmitting}
            />
          ))}
        </div>
        
        {/* Energy Level */}
        <div className="mb-6">
          <EnergySlider
            value={energyLevel}
            onChange={setEnergyLevel}
            disabled={disabled || isSubmitting}
          />
        </div>
        
        {/* Additional Feedback */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            How did it go? (Optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            disabled={disabled || isSubmitting}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={3}
            placeholder="Share your thoughts about this activity..."
          />
        </div>
        
        {/* Impact Factors */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            What affected your experience? (Optional)
          </label>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={weatherImpact}
                onChange={(e) => setWeatherImpact(e.target.checked)}
                disabled={disabled || isSubmitting}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Cloud className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">Weather conditions</span>
            </label>
            
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={crowdImpact}
                onChange={(e) => setCrowdImpact(e.target.checked)}
                disabled={disabled || isSubmitting}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Users className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-700">Crowd levels</span>
            </label>
          </div>
        </div>
        
        {/* Submit Button */}
        <button
          onClick={handleSubmitMood}
          disabled={!selectedMood || disabled || isSubmitting}
          className="w-full px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {isSubmitting ? 'Saving...' : 'Save Mood & Get AI Suggestions'}
        </button>
      </div>
      
      {/* Analytics Preview */}
      {moodHistory && moodHistory.length > 0 && (
        <MoodAnalytics tripId={tripId} moodHistory={moodHistory} />
      )}
    </div>
  );
}