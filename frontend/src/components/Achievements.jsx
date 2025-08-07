import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { Trophy, Star, Award, Target, Users, Compass, Sparkles, Lock, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';

const achievementCategories = [
  { id: 'completion', name: 'Completion', icon: Target, color: 'bg-green-500' },
  { id: 'exploration', name: 'Exploration', icon: Compass, color: 'bg-blue-500' },
  { id: 'social', name: 'Social', icon: Users, color: 'bg-purple-500' },
  { id: 'special', name: 'Special', icon: Sparkles, color: 'bg-yellow-500' },
];

const tierColors = {
  bronze: 'from-orange-400 to-orange-600',
  silver: 'from-gray-400 to-gray-600', 
  gold: 'from-yellow-400 to-yellow-600',
  platinum: 'from-purple-400 to-purple-600',
};

const tierIcons = {
  bronze: '🥉',
  silver: '🥈',
  gold: '🥇',
  platinum: '💎',
};

function AchievementCard({ achievement, onClick, showProgress = true }) {
  const progressPercent = achievement.maxProgress > 0 
    ? (achievement.progress / achievement.maxProgress) * 100 
    : (achievement.completed ? 100 : 0);

  const handleClick = () => {
    if (achievement.completed) {
      // Trigger celebration for completed achievements
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 }
      });
    }
    onClick(achievement);
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}
      className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all ${
        achievement.completed
          ? 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-orange-50 shadow-lg'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
      }`}
    >
      {/* Tier indicator */}
      <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-br ${tierColors[achievement.tier]} flex items-center justify-center text-white text-xs font-bold shadow-lg`}>
        {tierIcons[achievement.tier]}
      </div>

      {/* Achievement icon */}
      <div className="text-4xl mb-3 text-center">
        {achievement.completed ? achievement.icon : (
          <div className="relative">
            <span className="opacity-30">{achievement.icon}</span>
            {!achievement.completed && (
              <Lock className="absolute inset-0 m-auto w-6 h-6 text-gray-400" />
            )}
          </div>
        )}
      </div>

      {/* Achievement info */}
      <div className="text-center">
        <h3 className={`font-semibold mb-1 ${
          achievement.completed ? 'text-yellow-800' : 'text-gray-800'
        }`}>
          {achievement.name}
        </h3>
        <p className={`text-sm mb-3 ${
          achievement.completed ? 'text-yellow-700' : 'text-gray-600'
        }`}>
          {achievement.description}
        </p>

        {/* Progress bar */}
        {showProgress && achievement.maxProgress > 1 && (
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>{achievement.progress}</span>
              <span>{achievement.maxProgress}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div 
                className={`h-2 rounded-full ${
                  achievement.completed ? 'bg-yellow-500' : 'bg-blue-500'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </div>
          </div>
        )}

        {/* Points */}
        <div className={`flex items-center justify-center gap-1 text-sm font-medium ${
          achievement.completed ? 'text-yellow-700' : 'text-gray-600'
        }`}>
          <Star className="w-4 h-4" />
          <span>{achievement.points} points</span>
        </div>

        {/* Completion date */}
        {achievement.completed && achievement.completedAt && (
          <p className="text-xs text-yellow-600 mt-2">
            Earned {new Date(achievement.completedAt).toLocaleDateString()}
          </p>
        )}
      </div>
    </motion.div>
  );
}

function StatsCard({ title, value, icon: Icon, color, subtitle }) {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-full ${color} flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function LevelProgress({ currentLevel, totalPoints, nextLevelPoints }) {
  const currentLevelStart = (currentLevel - 1) * 1000;
  const currentLevelEnd = currentLevel * 1000;
  const progressInLevel = totalPoints - currentLevelStart;
  const levelProgressPercent = (progressInLevel / 1000) * 100;

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Level {currentLevel}</h3>
          <p className="text-sm text-gray-600">{totalPoints} total points</p>
        </div>
        <div className="text-4xl">
          {currentLevel >= 10 ? '👑' : currentLevel >= 5 ? '⭐' : '🌟'}
        </div>
      </div>
      
      <div className="mb-2">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress to Level {currentLevel + 1}</span>
          <span>{nextLevelPoints} points to go</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${levelProgressPercent}%` }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </div>
      </div>
      
      <div className="text-center">
        <p className="text-xs text-gray-500">
          {progressInLevel} / 1000 points in current level
        </p>
      </div>
    </div>
  );
}

function AchievementDetail({ achievement, onClose }) {
  if (!achievement) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.5, opacity: 0 }}
        className="bg-white rounded-xl p-8 max-w-md w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-center">
          {/* Achievement icon with animation */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="text-8xl mb-4"
          >
            {achievement.icon}
          </motion.div>
          
          {/* Tier badge */}
          <div className={`inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r ${tierColors[achievement.tier]} text-white text-sm font-medium mb-4`}>
            <span className="mr-1">{tierIcons[achievement.tier]}</span>
            {achievement.tier.charAt(0).toUpperCase() + achievement.tier.slice(1)} Tier
          </div>
          
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {achievement.name}
          </h2>
          
          <p className="text-gray-600 mb-6">
            {achievement.description}
          </p>
          
          {/* Points and stats */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-center gap-4 text-sm">
              <div className="text-center">
                <Star className="w-5 h-5 mx-auto mb-1 text-yellow-500" />
                <p className="font-semibold text-gray-800">{achievement.points}</p>
                <p className="text-gray-600">Points</p>
              </div>
              
              {achievement.maxProgress > 1 && (
                <div className="text-center">
                  <Target className="w-5 h-5 mx-auto mb-1 text-blue-500" />
                  <p className="font-semibold text-gray-800">
                    {achievement.progress}/{achievement.maxProgress}
                  </p>
                  <p className="text-gray-600">Progress</p>
                </div>
              )}
              
              <div className="text-center">
                <Award className="w-5 h-5 mx-auto mb-1 text-purple-500" />
                <p className="font-semibold text-gray-800">{achievement.category}</p>
                <p className="text-gray-600">Category</p>
              </div>
            </div>
          </div>
          
          {achievement.completed && achievement.completedAt && (
            <p className="text-sm text-green-600 mb-4">
              🎉 Earned on {new Date(achievement.completedAt).toLocaleDateString()}
            </p>
          )}
          
          <button
            onClick={onClose}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
          >
            {achievement.completed ? 'Awesome!' : 'Keep Going!'}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function Achievements() {
  const achievements = useQuery(api.achievements.getUserAchievements) || [];
  const userStats = useQuery(api.achievements.getUserStats);
  const initializeAchievements = useMutation(api.achievements.initializeUserAchievements);
  
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [newAchievementAlert, setNewAchievementAlert] = useState(null);

  // Initialize achievements if none exist
  useEffect(() => {
    if (achievements.length === 0) {
      initializeAchievements();
    }
  }, [achievements.length, initializeAchievements]);

  // Check for new achievements (in real app, this would come from a subscription)
  useEffect(() => {
    const recentAchievement = achievements.find(a => 
      a.completed && 
      a.completedAt && 
      Date.now() - a.completedAt < 5000 // Within last 5 seconds
    );
    
    if (recentAchievement && recentAchievement._id !== newAchievementAlert?.id) {
      setNewAchievementAlert(recentAchievement);
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
      });
      
      // Auto-hide after 5 seconds
      setTimeout(() => setNewAchievementAlert(null), 5000);
    }
  }, [achievements, newAchievementAlert]);

  const filteredAchievements = selectedCategory === 'all'
    ? achievements
    : achievements.filter(a => a.category === selectedCategory);

  const completedAchievements = achievements.filter(a => a.completed);
  const inProgressAchievements = achievements.filter(a => !a.completed && a.progress > 0);

  if (!userStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* New Achievement Alert */}
      <AnimatePresence>
        {newAchievementAlert && (
          <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.9 }}
            className="fixed top-4 right-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-white p-4 rounded-lg shadow-lg z-50 max-w-sm"
          >
            <div className="flex items-center gap-3">
              <div className="text-2xl">{newAchievementAlert.icon}</div>
              <div>
                <h4 className="font-semibold">Achievement Unlocked!</h4>
                <p className="text-sm opacity-90">{newAchievementAlert.name}</p>
                <p className="text-xs opacity-75">+{newAchievementAlert.points} points</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">Achievements</h1>
        <p className="opacity-90">
          Track your travel milestones and earn rewards for your adventures!
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <LevelProgress 
          currentLevel={userStats.level}
          totalPoints={userStats.totalPoints}
          nextLevelPoints={userStats.nextLevelPoints}
        />
        
        <StatsCard
          title="Completed"
          value={userStats.completedAchievements}
          icon={Trophy}
          color="bg-yellow-500"
          subtitle={`${userStats.completionRate.toFixed(1)}% completion rate`}
        />
        
        <StatsCard
          title="In Progress"
          value={inProgressAchievements.length}
          icon={TrendingUp}
          color="bg-blue-500"
          subtitle="Keep going!"
        />
        
        <StatsCard
          title="Total Points"
          value={userStats.totalPoints}
          icon={Star}
          color="bg-purple-500"
          subtitle="All time earned"
        />
      </div>

      {/* Tier Breakdown */}
      {Object.keys(userStats.byTier).length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Achievements by Tier</h2>
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(userStats.byTier).map(([tier, count]) => (
              <div key={tier} className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl mb-2">{tierIcons[tier]}</div>
                <p className="font-semibold text-gray-800">{count}</p>
                <p className="text-sm text-gray-600 capitalize">{tier}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedCategory === 'all'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All ({achievements.length})
          </button>
          
          {achievementCategories.map(category => {
            const count = achievements.filter(a => a.category === category.id).length;
            const Icon = category.icon;
            
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  selectedCategory === category.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {category.name} ({count})
              </button>
            );
          })}
        </div>

        {/* Achievements Grid */}
        {filteredAchievements.length === 0 ? (
          <div className="text-center py-12">
            <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <h3 className="text-lg font-medium text-gray-500 mb-2">No achievements yet</h3>
            <p className="text-gray-400">Start your travel journey to unlock achievements!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredAchievements
              .sort((a, b) => {
                // Sort by completion status, then by progress
                if (a.completed && !b.completed) return -1;
                if (!a.completed && b.completed) return 1;
                if (a.completed && b.completed) return b.completedAt - a.completedAt;
                return b.progress - a.progress;
              })
              .map(achievement => (
                <AchievementCard
                  key={achievement._id}
                  achievement={achievement}
                  onClick={setSelectedAchievement}
                />
              ))}
          </div>
        )}
      </div>

      {/* Achievement Detail Modal */}
      <AnimatePresence>
        {selectedAchievement && (
          <AchievementDetail
            achievement={selectedAchievement}
            onClose={() => setSelectedAchievement(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}