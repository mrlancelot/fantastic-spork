import React from 'react';
import { Check, Loader2 } from 'lucide-react';
import { ProgressStep } from '../types';

interface ProgressCardProps {
  steps: ProgressStep[];
}

export const ProgressCard: React.FC<ProgressCardProps> = ({ steps }) => {
  return (
    <div className="card p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Creating Your Perfect Itinerary
        </h2>
        <p className="text-gray-600">
          Please wait while we craft a personalized travel plan just for you
        </p>
      </div>

      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              {step.completed ? (
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <Check className="w-5 h-5 text-white" />
                </div>
              ) : step.current ? (
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                </div>
              ) : (
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <span className="text-gray-500 text-sm font-medium">{index + 1}</span>
                </div>
              )}
            </div>
            
            <div className="flex-1">
              <h3 className={`font-medium ${
                step.completed ? 'text-green-700' : 
                step.current ? 'text-primary-700' : 
                'text-gray-500'
              }`}>
                {step.title}
              </h3>
              <p className={`text-sm mt-1 ${
                step.completed ? 'text-green-600' : 
                step.current ? 'text-primary-600' : 
                'text-gray-400'
              }`}>
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8">
        <div className="bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${(steps.filter(s => s.completed).length / steps.length) * 100}%` 
            }}
          />
        </div>
        <p className="text-center text-sm text-gray-500 mt-2">
          {steps.filter(s => s.completed).length} of {steps.length} steps completed
        </p>
      </div>
    </div>
  );
};