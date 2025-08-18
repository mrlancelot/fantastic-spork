import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Plane, Hotel, UtensilsCrossed, Camera, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { useTripContext } from '../context/TripContext';
import { 
  createItineraryJob, 
  checkJobStatus, 
  getItinerary,
  formatDateForAPI, 
  mapBudgetToPriceRange, 
  ItineraryRequest
} from '../services/api';

interface LoadingStep {
  id: string;
  title: string;
  status: 'pending' | 'loading' | 'complete';
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

// localStorage key for pending job
const PENDING_JOB_KEY = 'pending_itinerary_job';

interface PendingJob {
  job_id: string;
  itinerary_uuid: string;
  started_at: number;
  form_data: ItineraryRequest;
}

export const LoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const { formData, setItineraryData, setError: setContextError } = useTripContext();
  const [_jobId, setJobId] = useState<string | null>(null);
  const [_itineraryUuid, setItineraryUuid] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const pollingInterval = useRef<number | null>(null);
  const apiCallInProgress = useRef(false); // Track if API call is in progress
  
  const [liveMessage, setLiveMessage] = useState<string>('Preparing your itinerary...');
  
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

  // Clean up function
  const cleanup = () => {
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
      pollingInterval.current = null;
    }
  };

  // Poll job status
  const pollJobStatus = async (jobId: string, uuid: string) => {
    try {
      const status = await checkJobStatus(jobId);
      
      // Update progress based on status
      if (status.progress) {
        setLiveMessage(status.progress.message);
        
        // Update step status based on progress step
        const stepMap: Record<string, number> = {
          'flights': 0,
          'hotels': 1,
          'restaurants': 2,
          'activities': 3,
          'completing': 3
        };
        
        const currentStepIndex = stepMap[status.progress.step] ?? -1;
        if (currentStepIndex >= 0) {
          setSteps(prevSteps => {
            const newSteps = [...prevSteps];
            for (let i = 0; i < newSteps.length; i++) {
              if (i < currentStepIndex) {
                newSteps[i].status = 'complete';
              } else if (i === currentStepIndex) {
                newSteps[i].status = 'loading';
              } else {
                newSteps[i].status = 'pending';
              }
            }
            return newSteps;
          });
          
          // Update progress bar
          const progressPercent = Math.min(((currentStepIndex + 1) / 4) * 90, 90);
          setProgress(progressPercent);
        }
      }
      
      if (status.status === 'completed') {
        cleanup();
        setProgress(100);
        setSteps(prevSteps => prevSteps.map(step => ({ ...step, status: 'complete' })));
        
        // Fetch complete itinerary using itinerary_id from result
        const itineraryId = status.result?.itinerary_id;
        if (itineraryId) {
          const itinerary = await getItinerary(itineraryId);
          setItineraryData(itinerary);
        } else {
          console.error('No itinerary_id in completed job result');
          setError('Failed to retrieve itinerary ID');
          return;
        }
        
        // Clear localStorage
        localStorage.removeItem(PENDING_JOB_KEY);
        
        setTimeout(() => navigate('/itinerary'), 1000);
      } else if (status.status === 'failed') {
        cleanup();
        setError(status.error || 'Itinerary creation failed');
        localStorage.removeItem(PENDING_JOB_KEY);
      }
    } catch (err) {
      console.error('Polling error:', err);
      // Continue polling even if one check fails
    }
  };

  // Start a new itinerary job
  const startNewJob = async (apiRequest: ItineraryRequest, retry = 0) => {
    if (apiCallInProgress.current && retry === 0) {
      console.log('API call already in progress, skipping duplicate call');
      return;
    }
    apiCallInProgress.current = true;

    try {
      setError(null);
      setIsRetrying(retry > 0);
      setRetryCount(retry);

      // Create job
      console.log('Creating job with:', apiRequest);
      const jobResponse = await createItineraryJob(apiRequest);
      
      setJobId(jobResponse.job_id);
      setItineraryUuid(jobResponse.itinerary_uuid);
      
      // Save to localStorage for recovery
      const pendingJob: PendingJob = {
        job_id: jobResponse.job_id,
        itinerary_uuid: jobResponse.itinerary_uuid,
        started_at: Date.now(),
        form_data: apiRequest
      };
      localStorage.setItem(PENDING_JOB_KEY, JSON.stringify(pendingJob));
      
      // Start polling
      apiCallInProgress.current = false;
      pollingInterval.current = setInterval(() => {
        pollJobStatus(jobResponse.job_id, jobResponse.itinerary_uuid);
      }, jobResponse.polling_interval_seconds * 1000);
      
      // Initial status check
      await pollJobStatus(jobResponse.job_id, jobResponse.itinerary_uuid);
      
    } catch (err) {
      console.error('Job creation error:', err);
      apiCallInProgress.current = false;
      
      // Retry logic
      if (retry < 3) {
        setError('Connection failed. Retrying...');
        setTimeout(() => {
          startNewJob(apiRequest, retry + 1);
        }, 2000);
      } else {
        setError(
          err instanceof Error 
            ? err.message 
            : 'Failed to create itinerary. Please try again.'
        );
        setContextError('Failed to create itinerary');
        localStorage.removeItem(PENDING_JOB_KEY);
      }
    } finally {
      setIsRetrying(false);
    }
  };

  useEffect(() => {
    // Check for pending job in localStorage
    const pendingJobStr = localStorage.getItem(PENDING_JOB_KEY);
    
    if (pendingJobStr) {
      try {
        const pendingJob: PendingJob = JSON.parse(pendingJobStr);
        const ageMinutes = (Date.now() - pendingJob.started_at) / 1000 / 60;
        
        // Auto-resume if less than 2 minutes old
        if (ageMinutes < 2) {
          console.log('Resuming pending job:', pendingJob.job_id);
          setJobId(pendingJob.job_id);
          setItineraryUuid(pendingJob.itinerary_uuid);
          setLiveMessage('Resuming your itinerary generation...');
          
          // Start polling
          pollingInterval.current = setInterval(() => {
            pollJobStatus(pendingJob.job_id, pendingJob.itinerary_uuid);
          }, 5000);
          
          // Initial check
          pollJobStatus(pendingJob.job_id, pendingJob.itinerary_uuid);
          return;
        } else {
          // Job too old, clear it
          localStorage.removeItem(PENDING_JOB_KEY);
        }
      } catch (e) {
        console.error('Failed to parse pending job:', e);
        localStorage.removeItem(PENDING_JOB_KEY);
      }
    }
    
    // Start fresh job if we have form data
    if (formData) {
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
      
      startNewJob(apiRequest);
    } else {
      // No form data, redirect to home
      navigate('/');
    }
    
    // Cleanup on unmount
    return () => cleanup();
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
          {!error && liveMessage && (
            <p className="text-sm text-primary-600 mt-3 font-medium animate-pulse">
              {liveMessage}
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
                    if (formData) {
                      setError(null);
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
                      startNewJob(apiRequest, retryCount);
                    }
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