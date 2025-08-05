import { useUser } from "@clerk/clerk-react";

export function useCurrentUser() {
  const { user, isLoaded, isSignedIn } = useUser();
  
  return {
    user,
    isLoaded,
    isSignedIn,
    userId: user?.id || 'demo-user', // Fallback for demo purposes
    userEmail: user?.primaryEmailAddress?.emailAddress || '',
    userName: user?.fullName || user?.firstName || 'Guest User'
  };
}