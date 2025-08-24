import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { RetroWindow, ProgressBar, theme } from '../components/retro';
import { ApiService, ItineraryRequest, ItineraryResponse } from '../services/api';

export const LoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('Initializing...');
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const { apiRequest, formData } = location.state as { 
    apiRequest: ItineraryRequest; 
    formData: any 
  } || {};

  const tasks = [
    { name: 'Flights', detail: 'Searching best flight deals...' },
    { name: 'Hotels', detail: 'Finding accommodation options...' },
    { name: 'Restaurants', detail: 'Discovering local cuisine...' },
    { name: 'Attractions', detail: 'Planning activities and sightseeing...' },
    { name: 'Itinerary', detail: 'Finalizing your personalized itinerary...' }
  ];

  const getTaskFromProgress = (progress: number) => {
    if (progress < 20) return tasks[0];
    if (progress < 40) return tasks[1];
    if (progress < 60) return tasks[2];
    if (progress < 80) return tasks[3];
    return tasks[4];
  };

  useEffect(() => {
    if (!apiRequest) {
      navigate('/');
      return;
    }

    let isCancelled = false;

    const createItinerary = async () => {
      try {
        setError(null);
        setCurrentTask('Starting itinerary creation...');
        
        // Make the API call
        const response: ItineraryResponse = await ApiService.createItinerary(apiRequest);
        
        // Only proceed if component hasn't been unmounted
        if (!isCancelled) {
          // Navigate to itinerary page with the response data
          navigate('/itinerary', { 
            state: { 
              itineraryData: response,
              formData 
            } 
          });
        }
        
      } catch (error) {
        if (!isCancelled) {
          console.error('Error creating itinerary:', error);
          setError(error instanceof Error ? error.message : 'Failed to create itinerary');
          
          // Auto-retry up to 2 times for network errors
          if (retryCount < 2 && (error instanceof Error && error.message.includes('fetch'))) {
            setTimeout(() => {
              if (!isCancelled) {
                setRetryCount(prev => prev + 1);
                setProgress(0);
                createItinerary();
              }
            }, 3000);
          }
        }
      }
    };

    // Simulate progress updates while API is working
    const progressInterval = setInterval(() => {
      if (!isCancelled) {
        setProgress(prev => {
          const newProgress = Math.min(prev + Math.random() * 8 + 2, 95); // Don't go to 100% until API completes
          const currentTaskData = getTaskFromProgress(newProgress);
          setCurrentTask(currentTaskData.detail);
          return newProgress;
        });
      }
    }, 1000);

    createItinerary();

    return () => {
      isCancelled = true;
      clearInterval(progressInterval);
    };
  }, [apiRequest, navigate, formData]); // Removed retryCount from dependencies

  const handleRetry = () => {
    setError(null);
    setProgress(0);
    setRetryCount(0);
    window.location.reload(); // Simple retry by reloading
  };

  const handleGoBack = () => {
    navigate('/', { state: { formData } });
  };

  if (error) {
    return (
      <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
        <div className="max-w-2xl mx-auto">
          <RetroWindow variant="error" title="Itinerary Creation Failed" icon={<Loader2 className="w-4 h-4" />}>
            <div className="space-y-4">
              <div className="bg-red-50 border-2 border-[#222222] rounded-[10px] p-4">
                <h3 className="font-semibold text-red-800 mb-2">Something went wrong</h3>
                <p className="text-sm text-red-700">{error}</p>
                {retryCount > 0 && (
                  <p className="text-xs text-red-600 mt-2">Retry attempt: {retryCount}/2</p>
                )}
              </div>
              
              <div className="flex gap-2">
                <button 
                  onClick={handleRetry}
                  className="flex-1 px-4 py-2 bg-[#4A90E2] text-white rounded-[8px] border-2 border-[#222222] font-medium hover:bg-[#357ABD] transition-colors"
                >
                  Try Again
                </button>
                <button 
                  onClick={handleGoBack}
                  className="flex-1 px-4 py-2 bg-white text-[#222222] rounded-[8px] border-2 border-[#222222] font-medium hover:bg-gray-50 transition-colors"
                >
                  Go Back
                </button>
              </div>
            </div>
          </RetroWindow>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-2xl mx-auto">
        <RetroWindow variant="default" title="Creating your itinerary" icon={<Loader2 className="w-4 h-4 animate-spin" />}>
          <div className="space-y-6">
            <ProgressBar progress={progress} />
            
            <div className="space-y-3">
              {tasks.map((task, i) => {
                const taskProgress = (progress / 100) * tasks.length;
                const isCompleted = taskProgress > i + 1;
                const isActive = taskProgress > i && taskProgress <= i + 1;
                
                return (
                  <div key={i} className="bg-white border-2 border-[#222222] rounded-[10px] p-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-[8px] border border-[#222222] flex items-center justify-center ${
                        isCompleted ? 'bg-green-400' : 
                        isActive ? 'bg-yellow-400' : 
                        'bg-gray-200'
                      }`}>
                        {isCompleted ? '✓' : 
                         isActive ? '...' : 
                         ''}
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-sm">{task.name}</div>
                        <div className="text-xs text-[#4E4E4E]">
                          {isActive ? currentTask : task.detail}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="text-center text-sm text-[#4E4E4E] border-t-2 border-[#ECE7DF] pt-3">
              Our AI agents are working hard to create your perfect itinerary...
              <br />
              <span className="text-xs">This may take 2-3 minutes</span>
            </div>
          </div>
        </RetroWindow>
      </div>
    </div>
  );
};