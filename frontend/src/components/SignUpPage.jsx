import { SignUp } from "@clerk/clerk-react";
import { Plane } from "lucide-react";

export function SignUpPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Plane className="h-10 w-10 text-blue-600" />
            <span className="text-3xl font-bold text-gray-900">TravelAI</span>
          </div>
          <p className="text-gray-600">Create your account to start planning</p>
        </div>
        <SignUp 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl",
            }
          }}
          afterSignUpUrl="/"
          signInUrl="/sign-in"
        />
      </div>
    </div>
  );
}