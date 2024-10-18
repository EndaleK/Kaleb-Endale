import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="mb-6 text-2xl font-bold text-center text-gray-800">Sign In to Family Calendar</h1>
        <SignIn 
          path="/sign-in" 
          routing="path" 
          signUpUrl="/sign-up" 
          afterSignInUrl="/"
          redirectUrl="/"
        />
      </div>
    </div>
  );
}