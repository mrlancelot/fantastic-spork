import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

const variants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25',
  secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 shadow-lg shadow-secondary-600/25',
  accent: 'bg-accent-600 text-white hover:bg-accent-700 shadow-lg shadow-accent-600/25',
  ghost: 'bg-transparent hover:bg-neutral-100 text-neutral-800',
  outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
  gradient: 'bg-gradient-to-r from-primary-600 to-secondary-600 text-white hover:from-primary-700 hover:to-secondary-700 shadow-lg',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3',
  xl: 'px-8 py-4 text-lg',
};

export const Button = forwardRef(
  ({ className, variant = 'primary', size = 'md', children, asChild = false, loading = false, ...props }, ref) => {
    const Comp = asChild ? 'span' : motion.button;
    
    return (
      <Comp
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'relative overflow-hidden',
          variants[variant],
          sizes[size],
          className
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        {...props}
      >
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-inherit">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          </div>
        )}
        <span className={cn('relative', loading && 'invisible')}>{children}</span>
      </Comp>
    );
  }
);

Button.displayName = 'Button';