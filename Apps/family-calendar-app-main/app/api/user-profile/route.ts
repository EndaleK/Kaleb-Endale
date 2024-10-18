import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs';

// Mock database for demonstration purposes
const userProfiles: Record<string, { name: string, email: string }> = {};

export async function GET(request: Request) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const userProfile = userProfiles[userId];

  if (userProfile) {
    return NextResponse.json(userProfile);
  } else {
    return NextResponse.json({ error: 'User profile not found' }, { status: 404 });
  }
}

export async function POST(request: Request) {
  const { userId } = auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();
  const { name, email } = body;

  if (!name || !email) {
    return NextResponse.json({ error: 'Name and email are required' }, { status: 400 });
  }

  // Create or update user profile
  userProfiles[userId] = { name, email };

  return NextResponse.json(userProfiles[userId], { status: 201 });
}