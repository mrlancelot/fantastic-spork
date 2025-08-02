import { motion } from 'framer-motion';
import { Bot, Map, ExternalLink, Sparkles, Globe, Shield } from 'lucide-react';
import { cn } from '../../utils/cn';

const features = [
  {
    icon: Bot,
    title: 'AI-Powered Planning',
    description: 'Smart agents research and plan your perfect itinerary with personalized recommendations',
    color: 'primary',
    delay: 0,
  },
  {
    icon: Map,
    title: 'Personalized Routes',
    description: 'Custom itineraries based on your preferences, budget, and travel style',
    color: 'secondary',
    delay: 0.1,
  },
  {
    icon: ExternalLink,
    title: 'Direct Booking',
    description: 'Book flights, hotels, and activities instantly with our trusted partners',
    color: 'accent',
    delay: 0.2,
  },
  {
    icon: Sparkles,
    title: 'Smart Suggestions',
    description: 'Get real-time recommendations based on weather, events, and local insights',
    color: 'primary',
    delay: 0.3,
  },
  {
    icon: Globe,
    title: 'Global Coverage',
    description: 'Explore destinations worldwide with comprehensive travel information',
    color: 'secondary',
    delay: 0.4,
  },
  {
    icon: Shield,
    title: 'Secure & Reliable',
    description: 'Your data is protected with enterprise-grade security and privacy',
    color: 'accent',
    delay: 0.5,
  },
];

const colorClasses = {
  primary: {
    bg: 'bg-primary-100',
    icon: 'text-primary-600',
    hover: 'hover:bg-primary-200',
    glow: 'hover:shadow-primary-500/20',
  },
  secondary: {
    bg: 'bg-secondary-100',
    icon: 'text-secondary-600',
    hover: 'hover:bg-secondary-200',
    glow: 'hover:shadow-secondary-500/20',
  },
  accent: {
    bg: 'bg-accent-100',
    icon: 'text-accent-600',
    hover: 'hover:bg-accent-200',
    glow: 'hover:shadow-accent-500/20',
  },
};

export function FeatureSection({ className }) {
  return (
    <div className={cn("py-20 px-4", className)}>
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Why Choose TravelAI?</span>
          </h2>
          <p className="text-xl text-neutral-600 max-w-3xl mx-auto">
            Experience the future of travel planning with our cutting-edge AI technology
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: feature.delay }}
              className="group"
            >
              <motion.div
                className={cn(
                  "relative p-6 rounded-2xl bg-white border border-neutral-200",
                  "transition-all duration-300",
                  "hover:shadow-2xl hover:-translate-y-1",
                  colorClasses[feature.color].glow
                )}
                whileHover={{ scale: 1.02 }}
              >
                {/* Animated background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-transparent to-neutral-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Icon */}
                <motion.div
                  className={cn(
                    "relative w-16 h-16 rounded-2xl flex items-center justify-center mb-4",
                    colorClasses[feature.color].bg,
                    colorClasses[feature.color].hover,
                    "transition-all duration-300"
                  )}
                  whileHover={{ rotate: 360, scale: 1.1 }}
                  transition={{ duration: 0.6 }}
                >
                  <feature.icon className={cn("w-8 h-8", colorClasses[feature.color].icon)} />
                </motion.div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-neutral-900 mb-2 relative">
                  {feature.title}
                </h3>
                <p className="text-neutral-600 relative">
                  {feature.description}
                </p>

                {/* Hover effect line */}
                <motion.div
                  className={cn(
                    "absolute bottom-0 left-0 right-0 h-1 rounded-b-2xl",
                    feature.color === 'primary' && "bg-gradient-to-r from-primary-500 to-primary-600",
                    feature.color === 'secondary' && "bg-gradient-to-r from-secondary-500 to-secondary-600",
                    feature.color === 'accent' && "bg-gradient-to-r from-accent-500 to-accent-600"
                  )}
                  initial={{ scaleX: 0 }}
                  whileHover={{ scaleX: 1 }}
                  transition={{ duration: 0.3 }}
                />
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}