import { motion } from 'framer-motion';
import { Thermometer, Droplets, Wind } from 'lucide-react';

const WeatherCard = ({ weather }) => {
  if (!weather) return null;

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-3 text-white"
    >
      <div className="flex items-center gap-3">
        <div className="text-2xl">
          {weather.icon}
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Thermometer className="w-4 h-4" />
            <span className="font-medium">{weather.temperature}</span>
          </div>
          <div className="text-xs opacity-90">
            {weather.condition}
          </div>
        </div>
        <div className="text-xs space-y-1 opacity-75">
          <div className="flex items-center gap-1">
            <Droplets className="w-3 h-3" />
            <span>{weather.humidity}</span>
          </div>
          <div className="flex items-center gap-1">
            <Wind className="w-3 h-3" />
            <span>{weather.wind}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default WeatherCard;