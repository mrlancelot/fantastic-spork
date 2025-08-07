import React, { useState } from 'react';
import { useQuery, useMutation } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { 
  Users, 
  UserPlus, 
  Share2, 
  MapPin, 
  Clock,
  Trophy,
  Copy,
  QrCode,
  Bell,
  Settings,
  Crown,
  Shield,
  CheckCircle,
  AlertCircle,
  MessageSquare,
  Calendar
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function GroupMemberCard({ member, isCurrentUser, canManage, onRemove }) {
  const getRoleIcon = (role) => {
    return role === 'leader' ? Crown : Shield;
  };

  const getRoleColor = (role) => {
    return role === 'leader' ? 'text-yellow-600' : 'text-blue-600';
  };

  const formatJoinDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const RoleIcon = getRoleIcon(member.role);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-4 rounded-lg border-2 ${
        isCurrentUser ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'
      } hover:shadow-md transition-all`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-semibold text-lg`}>
            {member.firstName?.charAt(0) || member.name?.charAt(0) || member.email.charAt(0).toUpperCase()}
          </div>
          
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-800">
                {member.firstName && member.lastName 
                  ? `${member.firstName} ${member.lastName}`
                  : member.name || 'Anonymous User'
                }
                {isCurrentUser && <span className="text-blue-600 text-sm">(You)</span>}
              </h3>
              <RoleIcon className={`w-4 h-4 ${getRoleColor(member.role)}`} />
            </div>
            <p className="text-sm text-gray-600">{member.email}</p>
            <p className="text-xs text-gray-500">
              Joined {formatJoinDate(member.joinedAt)}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs">
            <div className={`w-2 h-2 rounded-full ${
              Math.random() > 0.5 ? 'bg-green-500' : 'bg-gray-400'
            }`}></div>
            <span className="text-gray-500">
              {Math.random() > 0.5 ? 'Online' : 'Offline'}
            </span>
          </div>
          
          {canManage && !isCurrentUser && (
            <button
              onClick={() => onRemove(member._id)}
              className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              title="Remove member"
            >
              <AlertCircle className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function GroupCheckInMap({ checkIns, members }) {
  const getCheckInInfo = (checkIn) => {
    const member = members.find(m => m._id === checkIn.userId);
    return {
      ...checkIn,
      memberName: member?.firstName || member?.name || 'Unknown',
      memberInitial: (member?.firstName?.charAt(0) || member?.name?.charAt(0) || 'U').toUpperCase()
    };
  };

  const recentCheckIns = checkIns
    .map(getCheckInInfo)
    .sort((a, b) => b.time - a.time)
    .slice(0, 10);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <MapPin className="w-5 h-5" />
        Group Check-ins
      </h3>

      {recentCheckIns.length === 0 ? (
        <div className="text-center py-8">
          <MapPin className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">No check-ins yet</p>
          <p className="text-sm text-gray-400">Check-ins will appear here when members arrive at activities</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recentCheckIns.map((checkIn, index) => (
            <motion.div
              key={`${checkIn.userId}-${checkIn.time}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
            >
              <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-sm font-semibold">
                {checkIn.memberInitial}
              </div>
              
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">
                  {checkIn.memberName} checked in
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(checkIn.time).toLocaleTimeString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {checkIn.location.lat.toFixed(4)}, {checkIn.location.lng.toFixed(4)}
                  </span>
                </div>
              </div>
              
              <CheckCircle className="w-5 h-5 text-green-600" />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function SharedAchievements({ achievements, members }) {
  if (!achievements || achievements.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5" />
          Group Achievements
        </h3>
        <div className="text-center py-8">
          <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">No group achievements yet</p>
          <p className="text-sm text-gray-400">Complete activities together to unlock group achievements!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5" />
        Group Achievements ({achievements.length})
      </h3>
      
      <div className="space-y-3">
        {achievements.map((achievement, index) => {
          const earnedByMembers = achievement.earnedBy.map(userId => 
            members.find(m => m._id === userId)
          ).filter(Boolean);

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg"
            >
              <div className="text-3xl">🏆</div>
              
              <div className="flex-1">
                <h4 className="font-semibold text-gray-800 capitalize">
                  {achievement.type.replace('_', ' ')}
                </h4>
                <p className="text-sm text-gray-600">
                  Earned by {earnedByMembers.length} member{earnedByMembers.length !== 1 ? 's' : ''}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(achievement.earnedAt).toLocaleDateString()}
                </p>
              </div>
              
              <div className="flex -space-x-2">
                {earnedByMembers.slice(0, 3).map(member => (
                  <div
                    key={member._id}
                    className="w-8 h-8 rounded-full bg-purple-500 border-2 border-white flex items-center justify-center text-white text-xs font-semibold"
                    title={member.firstName || member.name}
                  >
                    {(member.firstName?.charAt(0) || member.name?.charAt(0) || 'U').toUpperCase()}
                  </div>
                ))}
                {earnedByMembers.length > 3 && (
                  <div className="w-8 h-8 rounded-full bg-gray-500 border-2 border-white flex items-center justify-center text-white text-xs font-semibold">
                    +{earnedByMembers.length - 3}
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

function InviteModal({ isOpen, onClose, groupId, onInvite }) {
  const [inviteMethod, setInviteMethod] = useState('link');
  const [email, setEmail] = useState('');
  const [copying, setCopying] = useState(false);

  const inviteLink = `${window.location.origin}/join-group/${groupId}`;

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(inviteLink);
      setCopying(true);
      setTimeout(() => setCopying(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const sendEmailInvite = () => {
    if (!email.trim()) return;
    
    onInvite(email);
    setEmail('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg p-6 w-full max-w-md"
      >
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Invite to Group
        </h2>

        <div className="space-y-4">
          {/* Method Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Invite Method
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setInviteMethod('link')}
                className={`p-3 rounded-lg border-2 flex items-center gap-2 ${
                  inviteMethod === 'link'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Share2 className="w-4 h-4" />
                <span className="text-sm">Share Link</span>
              </button>
              
              <button
                onClick={() => setInviteMethod('email')}
                className={`p-3 rounded-lg border-2 flex items-center gap-2 ${
                  inviteMethod === 'email'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm">Send Email</span>
              </button>
            </div>
          </div>

          {/* Share Link */}
          {inviteMethod === 'link' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Invite Link
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inviteLink}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 text-sm"
                />
                <button
                  onClick={copyToClipboard}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    copying
                      ? 'bg-green-500 text-white'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {copying ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Anyone with this link can join your group
              </p>
            </div>
          )}

          {/* Email Invite */}
          {inviteMethod === 'email' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="friend@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* QR Code Option */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <QrCode className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">QR Code</span>
            </div>
            <p className="text-xs text-gray-500">
              Generate a QR code for easy scanning and joining
            </p>
            <button className="mt-2 px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm">
              Generate QR Code
            </button>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          
          {inviteMethod === 'email' ? (
            <button
              onClick={sendEmailInvite}
              disabled={!email.trim()}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send Invite
            </button>
          ) : (
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Done
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default function GroupSync({ tripId }) {
  const groupSync = useQuery(api.groupSync.getGroupSync, { tripId });
  const groupMembers = useQuery(
    api.groupSync.getGroupMembers, 
    groupSync ? { groupId: groupSync.groupId } : 'skip'
  );
  
  const createGroup = useMutation(api.groupSync.createGroupSync);
  const joinGroup = useMutation(api.groupSync.joinGroup);
  const leaveGroup = useMutation(api.groupSync.leaveGroup);
  
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [joinCode, setJoinCode] = useState('');
  const [showJoinForm, setShowJoinForm] = useState(false);

  const handleCreateGroup = async () => {
    try {
      await createGroup({ tripId });
    } catch (error) {
      console.error('Error creating group:', error);
    }
  };

  const handleJoinGroup = async () => {
    if (!joinCode.trim()) return;
    
    try {
      await joinGroup({ groupId: joinCode.trim() });
      setJoinCode('');
      setShowJoinForm(false);
    } catch (error) {
      console.error('Error joining group:', error);
      alert('Failed to join group. Please check the group code.');
    }
  };

  const handleLeaveGroup = async () => {
    if (!confirm('Are you sure you want to leave this group?')) return;
    
    try {
      await leaveGroup({ groupId: groupSync.groupId });
    } catch (error) {
      console.error('Error leaving group:', error);
    }
  };

  const handleInviteMember = (email) => {
    // In a real implementation, this would send an email invite
    console.log('Inviting member:', email);
  };

  // No group exists
  if (!groupSync) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg p-8 text-center shadow-sm border border-gray-200">
          <Users className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Travel Better Together
          </h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Create or join a group to share your trip, sync activities, and earn achievements together.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={handleCreateGroup}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Create New Group
            </button>
            
            <button
              onClick={() => setShowJoinForm(true)}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Users className="w-4 h-4" />
              Join Existing Group
            </button>
          </div>

          <AnimatePresence>
            {showJoinForm && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 p-4 bg-gray-50 rounded-lg"
              >
                <h3 className="font-medium text-gray-800 mb-3">Join a Group</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={joinCode}
                    onChange={(e) => setJoinCode(e.target.value)}
                    placeholder="Enter group code"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleJoinGroup}
                    disabled={!joinCode.trim()}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Join
                  </button>
                </div>
                <button
                  onClick={() => setShowJoinForm(false)}
                  className="mt-2 text-sm text-gray-500 hover:text-gray-700"
                >
                  Cancel
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    );
  }

  const currentUser = groupMembers?.find(member => member.clerkId === 'current_user'); // TODO: Get actual current user
  const isLeader = currentUser?.role === 'leader';

  return (
    <div className="space-y-6">
      {/* Group Header */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Group Travel</h1>
            <p className="opacity-90">
              {groupMembers?.length || 0} member{(groupMembers?.length || 0) !== 1 ? 's' : ''} • 
              Group ID: {groupSync.groupId.slice(-8)}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowInviteModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors"
            >
              <UserPlus className="w-4 h-4" />
              Invite
            </button>
            
            <button className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Group Members */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Users className="w-5 h-5" />
            Group Members ({groupMembers?.length || 0})
          </h2>
          
          {isLeader && (
            <button
              onClick={handleLeaveGroup}
              className="text-red-600 hover:text-red-800 text-sm"
            >
              Leave Group
            </button>
          )}
        </div>
        
        <div className="grid gap-4">
          {groupMembers?.map(member => (
            <GroupMemberCard
              key={member._id}
              member={member}
              isCurrentUser={member.clerkId === 'current_user'} // TODO: Fix
              canManage={isLeader}
              onRemove={() => {}} // TODO: Implement
            />
          ))}
        </div>
      </div>

      {/* Group Check-ins */}
      <GroupCheckInMap 
        checkIns={groupSync.groupCheckIns || []} 
        members={groupMembers || []} 
      />

      {/* Shared Achievements */}
      <SharedAchievements 
        achievements={groupSync.sharedAchievements} 
        members={groupMembers || []} 
      />

      {/* Real-time Activity Feed */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Activity Feed
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <Calendar className="w-5 h-5 text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-800">
                Group synchronized successfully
              </p>
              <p className="text-xs text-blue-600">All members can now see shared activities</p>
            </div>
            <span className="text-xs text-blue-500">Just now</span>
          </div>
          
          <div className="text-center py-6 text-gray-500">
            <p className="text-sm">More activity updates will appear here</p>
          </div>
        </div>
      </div>

      <InviteModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        groupId={groupSync.groupId}
        onInvite={handleInviteMember}
      />
    </div>
  );
}