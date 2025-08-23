import React, { useState, useRef, useEffect, useCallback } from 'react';
import { X, MessageSquare } from 'lucide-react';

interface ResizablePanelProps {
  children: React.ReactNode;
  minWidthPercent?: number;
  maxWidthPercent?: number;
  defaultWidthPercent?: number;
  storageKey?: string;
  mobileBreakpoint?: number;
}

export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  children,
  minWidthPercent = 30,
  maxWidthPercent = 60,
  defaultWidthPercent = 35,
  storageKey = 'resizable-panel-width',
  mobileBreakpoint = 768
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
  const [isMobile, setIsMobile] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Check if screen is mobile size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < mobileBreakpoint);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [mobileBreakpoint]);

  // Save to localStorage whenever width changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(storageKey, widthPercent.toString());
    }
  }, [widthPercent, storageKey]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (isMobile) return;
    e.preventDefault();
    setIsDragging(true);
  }, [isMobile]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current || isMobile) return;

    const container = containerRef.current.parentElement;
    if (!container) return;

    const containerRect = container.getBoundingClientRect();
    const newWidthPercent = ((containerRect.right - e.clientX) / containerRect.width) * 100;
    
    // Constrain within min/max bounds
    const constrainedWidth = Math.min(maxWidthPercent, Math.max(minWidthPercent, newWidthPercent));
    setWidthPercent(constrainedWidth);
  }, [isDragging, minWidthPercent, maxWidthPercent, isMobile]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging && !isMobile) {
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
  }, [isDragging, handleMouseMove, handleMouseUp, isMobile]);

  // Mobile modal overlay
  if (isMobile) {
    return (
      <>
        {/* Mobile toggle button */}
        <button
          onClick={() => setIsModalOpen(true)}
          className="fixed bottom-4 right-4 z-40 bg-[#4A90E2] text-white p-3 rounded-full border-2 border-[#222222] shadow-[0_4px_0_0_#222222] hover:shadow-[0_2px_0_0_#222222] hover:translate-y-[2px] transition-all"
        >
          <MessageSquare className="w-6 h-6" />
        </button>

        {/* Mobile modal */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-end">
            {/* Backdrop */}
            <div 
              className="absolute inset-0 bg-black bg-opacity-50"
              onClick={() => setIsModalOpen(false)}
            />
            
            {/* Modal content */}
            <div className="relative w-full bg-white rounded-t-[20px] border-2 border-[#222222] shadow-[0_-4px_0_0_#222222] max-h-[80vh] overflow-hidden">
              {/* Modal header */}
              <div className="flex items-center justify-between p-4 border-b-2 border-[#222222] bg-purple-400">
                <h3 className="font-semibold text-white">Travel Assistant</h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="w-8 h-8 bg-red-400 border border-black rounded-sm flex items-center justify-center hover:bg-red-500"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              {/* Modal body */}
              <div className="p-4 overflow-y-auto max-h-[calc(80vh-80px)]">
                {children}
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // Desktop resizable panel
  return (
    <div 
      ref={containerRef}
      className="relative flex"
      style={{ width: `${widthPercent}%` }}
    >
      {/* Resize handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 bg-transparent hover:bg-blue-300 cursor-col-resize z-10 -ml-0.5"
        onMouseDown={handleMouseDown}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {/* Visual indicator */}
        <div className={`absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1 h-8 bg-gray-300 rounded-full transition-opacity ${
          isHovering || isDragging ? 'opacity-100' : 'opacity-0'
        }`} />
      </div>
      
      {/* Panel content */}
      <div className="flex-1 pl-2">
        {children}
      </div>
    </div>
  );
};
