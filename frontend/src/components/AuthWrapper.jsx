import { useUser } from "@clerk/clerk-react";
import { useConvexAuth } from "convex/react";
import { useEffect, useState } from "react";

export function AuthWrapper({ children }) {
  const { isLoaded: clerkLoaded, isSignedIn, user } = useUser();
  const { isLoading: convexLoading } = useConvexAuth();
  const [hasStoredUser, setHasStoredUser] = useState(false);

  useEffect(() => {
    // Store user in backend when authenticated with Clerk
    if (clerkLoaded && isSignedIn && user && !hasStoredUser) {
      const storeUserInBackend = async () => {
        try {
          // In production (Vercel), use relative path. In dev, use localhost
          const apiUrl = import.meta.env.PROD ? '/api' : (import.meta.env.VITE_API_URL || 'http://localhost:8000');
          const response = await fetch(`${apiUrl}/store-user`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              clerk_user_id: user.id,
              email: user.primaryEmailAddress?.emailAddress || '',
              name: user.fullName || user.firstName || null,
              image_url: user.imageUrl || null
            })
          });
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          setHasStoredUser(true);
        } catch (error) {
          // Silently handle error - user can still use the app
        }
      };
      
      storeUserInBackend();
    }
  }, [clerkLoaded, isSignedIn, user, hasStoredUser]);

  // Add a timeout to prevent infinite loading
  const [loadingTimeout, setLoadingTimeout] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!clerkLoaded || convexLoading) {
        setLoadingTimeout(true);
      }
    }, 10000); // 10 second timeout
    
    return () => clearTimeout(timer);
  }, [clerkLoaded, convexLoading]);

  if ((!clerkLoaded || convexLoading) && !loadingTimeout) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return children;
}