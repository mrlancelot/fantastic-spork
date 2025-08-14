import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Plane, Hotel, UtensilsCrossed, Camera, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { useTripContext } from '../context/TripContext';
import { createItinerary, formatDateForAPI, mapBudgetToPriceRange, ItineraryRequest } from '../services/api';

interface LoadingStep {
  id: string;
  title: string;
  status: 'pending' | 'loading' | 'complete';
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const LoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const { formData, setItineraryData, setError: setContextError } = useTripContext();
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [estimatedTime, setEstimatedTime] = useState(30); // seconds
  const apiCallInProgress = useRef(false); // Track if API call is in progress
  
  const [steps, setSteps] = useState<LoadingStep[]>([
    {
      id: 'flights',
      title: 'Flights',
      status: 'pending',
      description: 'Searching best flight deals...',
      icon: Plane
    },
    {
      id: 'hotels',
      title: 'Hotels',
      status: 'pending',
      description: 'Finding perfect accommodations...',
      icon: Hotel
    },
    {
      id: 'restaurants',
      title: 'Restaurants',
      status: 'pending',
      description: 'Discovering local dining experiences...',
      icon: UtensilsCrossed
    },
    {
      id: 'attractions',
      title: 'Attractions',
      status: 'pending',
      description: 'Curating must-see attractions...',
      icon: Camera
    }
  ]);

  const callAPIWithRetry = async (retryCount = 0) => {
    if (!formData) {
      navigate('/');
      return;
    }

    // Prevent duplicate API calls (React StrictMode in dev causes double useEffect)
    if (apiCallInProgress.current && retryCount === 0) {
      console.log('API call already in progress, skipping duplicate call');
      return;
    }
    apiCallInProgress.current = true;

    try {
      setError(null);
      setIsRetrying(retryCount > 0);
      
      // Convert form data to API format
      const apiRequest: ItineraryRequest = {
        trip_type: formData.tripType === 'roundtrip' ? 'round_trip' : 'one_way',
        from_city: formData.fromCity,
        to_city: formData.destination,
        departure_date: formatDateForAPI(formData.startDate) || '',
        return_date: formData.tripType === 'roundtrip' ? formatDateForAPI(formData.endDate) : undefined,
        adults: formData.travelers,
        travel_class: formData.travelClass,
        interests: formData.interests.join(', '),
        price_range: mapBudgetToPriceRange(formData.budget),
      };

      // Simulate progress through steps
      const updateSteps = (stepIndex: number, status: 'loading' | 'complete') => {
        setSteps(prevSteps => {
          const newSteps = [...prevSteps];
          if (stepIndex >= 0 && stepIndex < newSteps.length) {
            newSteps[stepIndex].status = status;
          }
          return newSteps;
        });
      };

      // Start progress animation
      let currentStep = 0;
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          const newProgress = Math.min(prev + 3, 90);
          
          // Update steps based on progress
          if (newProgress > 25 && currentStep === 0) {
            updateSteps(0, 'loading');
            currentStep++;
          } else if (newProgress > 40 && currentStep === 1) {
            updateSteps(0, 'complete');
            updateSteps(1, 'loading');
            currentStep++;
          } else if (newProgress > 60 && currentStep === 2) {
            updateSteps(1, 'complete');
            updateSteps(2, 'loading');
            currentStep++;
          } else if (newProgress > 80 && currentStep === 3) {
            updateSteps(2, 'complete');
            updateSteps(3, 'loading');
            currentStep++;
          }
          
          return newProgress;
        });
      }, 600);

      // Countdown timer
      const timerInterval = setInterval(() => {
        setEstimatedTime(prev => Math.max(0, prev - 1));
      }, 1000);

      // Make the API call
      console.log('Calling API with:', apiRequest);
      const response = await createItinerary(apiRequest);
      
      // Clear intervals
      clearInterval(progressInterval);
      clearInterval(timerInterval);
      
      // Complete the progress
      setProgress(100);
      
      // Update all steps to complete
      setSteps(prevSteps => prevSteps.map(step => ({ ...step, status: 'complete' })));
      
      // Save response and navigate
      setItineraryData(response);
      apiCallInProgress.current = false; // Reset flag on success
      setTimeout(() => navigate('/itinerary'), 1000);
      
    } catch (err) {
      console.error('API Error:', err);
      
      // Clear any running intervals
      setProgress(0);
      setEstimatedTime(30);
      
      // Retry logic
      if (retryCount < 2) {
        setError('Connection failed. Retrying...');
        setTimeout(() => {
          apiCallInProgress.current = false; // Reset before retry
          callAPIWithRetry(retryCount + 1);
        }, 2000);
      } else {
        apiCallInProgress.current = false; // Reset flag on final failure
        setError(
          err instanceof Error 
            ? err.message 
            : 'Failed to create itinerary. Please try again.'
        );
        setContextError('Failed to create itinerary');
      }
    } finally {
      setIsRetrying(false);
    }
  };

  useEffect(() => {
    callAPIWithRetry();
  }, []);

  const getStatusIcon = (status: string) => {
    if (status === 'complete') {
      return <div className="h-6 w-6 rounded-full bg-primary-600 flex items-center justify-center">
        <div className="h-2 w-2 bg-white rounded-full" />
      </div>;
    } else if (status === 'loading') {
      return <Loader2 className="h-6 w-6 text-primary-600 animate-spin" />;
    } else {
      return <div className="h-6 w-6 rounded-full border-2 border-neutral-300" />;
    }
  };

  const getIconColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'text-primary-600';
      case 'loading':
        return 'text-primary-600';
      default:
        return 'text-neutral-400';
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col items-center justify-center">
      {/* Header */}
      <div className="mb-12">
        <div className="flex items-center justify-center space-x-2 mb-16">
          <MapPin className="h-7 w-7 text-primary-600" />
          <span className="text-lg font-semibold text-neutral-900">Waypoint</span>
        </div>

        {/* Title Section */}
        <div className="text-center mb-3">
          <h1 className="text-2xl font-semibold text-neutral-900 mb-2">
            {error ? 'Oops! Something went wrong' : 'Creating your itinerary'}
          </h1>
          <p className="text-neutral-600">
            {error 
              ? 'We encountered an issue while planning your trip' 
              : formData 
                ? `${formData.fromCity} → ${formData.destination}`
                : 'Planning your perfect trip'
            }
          </p>
          {formData && !error && (
            <p className="text-sm text-neutral-500">
              {formData.startDate && formData.endDate 
                ? `${formData.startDate.toLocaleDateString()} - ${formData.endDate.toLocaleDateString()}`
                : formData.startDate 
                  ? `Departing ${formData.startDate.toLocaleDateString()}`
                  : ''
              }
            </p>
          )}
          {!error && estimatedTime > 0 && (
            <p className="text-xs text-neutral-400 mt-2">
              Estimated time: {estimatedTime} seconds
            </p>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="w-full max-w-xl px-6">
        {error ? (
          <div className="bg-white rounded-xl shadow-sm border border-red-100 p-8">
            <div className="flex flex-col items-center">
              <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
              <p className="text-gray-700 mb-6 text-center">{error}</p>
              <div className="flex space-x-4">
                <button
                  onClick={() => {
                    setError(null);
                    callAPIWithRetry();
                  }}
                  disabled={isRetrying}
                  className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isRetrying ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <RefreshCw className="h-5 w-5" />
                  )}
                  <span>{isRetrying ? 'Retrying...' : 'Try Again'}</span>
                </button>
                <button
                  onClick={() => navigate('/')}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Go Back
                </button>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* Progress Bar */}
            <div className="mb-10">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-neutral-600">Searching travel data</span>
                <span className="text-sm font-medium text-neutral-900">{progress}%</span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Loading Steps */}
            <div className="space-y-3">
              {steps.map((step) => {
                const Icon = step.icon;
                return (
                  <div 
                    key={step.id} 
                    className={`flex items-center space-x-4 p-4 rounded-xl border transition-all duration-300 ${
                      step.status === 'complete' 
                        ? 'bg-primary-50 border-primary-200'
                        : step.status === 'loading'
                        ? 'bg-white border-primary-300 shadow-sm'
                        : 'bg-white border-neutral-200'
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {getStatusIcon(step.status)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <Icon className={`h-5 w-5 ${getIconColor(step.status)}`} />
                        <span className={`font-medium ${
                          step.status === 'pending' ? 'text-neutral-400' : 'text-neutral-900'
                        }`}>
                          {step.title}
                        </span>
                      </div>
                      <p className={`text-sm mt-1 ${
                        step.status === 'pending' ? 'text-neutral-400' : 'text-neutral-600'
                      }`}>
                        {step.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </main>
    </div>
  );
};