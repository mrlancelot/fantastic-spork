import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { Plus, Clock, MapPin, Palette, Check, Play, X } from 'lucide-react';
import confetti from 'canvas-confetti';

const timeSlots = [
  { id: 'morning', name: 'Morning', time: '6:00-10:00', color: 'bg-orange-100 border-orange-200', icon: '🌅' },
  { id: 'midday', name: 'Midday', time: '10:00-15:00', color: 'bg-yellow-100 border-yellow-200', icon: '☀️' },
  { id: 'evening', name: 'Evening', time: '15:00-20:00', color: 'bg-blue-100 border-blue-200', icon: '🌆' },
  { id: 'night', name: 'Night', time: '20:00-24:00', color: 'bg-purple-100 border-purple-200', icon: '🌙' },
];

const themes = [
  { id: 'explore', name: 'Explore', icon: '🗺️', color: 'bg-green-500' },
  { id: 'eat', name: 'Eat', icon: '🍽️', color: 'bg-red-500' },
  { id: 'relax', name: 'Relax', icon: '🧘‍♀️', color: 'bg-blue-500' },
  { id: 'adventure', name: 'Adventure', icon: '🎯', color: 'bg-purple-500' },
];

function SortableSlot({ slot, onComplete, onEdit, onDelete }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: slot._id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-50 border-green-200';
      case 'in_progress': return 'bg-blue-50 border-blue-200';
      case 'pending': return 'bg-gray-50 border-gray-200';
      default: return 'bg-white border-gray-200';
    }
  };

  const getThemeIcon = (theme) => {
    const themeObj = themes.find(t => t.id === theme);
    return themeObj?.icon || '📍';
  };

  const triggerCelebration = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
  };

  const handleComplete = () => {
    if (slot.status !== 'completed') {
      triggerCelebration();
      onComplete(slot._id);
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`p-4 rounded-lg border-2 cursor-grab active:cursor-grabbing transition-all duration-200 ${getStatusColor(slot.status)}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getThemeIcon(slot.theme)}</span>
            <h3 className="font-semibold text-gray-800">{slot.title}</h3>
            {slot.status === 'completed' && (
              <Check className="w-4 h-4 text-green-600" />
            )}
          </div>
          
          {slot.description && (
            <p className="text-sm text-gray-600 mb-2">{slot.description}</p>
          )}
          
          <div className="flex flex-wrap gap-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {slot.startTime} - {slot.endTime}
            </span>
            {slot.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {slot.location.address}
              </span>
            )}
            {slot.budget && (
              <span className="bg-gray-100 px-2 py-1 rounded">
                Budget: ${slot.budget}
              </span>
            )}
          </div>
          
          {slot.packingItems && slot.packingItems.length > 0 && (
            <div className="mt-2">
              <span className="text-xs font-medium text-gray-600">Pack: </span>
              <span className="text-xs text-gray-500">
                {slot.packingItems.join(', ')}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-2 ml-4">
          {slot.status === 'pending' && (
            <button
              onClick={handleComplete}
              className="p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              title="Mark as complete"
            >
              <Check className="w-4 h-4" />
            </button>
          )}
          
          {slot.status === 'completed' && (
            <div className="p-2 bg-green-500 text-white rounded-lg">
              <Check className="w-4 h-4" />
            </div>
          )}
          
          <button
            onClick={() => onEdit(slot)}
            className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            title="Edit slot"
          >
            <Palette className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => onDelete(slot._id)}
            className="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            title="Delete slot"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {slot.planBOptions && slot.planBOptions.length > 0 && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-xs font-medium text-yellow-800 mb-1">Plan B Options:</p>
          {slot.planBOptions.map((option, index) => (
            <div key={index} className="text-xs text-yellow-700">
              • {option.title} ({option.reason})
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SlotCreationModal({ isOpen, onClose, onSave, selectedSlotType, tripId, date }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    startTime: '',
    endTime: '',
    theme: 'explore',
    location: null,
    budget: '',
    packingItems: [],
  });

  const [packingInput, setPackingInput] = useState('');

  useEffect(() => {
    if (selectedSlotType) {
      const slotInfo = timeSlots.find(s => s.id === selectedSlotType);
      if (slotInfo) {
        const [startTime] = slotInfo.time.split('-');
        setFormData(prev => ({
          ...prev,
          startTime,
          endTime: prev.endTime || startTime,
        }));
      }
    }
  }, [selectedSlotType]);

  const handleSave = () => {
    const slotData = {
      ...formData,
      tripId,
      date,
      slotType: selectedSlotType,
      color: timeSlots.find(s => s.id === selectedSlotType)?.color || 'bg-gray-100',
      packingItems: formData.packingItems,
    };
    
    onSave(slotData);
    onClose();
    setFormData({
      title: '',
      description: '',
      startTime: '',
      endTime: '',
      theme: 'explore',
      location: null,
      budget: '',
      packingItems: [],
    });
    setPackingInput('');
  };

  const addPackingItem = () => {
    if (packingInput.trim()) {
      setFormData(prev => ({
        ...prev,
        packingItems: [...prev.packingItems, packingInput.trim()]
      }));
      setPackingInput('');
    }
  };

  const removePackingItem = (index) => {
    setFormData(prev => ({
      ...prev,
      packingItems: prev.packingItems.filter((_, i) => i !== index)
    }));
  };

  if (!isOpen) return null;

  const selectedSlot = timeSlots.find(s => s.id === selectedSlotType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-screen overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">
          Create {selectedSlot?.name} Activity
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              placeholder="What will you do?"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              placeholder="Add details about your activity"
              rows={3}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Time</label>
              <input
                type="time"
                value={formData.startTime}
                onChange={(e) => setFormData(prev => ({ ...prev, startTime: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Time</label>
              <input
                type="time"
                value={formData.endTime}
                onChange={(e) => setFormData(prev => ({ ...prev, endTime: e.target.value }))}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Theme</label>
            <div className="grid grid-cols-2 gap-2">
              {themes.map(theme => (
                <button
                  key={theme.id}
                  onClick={() => setFormData(prev => ({ ...prev, theme: theme.id }))}
                  className={`p-2 rounded-lg border-2 flex items-center gap-2 ${
                    formData.theme === theme.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <span>{theme.icon}</span>
                  <span className="text-sm">{theme.name}</span>
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Budget (optional)</label>
            <input
              type="number"
              value={formData.budget}
              onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg"
              placeholder="Estimated cost"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Packing Items</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={packingInput}
                onChange={(e) => setPackingInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addPackingItem()}
                className="flex-1 p-2 border border-gray-300 rounded-lg"
                placeholder="Add item to pack"
              />
              <button
                onClick={addPackingItem}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Add
              </button>
            </div>
            {formData.packingItems.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.packingItems.map((item, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 px-2 py-1 rounded text-sm flex items-center gap-1"
                  >
                    {item}
                    <button
                      onClick={() => removePackingItem(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!formData.title.trim()}
            className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create Activity
          </button>
        </div>
      </div>
    </div>
  );
}

export default function DailyPlanner({ tripId, date }) {
  const slots = useQuery(api.slots.getTripSlots, { tripId, date }) || [];
  const createSlot = useMutation(api.slots.createSlot);
  const updateSlot = useMutation(api.slots.updateSlot);
  const deleteSlot = useMutation(api.slots.deleteSlot);
  const completeSlot = useMutation(api.slots.completeSlot);
  const reorderSlots = useMutation(api.slots.reorderSlots);

  const [showModal, setShowModal] = useState(false);
  const [selectedSlotType, setSelectedSlotType] = useState(null);

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

  const handleDragEnd = async (event) => {
    const { active, over } = event;

    if (active.id !== over?.id) {
      const oldIndex = slots.findIndex(slot => slot._id === active.id);
      const newIndex = slots.findIndex(slot => slot._id === over.id);
      
      const newSlots = arrayMove(slots, oldIndex, newIndex);
      const slotIds = newSlots.map(slot => slot._id);
      
      await reorderSlots({ tripId, date, slotIds });
    }
  };

  const handleCreateSlot = async (slotData) => {
    try {
      await createSlot(slotData);
    } catch (error) {
      console.error('Error creating slot:', error);
    }
  };

  const handleCompleteSlot = async (slotId) => {
    try {
      await completeSlot({
        slotId,
        moodRating: 4, // Default good mood
        energyLevel: 7, // Default good energy
      });
    } catch (error) {
      console.error('Error completing slot:', error);
    }
  };

  const handleEditSlot = (slot) => {
    // TODO: Implement edit functionality
    console.log('Edit slot:', slot);
  };

  const handleDeleteSlot = async (slotId) => {
    if (confirm('Are you sure you want to delete this activity?')) {
      try {
        await deleteSlot({ slotId });
      } catch (error) {
        console.error('Error deleting slot:', error);
      }
    }
  };

  const openCreateModal = (slotType) => {
    setSelectedSlotType(slotType);
    setShowModal(true);
  };

  const getSlotsByType = (slotType) => {
    return slots
      .filter(slot => slot.slotType === slotType)
      .sort((a, b) => a.order - b.order);
  };

  const completedSlots = slots.filter(slot => slot.status === 'completed').length;
  const totalSlots = slots.length;
  const progressPercent = totalSlots > 0 ? (completedSlots / totalSlots) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Progress Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-800">
            Daily Planner - {new Date(date).toLocaleDateString()}
          </h1>
          <div className="text-sm text-gray-600">
            {completedSlots} of {totalSlots} completed
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        
        {progressPercent === 100 && totalSlots > 0 && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 text-green-800">
              <Check className="w-5 h-5" />
              <span className="font-semibold">Perfect Day Complete!</span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              You've completed all activities for today. Great job! 🎉
            </p>
          </div>
        )}
      </div>

      {/* Time Slots */}
      <div className="grid gap-6">
        {timeSlots.map(timeSlot => {
          const slotActivities = getSlotsByType(timeSlot.id);
          
          return (
            <div key={timeSlot.id} className="bg-white rounded-lg p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{timeSlot.icon}</span>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-800">
                      {timeSlot.name}
                    </h2>
                    <p className="text-sm text-gray-600">{timeSlot.time}</p>
                  </div>
                </div>
                
                <button
                  onClick={() => openCreateModal(timeSlot.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add Activity
                </button>
              </div>
              
              {slotActivities.length > 0 ? (
                <DndContext
                  sensors={sensors}
                  collisionDetection={closestCenter}
                  onDragEnd={handleDragEnd}
                >
                  <SortableContext
                    items={slotActivities.map(slot => slot._id)}
                    strategy={verticalListSortingStrategy}
                  >
                    <div className="space-y-3">
                      {slotActivities.map(slot => (
                        <SortableSlot
                          key={slot._id}
                          slot={slot}
                          onComplete={handleCompleteSlot}
                          onEdit={handleEditSlot}
                          onDelete={handleDeleteSlot}
                        />
                      ))}
                    </div>
                  </SortableContext>
                </DndContext>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Plus className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No activities planned for {timeSlot.name.toLowerCase()}</p>
                  <p className="text-sm">Click "Add Activity" to get started</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <SlotCreationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSave={handleCreateSlot}
        selectedSlotType={selectedSlotType}
        tripId={tripId}
        date={date}
      />
    </div>
  );
}