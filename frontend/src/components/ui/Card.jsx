import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export const Card = forwardRef(({ className, children, hover = true, glass = false, ...props }, ref) => (
  <motion.div
    ref={ref}
    className={cn(
      'rounded-xl overflow-hidden',
      glass ? 'glass' : 'bg-white shadow-lg',
      hover && 'hover-lift cursor-pointer',
      className
    )}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    {...props}
  >
    {children}
  </motion.div>
));

Card.displayName = 'Card';

export const CardHeader = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('px-6 py-4', className)} {...props} />
));

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef(({ className, ...props }, ref) => (
  <h3 ref={ref} className={cn('text-xl font-semibold tracking-tight text-neutral-900', className)} {...props} />
));

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef(({ className, ...props }, ref) => (
  <p ref={ref} className={cn('text-sm text-neutral-600 mt-1', className)} {...props} />
));

CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('px-6 pb-6', className)} {...props} />
));

CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('flex items-center px-6 py-4 bg-neutral-50', className)} {...props} />
));

CardFooter.displayName = 'CardFooter';