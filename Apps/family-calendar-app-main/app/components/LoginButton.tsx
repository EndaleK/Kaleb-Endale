'use client';

import { useSignIn } from '@clerk/nextjs';
import { useState } from 'react';

export function LoginButton() {
  const { signIn, isLoaded } = useSignIn();
  const [isLogging, setIsLogging] = useState(false);

  const handleLogin = async () => {
    if (!isLoaded) return;
    
    setIsLogging(true);
    try {
      await signIn.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/auth/callback',
        redirectUrlComplete: '/dashboard'
      });
    } catch (error) {
      console.error('Error during login:', error);
      setIsLogging(false);
    }
  };

  return (
    <button onClick={handleLogin} disabled={!isLoaded || isLogging}>
      {isLogging ? 'Redirecting...' : 'Log in with Google'}
    </button>
  );
}