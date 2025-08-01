import { useAuth } from "@clerk/clerk-react";
import { useEffect } from "react";

export function ConvexDebug() {
  const { getToken } = useAuth();
  
  useEffect(() => {
    const checkToken = async () => {
      try {
        const token = await getToken({ template: "convex" });
        console.log("Convex JWT token:", token);
        if (token) {
          // Decode and log the token payload
          const payload = JSON.parse(atob(token.split('.')[1]));
          console.log("Token payload:", payload);
        } else {
          console.error("No Convex JWT token found - you need to create a JWT template named 'convex' in Clerk dashboard");
        }
      } catch (error) {
        console.error("Error getting Convex token:", error);
      }
    };
    
    checkToken();
  }, [getToken]);
  
  return null;
}