import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Plane, Hotel, UtensilsCrossed, Camera, Loader2 } from 'lucide-react';

interface LoadingStep {
  id: string;
  title: string;
  status: 'pending' | 'loading' | 'complete';
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const LoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(17);
  
  const [steps, setSteps] = useState<LoadingStep[]>([
    {
      id: 'flights',
      title: 'Flights',
      status: 'loading',
      description: 'Searching...',
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

  useEffect(() => {
    const progressStages = [
      { progress: 17, step: 0, description: 'Searching...' },
      { progress: 47, step: 0, description: 'Searching best flight deals...' },
      { progress: 47, step: 1, description: 'Found flights data!' },
      { progress: 73, step: 1, description: 'Found hotels data!' },
      { progress: 73, step: 2, description: 'Found restaurants data!' },
      { progress: 100, step: 3, description: 'Found attractions data!' }
    ];

    let stageIndex = 0;
    const interval = setInterval(() => {
      if (stageIndex < progressStages.length) {
        const stage = progressStages[stageIndex];
        setProgress(stage.progress);
        
        setSteps(prevSteps => {
          const newSteps = [...prevSteps];
          
          // Update current step
          if (stageIndex === 0) {
            newSteps[0].status = 'loading';
            newSteps[0].description = stage.description;
          } else if (stageIndex === 1) {
            newSteps[0].description = stage.description;
          } else if (stageIndex === 2) {
            newSteps[0].status = 'complete';
            newSteps[0].description = stage.description;
            newSteps[1].status = 'loading';
          } else if (stageIndex === 3) {
            newSteps[1].status = 'complete';
            newSteps[1].description = stage.description;
            newSteps[2].status = 'loading';
          } else if (stageIndex === 4) {
            newSteps[2].status = 'complete';
            newSteps[2].description = stage.description;
            newSteps[3].status = 'loading';
          } else if (stageIndex === 5) {
            newSteps[3].status = 'complete';
            newSteps[3].description = stage.description;
          }
          
          return newSteps;
        });
        
        stageIndex++;
      } else {
        clearInterval(interval);
        setTimeout(() => {
          navigate('/itinerary');
        }, 1000);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [navigate]);

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
            Creating your itinerary
          </h1>
          <p className="text-neutral-600">
            NYC → SFO
          </p>
          <p className="text-sm text-neutral-500">
            November 10, 1111 - November 10, 1111
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="w-full max-w-xl px-6">

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

        {/* Status Cards */}
        <div className="space-y-3">
          {steps.map((step) => {
            const StatusIcon = step.icon;
            return (
              <div key={step.id} className="bg-white rounded-xl border border-neutral-200 p-4 shadow-xs">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center ${step.status === 'loading' ? 'bg-primary-50' : ''}`}>
                    {step.status === 'loading' ? (
                      <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                    ) : (
                      <StatusIcon className={`w-5 h-5 ${getIconColor(step.status)}`} />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-neutral-900">{step.title}</span>
                      {step.status === 'loading' && (
                        <span className="text-xs text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full">Searching...</span>
                      )}
                    </div>
                    <div className="text-sm text-neutral-500">{step.description}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Message */}
        <div className="text-center mt-12">
          <div className="inline-flex items-center gap-2 text-sm text-neutral-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>This may take a few moments...</span>
          </div>
        </div>
      </main>
    </div>
  );
};