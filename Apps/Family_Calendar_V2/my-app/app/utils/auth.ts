import { auth } from '@clerk/nextjs';
import { supabase } from './supabase';

export async function login() {
  const { userId } = auth();

  if (!userId) {
    throw new Error('Not authenticated');
  }

  try {
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (error && error.code === 'PGRST116') {
      // User doesn't exist, create a new profile
      const { data: newProfile, error: createError } = await supabase
        .from('profiles')
        .insert({ user_id: userId })
        .single();

      if (createError) {
        throw createError;
      }

      return newProfile;
    } else if (error) {
      throw error;
    }

    return profile;
  } catch (error) {
    console.error('Error in login function:', error);
    throw error;
  }
}