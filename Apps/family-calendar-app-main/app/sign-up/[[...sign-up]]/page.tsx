import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="mb-6 text-2xl font-bold text-center text-gray-800">Sign Up for Family Calendar</h1>
        <SignUp path="/sign-up" routing="path" signInUrl="/sign-in" />
      </div>
    </div>
  );
}