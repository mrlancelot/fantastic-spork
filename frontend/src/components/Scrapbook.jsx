import React, { useState } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { 
  Camera, 
  BookOpen, 
  Video, 
  Mic, 
  Plus, 
  Search, 
  Filter, 
  MapPin, 
  Calendar,
  Eye,
  EyeOff,
  Edit3,
  Trash2,
  Share2,
  Download,
  Heart,
  MessageCircle,
  Tag,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const entryTypes = [
  { id: 'photo', name: 'Photo', icon: Camera, color: 'bg-pink-500' },
  { id: 'journal', name: 'Journal', icon: BookOpen, color: 'bg-green-500' },
  { id: 'video', name: 'Video', icon: Video, color: 'bg-red-500' },
  { id: 'audio', name: 'Audio', icon: Mic, color: 'bg-purple-500' },
];

function ScrapbookEntry({ entry, onEdit, onDelete, onClick }) {
  const typeInfo = entryTypes.find(t => t.id === entry.type);
  const Icon = typeInfo?.icon || BookOpen;

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <motion.div
      layoutId={entry._id}
      whileHover={{ y: -2 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-all"
      onClick={() => onClick(entry)}
    >
      {/* Entry Header */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full ${typeInfo?.color} flex items-center justify-center text-white`}>
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-medium text-gray-800">
                {entry.title || `${typeInfo?.name} Entry`}
              </h3>
              <p className="text-xs text-gray-500">{formatDate(entry.createdAt)}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            {entry.isPublic ? (
              <Eye className="w-4 h-4 text-green-500" title="Public" />
            ) : (
              <EyeOff className="w-4 h-4 text-gray-400" title="Private" />
            )}
          </div>
        </div>

        {/* Media Preview */}
        {entry.type === 'photo' && entry.mediaUrl && (
          <div className="mb-3 rounded-lg overflow-hidden bg-gray-100">
            <img 
              src={entry.thumbnailUrl || entry.mediaUrl}
              alt={entry.title || 'Photo'}
              className="w-full h-32 object-cover"
            />
          </div>
        )}

        {entry.type === 'video' && entry.thumbnailUrl && (
          <div className="mb-3 rounded-lg overflow-hidden bg-gray-100 relative">
            <img 
              src={entry.thumbnailUrl}
              alt={entry.title || 'Video thumbnail'}
              className="w-full h-32 object-cover"
            />
            <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
              <Video className="w-8 h-8 text-white" />
            </div>
          </div>
        )}

        {/* Content Preview */}
        {entry.content && (
          <div className="mb-3">
            <p className="text-sm text-gray-600 line-clamp-3">
              {entry.content}
            </p>
          </div>
        )}

        {/* Location */}
        {entry.location && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
            <MapPin className="w-3 h-3" />
            <span>{entry.location.name}</span>
          </div>
        )}

        {/* Tags */}
        {entry.tags && entry.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {entry.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
              >
                #{tag}
              </span>
            ))}
            {entry.tags.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
                +{entry.tags.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Entry Actions */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3 text-gray-500">
          <button className="flex items-center gap-1 text-xs hover:text-red-500">
            <Heart className="w-3 h-3" />
            <span>0</span>
          </button>
          <button className="flex items-center gap-1 text-xs hover:text-blue-500">
            <MessageCircle className="w-3 h-3" />
            <span>0</span>
          </button>
          <button className="flex items-center gap-1 text-xs hover:text-green-500">
            <Share2 className="w-3 h-3" />
          </button>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(entry);
            }}
            className="p-1 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
          >
            <Edit3 className="w-3 h-3" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(entry._id);
            }}
            className="p-1 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function CreateEntryModal({ isOpen, onClose, onSave, tripId, slotId }) {
  const [entryType, setEntryType] = useState('journal');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!content.trim()) return;
    
    setIsSaving(true);
    
    try {
      await onSave({
        tripId,
        slotId,
        type: entryType,
        title: title.trim() || undefined,
        content: content.trim(),
        tags: tags.length > 0 ? tags : undefined,
        isPublic,
      });
      
      // Reset form
      setTitle('');
      setContent('');
      setTags([]);
      setTagInput('');
      setIsPublic(false);
      setEntryType('journal');
      
      onClose();
    } catch (error) {
      console.error('Error saving entry:', error);
      alert('Failed to save entry. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const addTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !tags.includes(tag)) {
      setTags(prev => [...prev, tag]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(prev => prev.filter(tag => tag !== tagToRemove));
  };

  if (!isOpen) return null;

  const selectedType = entryTypes.find(t => t.id === entryType);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            Create {selectedType?.name} Entry
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Entry Type Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Entry Type
          </label>
          <div className="grid grid-cols-4 gap-3">
            {entryTypes.map(type => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => setEntryType(type.id)}
                  className={`p-3 rounded-lg border-2 transition-colors flex flex-col items-center gap-2 ${
                    entryType === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-full ${type.color} flex items-center justify-center text-white`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-medium">{type.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Title */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title (Optional)
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Give your entry a title..."
          />
        </div>

        {/* Content */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {entryType === 'photo' ? 'Caption' : 
             entryType === 'journal' ? 'Write your thoughts' : 
             'Description'}
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={6}
            placeholder={
              entryType === 'journal' 
                ? "What happened? How did you feel? What did you learn?"
                : "Describe this moment..."
            }
          />
        </div>

        {/* File Upload for Media Types */}
        {(entryType === 'photo' || entryType === 'video' || entryType === 'audio') && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload {entryType}
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <div className={`w-12 h-12 mx-auto mb-3 ${selectedType?.color} rounded-full flex items-center justify-center text-white`}>
                {React.createElement(selectedType?.icon, { className: "w-6 h-6" })}
              </div>
              <p className="text-gray-600 mb-2">
                Drag & drop your {entryType} here, or click to browse
              </p>
              <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                Choose File
              </button>
            </div>
          </div>
        )}

        {/* Tags */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTag()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add tags..."
            />
            <button
              onClick={addTag}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              Add
            </button>
          </div>
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  <Tag className="w-3 h-3" />
                  {tag}
                  <button
                    onClick={() => removeTag(tag)}
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Privacy */}
        <div className="mb-6">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Make this entry public</span>
          </label>
          <p className="text-xs text-gray-500 mt-1">
            Public entries can be seen by other travelers
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!content.trim() || isSaving}
            className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Saving...' : 'Save Entry'}
          </button>
        </div>
      </div>
    </div>
  );
}

function EntryDetailModal({ entry, onClose }) {
  if (!entry) return null;

  const typeInfo = entryTypes.find(t => t.id === entry.type);
  const Icon = typeInfo?.icon || BookOpen;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        layoutId={entry._id}
        className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full ${typeInfo?.color} flex items-center justify-center text-white`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-800">
                  {entry.title || `${typeInfo?.name} Entry`}
                </h2>
                <p className="text-sm text-gray-500">
                  {new Date(entry.createdAt).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Media */}
          {entry.type === 'photo' && entry.mediaUrl && (
            <div className="mb-6 rounded-lg overflow-hidden">
              <img 
                src={entry.mediaUrl}
                alt={entry.title || 'Photo'}
                className="w-full h-auto"
              />
            </div>
          )}

          {entry.type === 'video' && entry.mediaUrl && (
            <div className="mb-6 rounded-lg overflow-hidden bg-gray-100">
              <video 
                src={entry.mediaUrl}
                controls
                className="w-full h-auto"
              />
            </div>
          )}

          {entry.type === 'audio' && entry.mediaUrl && (
            <div className="mb-6">
              <audio 
                src={entry.mediaUrl}
                controls
                className="w-full"
              />
            </div>
          )}

          {/* Text Content */}
          <div className="mb-6">
            <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
              {entry.content}
            </p>
          </div>

          {/* Location */}
          {entry.location && (
            <div className="flex items-center gap-2 text-gray-600 mb-4">
              <MapPin className="w-4 h-4" />
              <span>{entry.location.name}</span>
            </div>
          )}

          {/* Tags */}
          {entry.tags && entry.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {entry.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                >
                  <Tag className="w-3 h-3" />
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Privacy Status */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {entry.isPublic ? (
              <>
                <Eye className="w-4 h-4" />
                <span>Public entry</span>
              </>
            ) : (
              <>
                <EyeOff className="w-4 h-4" />
                <span>Private entry</span>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 text-gray-600 hover:text-red-500">
              <Heart className="w-4 h-4" />
              <span>Like</span>
            </button>
            <button className="flex items-center gap-2 text-gray-600 hover:text-blue-500">
              <Share2 className="w-4 h-4" />
              <span>Share</span>
            </button>
            <button className="flex items-center gap-2 text-gray-600 hover:text-green-500">
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function Scrapbook({ tripId, slotId }) {
  const entries = useQuery(api.scrapbook.getUserScrapbook, { tripId }) || [];
  const addEntry = useMutation(api.scrapbook.addScrapbookEntry);
  const deleteEntry = useMutation(api.scrapbook.deleteScrapbookEntry);
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredEntries = entries
    .filter(entry => filterType === 'all' || entry.type === filterType)
    .filter(entry => 
      !searchTerm || 
      entry.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (entry.title && entry.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (entry.tags && entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
    )
    .sort((a, b) => b.createdAt - a.createdAt);

  const handleSaveEntry = async (entryData) => {
    try {
      await addEntry(entryData);
    } catch (error) {
      console.error('Error saving entry:', error);
      throw error;
    }
  };

  const handleDeleteEntry = async (entryId) => {
    if (confirm('Are you sure you want to delete this entry?')) {
      try {
        await deleteEntry({ entryId });
      } catch (error) {
        console.error('Error deleting entry:', error);
      }
    }
  };

  const getEntryTypeCount = (type) => {
    return entries.filter(entry => entry.type === type).length;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Travel Scrapbook</h1>
            <p className="opacity-90">Capture and preserve your travel memories</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Entry
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {entryTypes.map(type => {
          const Icon = type.icon;
          const count = getEntryTypeCount(type.id);
          
          return (
            <div key={type.id} className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-gray-800">{count}</p>
                  <p className="text-sm text-gray-600">{type.name}</p>
                </div>
                <div className={`w-10 h-10 rounded-full ${type.color} flex items-center justify-center text-white`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search entries..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              {entryTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name} ({getEntryTypeCount(type.id)})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Entries Grid */}
      {filteredEntries.length === 0 ? (
        <div className="bg-white rounded-lg p-12 text-center shadow-sm border border-gray-200">
          <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-500 mb-2">
            {searchTerm || filterType !== 'all' ? 'No entries found' : 'No entries yet'}
          </h3>
          <p className="text-gray-400 mb-4">
            {searchTerm || filterType !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'Start documenting your travel memories!'
            }
          </p>
          {!searchTerm && filterType === 'all' && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Create Your First Entry
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredEntries.map(entry => (
              <ScrapbookEntry
                key={entry._id}
                entry={entry}
                onEdit={() => {}} // TODO: Implement edit
                onDelete={handleDeleteEntry}
                onClick={setSelectedEntry}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      <CreateEntryModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSave={handleSaveEntry}
        tripId={tripId}
        slotId={slotId}
      />

      <AnimatePresence>
        {selectedEntry && (
          <EntryDetailModal
            entry={selectedEntry}
            onClose={() => setSelectedEntry(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}