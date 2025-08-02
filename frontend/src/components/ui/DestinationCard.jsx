import { motion } from 'framer-motion';
import { MapPin, Star, Heart, Calendar, Users } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../utils/cn';
import { Badge } from './Badge';

export function DestinationCard({ 
  destination, 
  image, 
  rating, 
  price, 
  duration, 
  travelers, 
  tags = [], 
  onSelect,
  className 
}) {
  const [isLiked, setIsLiked] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  return (
    <motion.div
      className={cn(
        "group relative overflow-hidden rounded-2xl bg-white shadow-lg",
        "cursor-pointer transition-all duration-300",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      onClick={onSelect}
    >
      {/* Image container with parallax effect */}
      <div className="relative h-64 overflow-hidden">
        {/* Skeleton loader */}
        {!imageLoaded && (
          <div className="absolute inset-0 bg-neutral-200 animate-pulse" />
        )}
        
        <motion.img
          src={image}
          alt={destination}
          className="w-full h-full object-cover"
          onLoad={() => setImageLoaded(true)}
          initial={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          transition={{ duration: 0.6 }}
        />
        
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        
        {/* Like button */}
        <motion.button
          className="absolute top-4 right-4 p-2 rounded-full bg-white/20 backdrop-blur-md"
          onClick={(e) => {
            e.stopPropagation();
            setIsLiked(!isLiked);
          }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Heart
            className={cn(
              "w-5 h-5 transition-colors",
              isLiked ? "fill-red-500 text-red-500" : "text-white"
            )}
          />
        </motion.button>
        
        {/* Tags */}
        <div className="absolute top-4 left-4 flex flex-wrap gap-2">
          {tags.slice(0, 2).map((tag, index) => (
            <Badge
              key={index}
              variant="default"
              size="sm"
              className="bg-white/20 backdrop-blur-md text-white border-white/30"
            >
              {tag}
            </Badge>
          ))}
        </div>
        
        {/* Rating */}
        <div className="absolute bottom-4 left-4 flex items-center gap-1 text-white">
          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
          <span className="text-sm font-medium">{rating}</span>
        </div>
        
        {/* Price badge */}
        <div className="absolute bottom-4 right-4">
          <div className="bg-white/20 backdrop-blur-md rounded-lg px-3 py-1">
            <span className="text-white font-semibold">${price}</span>
            <span className="text-white/80 text-sm">/day</span>
          </div>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-6">
        <h3 className="text-xl font-semibold text-neutral-900 mb-2 group-hover:text-primary-600 transition-colors">
          {destination}
        </h3>
        
        <div className="flex items-center gap-4 text-sm text-neutral-600">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>{duration} days</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{travelers} travelers</span>
          </div>
        </div>
        
        {/* Hover effect - sliding action */}
        <motion.div
          className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-r from-primary-600 to-secondary-600 flex items-center justify-center"
          initial={{ y: 100 }}
          whileHover={{ y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <span className="text-white font-medium flex items-center gap-2">
            Explore Destination
            <MapPin className="w-4 h-4" />
          </span>
        </motion.div>
      </div>
    </motion.div>
  );
}