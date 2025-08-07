import React, { useEffect, useRef, useState } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { Trophy, Star, Award, MapPin, Zap } from 'lucide-react';
import confetti from 'canvas-confetti';

const LEVEL_COLORS = {
  1: '#4ade80', // green-400
  2: '#60a5fa', // blue-400  
  3: '#a78bfa', // purple-400
  4: '#f472b6', // pink-400
  5: '#fb923c', // orange-400
};

const BADGES = {
  early_bird: { name: 'Early Bird', icon: '🌅', color: '#fbbf24' },
  night_owl: { name: 'Night Owl', icon: '🦉', color: '#6366f1' },
  explorer: { name: 'Explorer', icon: '🗺️', color: '#10b981' },
  perfect_day: { name: 'Perfect Day', icon: '🏆', color: '#f59e0b' },
  social_butterfly: { name: 'Social Butterfly', icon: '🦋', color: '#ec4899' },
  photographer: { name: 'Photographer', icon: '📸', color: '#8b5cf6' },
  foodie: { name: 'Foodie', icon: '🍽️', color: '#f97316' },
  adventurer: { name: 'Adventurer', icon: '🎯', color: '#dc2626' },
};

function AnimatedCharacter({ position, level, isMoving }) {
  const characters = ['🚶‍♀️', '🏃‍♀️', '🧗‍♀️', '🚴‍♀️', '🏄‍♀️'];
  const character = characters[Math.min(level - 1, characters.length - 1)];
  
  return (
    <div
      className={`absolute transition-all duration-1000 ease-in-out text-4xl ${isMoving ? 'animate-bounce' : ''}`}
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        transform: 'translate(-50%, -50%)',
        zIndex: 20,
      }}
    >
      {character}
    </div>
  );
}

function LevelNode({ level, isUnlocked, isCurrent, onClick, position }) {
  const color = LEVEL_COLORS[level] || '#9ca3af';
  const size = isCurrent ? 'w-12 h-12' : 'w-10 h-10';
  
  return (
    <button
      onClick={() => onClick(level)}
      className={`absolute ${size} rounded-full border-4 border-white shadow-lg transition-all duration-300 hover:scale-110 flex items-center justify-center text-white font-bold`}
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        backgroundColor: isUnlocked ? color : '#d1d5db',
        transform: 'translate(-50%, -50%)',
        zIndex: isCurrent ? 15 : 10,
      }}
      disabled={!isUnlocked}
    >
      {isCurrent ? (
        <Star className="w-6 h-6" fill="currentColor" />
      ) : (
        <span className="text-lg">{level}</span>
      )}
    </button>
  );
}

function PathLine({ from, to, isUnlocked }) {
  const length = Math.sqrt(
    Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2)
  );
  
  const angle = Math.atan2(to.y - from.y, to.x - from.x) * 180 / Math.PI;
  
  return (
    <div
      className={`absolute border-t-4 ${isUnlocked ? 'border-green-400' : 'border-gray-300'} transition-colors duration-500`}
      style={{
        left: `${from.x}%`,
        top: `${from.y}%`,
        width: `${length * 0.8}%`, // Scale factor for visual
        transformOrigin: '0 0',
        transform: `rotate(${angle}deg)`,
        zIndex: 5,
      }}
    />
  );
}

function BadgeShowcase({ badges, onBadgeClick }) {
  return (
    <div className="bg-white rounded-lg p-4 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <Award className="w-5 h-5" />
        Achievements
      </h3>
      
      {badges.length === 0 ? (
        <p className="text-gray-500 text-sm">Complete activities to earn badges!</p>
      ) : (
        <div className="grid grid-cols-4 gap-3">
          {badges.map((badge, index) => {
            const badgeInfo = BADGES[badge.id] || { name: badge.name, icon: badge.icon, color: '#6b7280' };
            
            return (
              <button
                key={badge.id}
                onClick={() => onBadgeClick(badge)}
                className="flex flex-col items-center p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors group"
              >
                <div 
                  className="w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-1 group-hover:scale-110 transition-transform"
                  style={{ backgroundColor: badgeInfo.color + '20' }}
                >
                  {badgeInfo.icon}
                </div>
                <span className="text-xs text-gray-600 text-center font-medium">
                  {badgeInfo.name}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(badge.unlockedAt).toLocaleDateString()}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function DailyProgress({ dailyProgress }) {
  if (!dailyProgress || dailyProgress.length === 0) {
    return (
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Daily Progress</h3>
        <p className="text-gray-500 text-sm">Start completing activities to see your progress!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <Zap className="w-5 h-5" />
        Daily Progress
      </h3>
      
      <div className="space-y-3">
        {dailyProgress.slice(-5).map((day, index) => {
          const completionRate = (day.slotsCompleted / day.totalSlots) * 100;
          
          return (
            <div key={day.date} className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">
                    {new Date(day.date).toLocaleDateString()}
                  </span>
                  <span className="text-gray-500">
                    {day.slotsCompleted}/{day.totalSlots}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
              </div>
              <div className="ml-4 text-right">
                <div className="text-sm font-semibold text-blue-600">
                  {day.score} pts
                </div>
                {day.distanceWalked > 0 && (
                  <div className="text-xs text-gray-500">
                    {(day.distanceWalked / 1000).toFixed(1)}km
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function CartoonMapJourney({ tripId }) {
  const journey = useQuery(api.journeys.getJourney, { tripId });
  const createJourney = useMutation(api.journeys.createJourney);
  const updateProgress = useMutation(api.journeys.updateProgress);
  
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [showBadgeDetail, setShowBadgeDetail] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const canvasRef = useRef(null);

  // Initialize journey if it doesn't exist
  useEffect(() => {
    if (tripId && journey === null) {
      createJourney({ 
        tripId, 
        totalLevels: 5, 
        mapTheme: 'adventure' 
      });
    }
  }, [tripId, journey, createJourney]);

  // Generate level positions (Angry Birds style path)
  const generateLevelPositions = (totalLevels) => {
    const positions = [];
    for (let i = 0; i < totalLevels; i++) {
      const progress = i / (totalLevels - 1);
      // Create a wavy path
      const x = 15 + progress * 70; // 15% to 85% width
      const y = 50 + Math.sin(progress * Math.PI * 2) * 20; // Wave pattern
      positions.push({ x, y });
    }
    return positions;
  };

  const triggerLevelUpCelebration = () => {
    setIsAnimating(true);
    
    // Confetti explosion
    confetti({
      particleCount: 150,
      spread: 100,
      origin: { y: 0.4 }
    });
    
    setTimeout(() => setIsAnimating(false), 2000);
  };

  const handleLevelClick = (level) => {
    if (!journey || level > journey.currentLevel) return;
    setSelectedLevel(level);
  };

  const handleBadgeClick = (badge) => {
    setShowBadgeDetail(badge);
  };

  if (!journey) {
    return (
      <div className="bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 rounded-lg p-8 text-center text-white">
        <div className="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
        <p>Loading your journey...</p>
      </div>
    );
  }

  const levelPositions = generateLevelPositions(journey.totalLevels);
  const currentLevel = journey.currentLevel || 1;

  return (
    <div className="space-y-6">
      {/* Main Map */}
      <div className="relative bg-gradient-to-br from-green-400 via-blue-500 to-purple-600 rounded-lg overflow-hidden shadow-lg">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-96"
          width="800"
          height="400"
        />
        
        {/* Background decorations */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-4 left-4 text-4xl">☁️</div>
          <div className="absolute top-8 right-8 text-3xl">🌞</div>
          <div className="absolute bottom-4 left-8 text-3xl">🌳</div>
          <div className="absolute bottom-8 right-4 text-3xl">🏔️</div>
          <div className="absolute top-1/2 left-1/4 text-2xl">🦋</div>
          <div className="absolute top-1/3 right-1/3 text-2xl">🌸</div>
        </div>

        {/* Path lines */}
        {levelPositions.slice(0, -1).map((position, index) => (
          <PathLine
            key={index}
            from={position}
            to={levelPositions[index + 1]}
            isUnlocked={index + 1 < currentLevel}
          />
        ))}

        {/* Level nodes */}
        {levelPositions.map((position, index) => {
          const level = index + 1;
          return (
            <LevelNode
              key={level}
              level={level}
              isUnlocked={level <= currentLevel}
              isCurrent={level === currentLevel}
              onClick={handleLevelClick}
              position={position}
            />
          );
        })}

        {/* Animated character */}
        <AnimatedCharacter
          position={journey.characterPosition}
          level={currentLevel}
          isMoving={isAnimating}
        />

        {/* Progress indicator */}
        <div className="absolute top-4 left-4 bg-white bg-opacity-90 rounded-lg p-3 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            <span className="font-semibold text-gray-800">Level {currentLevel}</span>
          </div>
          <div className="text-sm text-gray-600">
            {journey.dailyProgress?.reduce((sum, day) => sum + day.slotsCompleted, 0) || 0} activities completed
          </div>
        </div>

        {/* Theme selector */}
        <div className="absolute top-4 right-4 bg-white bg-opacity-90 rounded-lg p-2">
          <select 
            className="text-sm border-none bg-transparent focus:outline-none"
            value={journey.mapTheme}
            onChange={(e) => {
              // TODO: Update map theme
              console.log('Theme changed:', e.target.value);
            }}
          >
            <option value="adventure">🎯 Adventure</option>
            <option value="tropical">🏝️ Tropical</option>
            <option value="urban">🏙️ Urban</option>
            <option value="nature">🌲 Nature</option>
            <option value="cultural">🏛️ Cultural</option>
          </select>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <BadgeShowcase 
          badges={journey.unlockedBadges || []}
          onBadgeClick={handleBadgeClick}
        />
        
        <DailyProgress dailyProgress={journey.dailyProgress} />
      </div>

      {/* Level Detail Modal */}
      {selectedLevel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold mb-4">Level {selectedLevel}</h3>
            <p className="text-gray-600 mb-4">
              {selectedLevel <= currentLevel 
                ? "You've completed this level! Great job!" 
                : "Complete more activities to unlock this level."
              }
            </p>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <div className="text-sm text-gray-500 mb-1">Progress</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full"
                    style={{ 
                      width: selectedLevel <= currentLevel ? '100%' : '0%' 
                    }}
                  />
                </div>
              </div>
            </div>
            <button
              onClick={() => setSelectedLevel(null)}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Badge Detail Modal */}
      {showBadgeDetail && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="text-center">
              <div className="text-6xl mb-4">{BADGES[showBadgeDetail.id]?.icon || showBadgeDetail.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{showBadgeDetail.name}</h3>
              <p className="text-gray-600 mb-4">
                Earned on {new Date(showBadgeDetail.unlockedAt).toLocaleDateString()}
              </p>
              <button
                onClick={() => setShowBadgeDetail(null)}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Awesome!
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}