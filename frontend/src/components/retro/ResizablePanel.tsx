import React, { useState, useRef, useEffect, useCallback } from 'react';

interface ResizablePanelProps {
  children: React.ReactNode;
  minWidthPercent?: number;
  maxWidthPercent?: number;
  defaultWidthPercent?: number;
  storageKey?: string;
}

export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  children,
  minWidthPercent = 30,
  maxWidthPercent = 60,
  defaultWidthPercent = 35,
  storageKey = 'resizable-panel-width'
}) => {
  const [widthPercent, setWidthPercent] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(storageKey);
      return saved ? parseFloat(saved) : defaultWidthPercent;
    }
    return defaultWidthPercent;
  });
  
  const [isDragging, setIsDragging] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Save to localStorage whenever width changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, widthPercent.toString());
    }
  }, [widthPercent, storageKey]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const container = containerRef.current.parentElement;
    if (!container) return;

    const containerRect = container.getBoundingClientRect();
    const newWidthPercent = ((containerRect.right - e.clientX) / containerRect.width) * 100;
    
    // Constrain within min/max bounds
    const constrainedWidth = Math.min(maxWidthPercent, Math.max(minWidthPercent, newWidthPercent));
    setWidthPercent(constrainedWidth);
  }, [isDragging, minWidthPercent, maxWidthPercent]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div 
      ref={containerRef}
      className="relative flex h-full"
      style={{ width: `${widthPercent}%` }}
    >
      {/* Resize handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-2 bg-transparent cursor-col-resize z-10 -ml-1 flex items-center justify-center group"
        onMouseDown={handleMouseDown}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {/* Visual indicator - vertical dots */}
        <div className={`w-1 h-12 flex flex-col justify-center items-center gap-1 transition-opacity duration-200 ${
          isHovering || isDragging ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
        </div>
        
        {/* Invisible wider hit area */}
        <div className="absolute inset-0 w-4 -ml-1"></div>
      </div>
      
      {/* Panel content */}
      <div className="flex-1 pl-3 h-full">
        {children}
      </div>
    </div>
  );
};
