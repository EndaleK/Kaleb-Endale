import React from 'react';
import Link from 'next/link';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { useUser } from '@clerk/clerk-react';

const Header = () => {
  const { isSignedIn, user } = useUser();

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold">Your App Name</span>
            </Link>
          </div>
          <div className="flex items-center">
            <SignedIn>
              <span className="mr-4">Welcome, {user?.firstName}!</span>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
            <SignedOut>
              <Link href="/sign-in" className="text-gray-700 hover:text-gray-900 mr-4">
                Sign In
              </Link>
              <Link href="/sign-up" className="text-gray-700 hover:text-gray-900">
                Sign Up
              </Link>
            </SignedOut>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
