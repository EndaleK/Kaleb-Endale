import { auth } from '@clerk/nextjs';
import { NextResponse } from 'next/server';
import { login } from '@/app/utils/auth';

export async function GET() {
  const { userId } = auth();
  
  if (!userId) {
    return NextResponse.redirect('/login?error=AuthFailed');
  }

  try {
    await login();
    return NextResponse.redirect('/dashboard');
  } catch (error) {
    console.error('Error in auth callback:', error);
    return NextResponse.redirect('/login?error=ProfileCreationFailed');
  }
}