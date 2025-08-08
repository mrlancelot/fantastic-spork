import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Clock, MapPin, CheckCircle, GripVertical } from 'lucide-react';
import WeatherCard from './WeatherCard';

// Sortable Slot Component
const SortableSlot = ({ slot, slotIndex, dayIndex, onComplete, completed }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: `${dayIndex}-${slotIndex}` });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getSlotColor = (timeSlot) => {
    switch (timeSlot) {
      case 'morning': return 'from-yellow-400 to-orange-500';
      case 'midday': return 'from-blue-400 to-blue-600';
      case 'evening': return 'from-purple-400 to-purple-600';
      case 'night': return 'from-indigo-500 to-purple-700';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  const getSlotEmoji = (timeSlot) => {
    switch (timeSlot) {
      case 'morning': return '🌅';
      case 'midday': return '☀️';
      case 'evening': return '🌆';
      case 'night': return '🌙';
      default: return '⏰';
    }
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: slotIndex * 0.1 }}
      className={`group relative bg-white rounded-xl shadow-lg border-2 ${
        completed ? 'border-green-300 bg-green-50' : 'border-gray-200 hover:border-purple-300'
      } transition-all duration-300 hover:shadow-xl`}
    >
      {/* Drag Handle */}
      <div 
        {...listeners}
        className="absolute left-2 top-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <GripVertical className="w-5 h-5 text-gray-400" />
      </div>

      <div className="p-6 pl-12">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium text-white bg-gradient-to-r ${getSlotColor(slot.time_slot)} mb-3`}>
              <span className="mr-2">{getSlotEmoji(slot.time_slot)}</span>
              {slot.time_slot.charAt(0).toUpperCase() + slot.time_slot.slice(1)}
            </div>
            
            <h3 className={`text-xl font-bold mb-2 ${completed ? 'text-green-800 line-through' : 'text-gray-800'}`}>
              {slot.activity}
            </h3>
            
            <p className={`text-gray-600 mb-3 ${completed ? 'text-green-600' : ''}`}>
              {slot.description}
            </p>

            <div className="flex items-center gap-4 text-sm text-gray-500">
              {slot.duration && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {slot.duration}
                </span>
              )}
              {slot.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {slot.location}
                </span>
              )}
            </div>
          </div>

          {/* Complete Button */}
          <motion.button
            onClick={() => onComplete(`${dayIndex}-${slotIndex}`, dayIndex, slotIndex)}
            disabled={completed}
            className={`p-3 rounded-full transition-all duration-300 ${
              completed 
                ? 'bg-green-100 text-green-600 cursor-default' 
                : 'bg-gray-100 hover:bg-purple-100 text-gray-600 hover:text-purple-600 hover:scale-110'
            }`}
            whileHover={completed ? {} : { scale: 1.1 }}
            whileTap={completed ? {} : { scale: 0.95 }}
          >
            <CheckCircle className={`w-6 h-6 ${completed ? 'fill-current' : ''}`} />
          </motion.button>
        </div>

        {/* Booking URL */}
        {slot.booking_url && (
          <motion.a
            href={slot.booking_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 font-medium"
            whileHover={{ x: 5 }}
          >
            Book Now →
          </motion.a>
        )}
      </div>
    </motion.div>
  );
};

export default function DailyPlannerView({ itinerary, day, dayIndex, onSlotComplete, completedSlots, onDragEnd }) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // If displaying full itinerary
  if (itinerary && itinerary.daily_plans) {
    return (
      <div className="space-y-8">
        {itinerary.daily_plans.map((dailyPlan, index) => (
          <motion.div
            key={dailyPlan.date}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-2xl shadow-xl overflow-hidden"
          >
            {/* Day Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold mb-1">
                    Day {index + 1}
                  </h2>
                  <p className="text-purple-100 text-lg">
                    {new Date(dailyPlan.date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long', 
                      day: 'numeric'
                    })}
                  </p>
                </div>
                {dailyPlan.weather && (
                  <WeatherCard weather={dailyPlan.weather} />
                )}
              </div>
            </div>

            {/* Slots */}
            <div className="p-6">
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={(event) => {
                  const { active, over } = event;
                  if (active.id !== over?.id) {
                    onDragEnd?.(active.id, over.id);
                  }
                }}
              >
                <SortableContext 
                  items={dailyPlan.slots.map((_, i) => `${index}-${i}`)}
                  strategy={verticalListSortingStrategy}
                >
                  <div className="space-y-4">
                    {dailyPlan.slots.map((slot, slotIndex) => (
                      <SortableSlot
                        key={`${index}-${slotIndex}`}
                        slot={slot}
                        slotIndex={slotIndex}
                        dayIndex={index}
                        onComplete={onSlotComplete}
                        completed={completedSlots?.has?.(`${index}-${slotIndex}`)}
                      />
                    ))}
                  </div>
                </SortableContext>
              </DndContext>
            </div>
          </motion.div>
        ))}
      </div>
    );
  }

  // If displaying single day
  if (day) {
    return (
      <div className="p-6">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={(event) => {
            const { active, over } = event;
            if (active.id !== over?.id) {
              onDragEnd?.(active.id, over.id);
            }
          }}
        >
          <SortableContext 
            items={day.slots.map((_, i) => `${dayIndex}-${i}`)}
            strategy={verticalListSortingStrategy}
          >
            <div className="space-y-4">
              {day.slots.map((slot, slotIndex) => (
                <SortableSlot
                  key={`${dayIndex}-${slotIndex}`}
                  slot={slot}
                  slotIndex={slotIndex}
                  dayIndex={dayIndex}
                  onComplete={onSlotComplete}
                  completed={completedSlots?.has?.(`${dayIndex}-${slotIndex}`)}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      </div>
    );
  }

  return null;
}