import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { RetroWindow, ProgressBar, theme } from '../components/retro';

export const LoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [tasks, setTasks] = useState([
    { name: 'Flights', status: 'loading', detail: 'Searching best flight deals...' },
    { name: 'Hotels', status: 'pending', detail: 'Ready to search' },
    { name: 'Restaurants', status: 'pending', detail: 'Ready to search' },
    { name: 'Attractions', status: 'pending', detail: 'Ready to search' }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => navigate('/itinerary'), 500);
          return 100;
        }
        return prev + 5;
      });
    }, 180);

    const taskInterval = setInterval(() => {
      setTasks(prev => {
        const loading = prev.findIndex(t => t.status === 'loading');
        if (loading === -1) return prev;
        
        const newTasks = [...prev];
        if (loading < prev.length) {
          newTasks[loading].status = 'done';
          newTasks[loading].detail = `Found ${Math.floor(Math.random() * 20) + 5} options!`;
          
          if (loading + 1 < prev.length) {
            newTasks[loading + 1].status = 'loading';
            newTasks[loading + 1].detail = `Searching best ${newTasks[loading + 1].name.toLowerCase()} options...`;
          }
        }
        return newTasks;
      });
    }, 1500);

    return () => {
      clearInterval(interval);
      clearInterval(taskInterval);
    };
  }, [navigate]);

  return (
    <div className={`min-h-screen ${theme.colors.canvas} p-8`}>
      <div className="max-w-2xl mx-auto">
        <RetroWindow variant="default" title="Creating your itinerary" icon={<Loader2 className="w-4 h-4 animate-spin" />}>
          <div className="space-y-6">
            <ProgressBar progress={progress} />
            
            <div className="space-y-3">
              {tasks.map((task, i) => (
                <div key={i} className="bg-white border-2 border-[#222222] rounded-[10px] p-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-[8px] border border-[#222222] flex items-center justify-center ${
                      task.status === 'done' ? 'bg-green-400' : 
                      task.status === 'loading' ? 'bg-yellow-400' : 
                      'bg-gray-200'
                    }`}>
                      {task.status === 'done' ? '✓' : 
                       task.status === 'loading' ? '...' : 
                       ''}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-sm">{task.name}</div>
                      <div className="text-xs text-[#4E4E4E]">{task.detail}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="text-center text-sm text-[#4E4E4E] border-t-2 border-[#ECE7DF] pt-3">
              This may take a few moments...
            </div>
          </div>
        </RetroWindow>
      </div>
    </div>
  );
};