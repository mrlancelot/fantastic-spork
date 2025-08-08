import React, { useState, useEffect } from 'react';
import { 
  Sun, 
  Cloud, 
  CloudRain, 
  CloudSnow, 
  Wind, 
  Droplets, 
  Thermometer,
  Eye,
  Umbrella,
  Shirt,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';

// Note: Weather API endpoint not yet implemented in backend
const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

const weatherIcons = {
  'sunny': Sun,
  'clear': Sun,
  'cloudy': Cloud,
  'rain': CloudRain,
  'snow': CloudSnow,
  'drizzle': CloudRain,
  'thunderstorm': CloudRain,
  'mist': Cloud,
  'fog': Cloud,
};

const clothingRecommendations = {
  hot: {
    temp: '> 25°C',
    items: ['Light t-shirt', 'Shorts', 'Sandals', 'Sunhat', 'Sunglasses'],
    color: 'text-red-600',
    icon: '🌡️',
  },
  warm: {
    temp: '20-25°C', 
    items: ['T-shirt', 'Light pants', 'Sneakers', 'Light jacket'],
    color: 'text-orange-600',
    icon: '☀️',
  },
  mild: {
    temp: '15-20°C',
    items: ['Long sleeves', 'Jeans', 'Closed shoes', 'Light jacket'],
    color: 'text-yellow-600', 
    icon: '🌤️',
  },
  cool: {
    temp: '10-15°C',
    items: ['Sweater', 'Long pants', 'Jacket', 'Closed shoes'],
    color: 'text-blue-600',
    icon: '🌥️',
  },
  cold: {
    temp: '< 10°C',
    items: ['Warm coat', 'Layers', 'Warm shoes', 'Hat', 'Gloves'],
    color: 'text-purple-600',
    icon: '🧥',
  },
};

function WeatherCard({ weather, date, isToday = false }) {
  const getWeatherIcon = (condition) => {
    const IconComponent = weatherIcons[condition.toLowerCase()] || Sun;
    return IconComponent;
  };

  const getClothingCategory = (temp) => {
    const temperature = parseInt(temp);
    if (temperature > 25) return clothingRecommendations.hot;
    if (temperature > 20) return clothingRecommendations.warm;
    if (temperature > 15) return clothingRecommendations.mild;
    if (temperature > 10) return clothingRecommendations.cool;
    return clothingRecommendations.cold;
  };

  const WeatherIcon = getWeatherIcon(weather.condition);
  const clothingRec = getClothingCategory(weather.temperature);
  const temp = parseInt(weather.temperature);

  return (
    <div className={`bg-white rounded-lg p-4 shadow-sm border-2 ${
      isToday ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className={`font-semibold ${isToday ? 'text-blue-800' : 'text-gray-800'}`}>
            {isToday ? 'Today' : new Date(date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
          </h3>
          <p className="text-sm text-gray-600 capitalize">{weather.condition}</p>
        </div>
        <div className="text-right">
          <WeatherIcon className="w-8 h-8 text-blue-500 mb-1" />
          <p className="text-2xl font-bold text-gray-800">{weather.temperature}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <Droplets className="w-4 h-4" />
          <span>{weather.humidity}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-600">
          <Wind className="w-4 h-4" />
          <span>{weather.wind}</span>
        </div>
      </div>

      {/* Clothing Recommendations */}
      <div className="pt-3 border-t border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <Shirt className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">What to wear</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {clothingRec.items.slice(0, 3).map((item, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
            >
              {item}
            </span>
          ))}
          {clothingRec.items.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
              +{clothingRec.items.length - 3}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function WeatherAlert({ weather, activities }) {
  const getAlerts = () => {
    const alerts = [];
    const temp = parseInt(weather.temperature);
    const humidity = parseInt(weather.humidity);
    const condition = weather.condition.toLowerCase();

    // Temperature alerts
    if (temp > 30) {
      alerts.push({
        type: 'warning',
        icon: AlertTriangle,
        message: 'Very hot weather - stay hydrated and seek shade',
        suggestions: ['Drink lots of water', 'Plan indoor activities during midday', 'Wear sunscreen']
      });
    } else if (temp < 5) {
      alerts.push({
        type: 'warning', 
        icon: AlertTriangle,
        message: 'Very cold weather - dress warmly',
        suggestions: ['Layer clothing', 'Wear warm accessories', 'Limit outdoor exposure']
      });
    }

    // Precipitation alerts
    if (condition.includes('rain') || condition.includes('storm')) {
      alerts.push({
        type: 'info',
        icon: Info,
        message: 'Rain expected - plan indoor alternatives',
        suggestions: ['Bring umbrella', 'Pack waterproof jacket', 'Have backup indoor plans']
      });
    }

    // High humidity alerts
    if (humidity > 80) {
      alerts.push({
        type: 'info',
        icon: Info,
        message: 'High humidity - may feel warmer than temperature',
        suggestions: ['Stay in air-conditioned spaces', 'Take breaks frequently', 'Light breathable clothing']
      });
    }

    // Activity-specific alerts
    if (activities) {
      activities.forEach(activity => {
        const activityLower = activity.toLowerCase();
        if (activityLower.includes('beach') && condition.includes('rain')) {
          alerts.push({
            type: 'warning',
            icon: Umbrella,
            message: 'Beach activities may be affected by rain',
            suggestions: ['Consider indoor alternatives', 'Check weather updates', 'Pack rain gear']
          });
        }
        if (activityLower.includes('hiking') && (temp > 32 || temp < 0)) {
          alerts.push({
            type: 'warning',
            icon: AlertTriangle,
            message: 'Extreme temperatures not ideal for hiking',
            suggestions: ['Reschedule for better weather', 'Take extra precautions', 'Inform others of plans']
          });
        }
      });
    }

    return alerts;
  };

  const alerts = getAlerts();

  if (alerts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-green-800">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Perfect weather conditions!</span>
        </div>
        <p className="text-green-700 text-sm mt-1">
          Great day for all your planned activities.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert, index) => {
        const IconComponent = alert.icon;
        const bgColor = alert.type === 'warning' ? 'bg-yellow-50 border-yellow-200' : 'bg-blue-50 border-blue-200';
        const textColor = alert.type === 'warning' ? 'text-yellow-800' : 'text-blue-800';
        const iconColor = alert.type === 'warning' ? 'text-yellow-600' : 'text-blue-600';

        return (
          <div key={index} className={`${bgColor} border rounded-lg p-4`}>
            <div className={`flex items-center gap-2 ${textColor} mb-2`}>
              <IconComponent className={`w-5 h-5 ${iconColor}`} />
              <span className="font-medium">{alert.message}</span>
            </div>
            {alert.suggestions && (
              <ul className={`text-sm ${textColor} ml-7 space-y-1`}>
                {alert.suggestions.map((suggestion, idx) => (
                  <li key={idx}>• {suggestion}</li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}

function ActivitySuggestions({ weather, currentActivities }) {
  const temp = parseInt(weather.temperature);
  const condition = weather.condition.toLowerCase();

  const getSuggestions = () => {
    const suggestions = [];

    // Weather-based suggestions
    if (condition.includes('sunny') || condition.includes('clear')) {
      if (temp > 20 && temp < 30) {
        suggestions.push({
          category: 'Outdoor',
          activities: ['Sightseeing', 'Walking tours', 'Park visits', 'Outdoor dining'],
          icon: '🌞'
        });
      }
      if (temp > 25) {
        suggestions.push({
          category: 'Beach/Water',
          activities: ['Beach activities', 'Swimming', 'Water sports', 'Boat tours'],
          icon: '🏖️'
        });
      }
    }

    if (condition.includes('rain') || condition.includes('cloudy')) {
      suggestions.push({
        category: 'Indoor',
        activities: ['Museums', 'Art galleries', 'Shopping centers', 'Indoor markets', 'Cafes'],
        icon: '🏛️'
      });
    }

    if (temp < 15) {
      suggestions.push({
        category: 'Cozy Indoor',
        activities: ['Hot springs', 'Spas', 'Cozy restaurants', 'Tea houses', 'Bookstores'],
        icon: '☕'
      });
    }

    if (condition.includes('snow')) {
      suggestions.push({
        category: 'Winter Activities',
        activities: ['Ice skating', 'Winter markets', 'Hot chocolate spots', 'Winter photography'],
        icon: '❄️'
      });
    }

    return suggestions;
  };

  const suggestions = getSuggestions();

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Eye className="w-5 h-5" />
        Weather-Aware Activity Suggestions
      </h3>
      
      {suggestions.length === 0 ? (
        <p className="text-gray-500 text-sm">
          Current activities look good for the weather conditions!
        </p>
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xl">{suggestion.icon}</span>
                <h4 className="font-medium text-gray-800">{suggestion.category}</h4>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {suggestion.activities.map((activity, idx) => (
                  <button
                    key={idx}
                    className="text-left px-3 py-2 bg-gray-50 hover:bg-blue-50 hover:text-blue-700 rounded-lg text-sm transition-colors"
                  >
                    {activity}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function WeatherPlanning({ location, date, activities }) {
  const [weatherData, setWeatherData] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWeather = async () => {
      if (!location || !date) return;

      setLoading(true);
      setError(null);

      try {
        // Weather API not yet implemented in backend
        setError('Weather service is currently unavailable. Please check back later.');

        // Forecast will be available once weather service is implemented
        setForecast([]);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [location, date]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-8 shadow-sm border border-gray-200">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-300 rounded w-1/4"></div>
          <div className="h-8 bg-gray-300 rounded w-1/2"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-16 bg-gray-300 rounded"></div>
            <div className="h-16 bg-gray-300 rounded"></div>
            <div className="h-16 bg-gray-300 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-2 text-red-800 mb-2">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-medium">Weather data unavailable</span>
        </div>
        <p className="text-red-700 text-sm">
          {error}. Please check your internet connection or try again later.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Weather Planning</h1>
        <p className="opacity-90">Smart recommendations based on weather conditions</p>
      </div>

      {/* Current Weather & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <WeatherCard weather={weatherData} date={date} isToday={true} />
        </div>
        <div className="lg:col-span-2">
          <WeatherAlert weather={weatherData} activities={activities} />
        </div>
      </div>

      {/* 5-Day Forecast */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">5-Day Forecast</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {forecast.map((day, index) => (
            <WeatherCard
              key={day.date}
              weather={day}
              date={day.date}
              isToday={index === 0}
            />
          ))}
        </div>
      </div>

      {/* Activity Suggestions */}
      <ActivitySuggestions weather={weatherData} currentActivities={activities} />

      {/* Packing Recommendations */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Shirt className="w-5 h-5" />
          Smart Packing List
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(clothingRecommendations).map(([key, rec]) => {
            const temp = parseInt(weatherData.temperature);
            const isRecommended = 
              (key === 'hot' && temp > 25) ||
              (key === 'warm' && temp <= 25 && temp > 20) ||
              (key === 'mild' && temp <= 20 && temp > 15) ||
              (key === 'cool' && temp <= 15 && temp > 10) ||
              (key === 'cold' && temp <= 10);

            return (
              <div 
                key={key}
                className={`p-4 rounded-lg border-2 transition-all ${
                  isRecommended 
                    ? 'border-green-500 bg-green-50' 
                    : 'border-gray-200 bg-gray-50 opacity-50'
                }`}
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{rec.icon}</span>
                  <div>
                    <h4 className="font-medium text-gray-800 capitalize">{key} Weather</h4>
                    <p className="text-sm text-gray-600">{rec.temp}</p>
                  </div>
                  {isRecommended && (
                    <CheckCircle className="w-5 h-5 text-green-600 ml-auto" />
                  )}
                </div>
                
                <div className="space-y-1">
                  {rec.items.map((item, index) => (
                    <div key={index} className="flex items-center gap-2 text-sm text-gray-700">
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}