import { useUser } from "@clerk/clerk-react";
import { RedirectToSignIn } from "@clerk/clerk-react";

export function ProtectedRoute({ children }) {
  const { isSignedIn, isLoaded } = useUser();

  // Show loading state while Clerk is loading
  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to sign-in if user is not authenticated
  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  // Render protected content if user is authenticated
  return children;
}

export default ProtectedRoute;