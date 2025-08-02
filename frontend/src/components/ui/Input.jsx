import { forwardRef } from 'react';
import { cn } from '../../utils/cn';

export const Input = forwardRef(
  ({ className, type, icon: Icon, error, ...props }, ref) => {
    return (
      <div className="relative">
        {Icon && (
          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400 pointer-events-none" />
        )}
        <input
          type={type}
          className={cn(
            'w-full rounded-lg border bg-white px-4 py-3 text-sm',
            'placeholder:text-neutral-400',
            'transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
            'hover:border-neutral-400',
            error
              ? 'border-red-500 focus:ring-red-500'
              : 'border-neutral-300',
            Icon && 'pl-11',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';