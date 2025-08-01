import { useAuth, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";

export function ConvexDebug() {
  const { getToken } = useAuth();
  const { isLoaded, isSignedIn } = useUser();
  
  useEffect(() => {
    const checkToken = async () => {
      // Only check for token if user is signed in
      if (!isLoaded || !isSignedIn) {
        return;
      }
      
      try {
        const token = await getToken({ template: "convex" });
        if (!token) {
          console.error("No Convex JWT token found - you need to create a JWT template named 'convex' in Clerk dashboard");
        }
      } catch (error) {
        console.error("Error getting Convex token:", error);
      }
    };
    
    checkToken();
  }, [getToken, isLoaded, isSignedIn]);
  
  return null;
}