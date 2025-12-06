-- Database Schema for Workout Plan Generator
-- Run this in Supabase SQL Editor after creating your project

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_verification_token ON users(verification_token);

-- User preferences table (for storing workout preferences and plans)
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fitness_level VARCHAR(50),
    fitness_goal VARCHAR(50),
    training_days INTEGER,
    training_split VARCHAR(10),
    workout_location VARCHAR(100),
    equipment JSONB,
    workout_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- User workout history (optional - for tracking workout plans over time)
CREATE TABLE IF NOT EXISTS user_workout_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workout_plan JSONB NOT NULL,
    fitness_level VARCHAR(50),
    fitness_goal VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id and created_at for faster queries
CREATE INDEX IF NOT EXISTS idx_workout_history_user_id ON user_workout_history(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_history_created_at ON user_workout_history(created_at DESC);

-- Enable Row Level Security (RLS) - Optional but recommended for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_workout_history ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their own data)
-- Note: Adjust these policies based on your security needs

-- Users can read their own data
CREATE POLICY "Users can view own data"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- User preferences policies
CREATE POLICY "Users can view own preferences"
    ON user_preferences FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences"
    ON user_preferences FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences"
    ON user_preferences FOR UPDATE
    USING (auth.uid() = user_id);

-- Workout history policies
CREATE POLICY "Users can view own workout history"
    ON user_workout_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own workout history"
    ON user_workout_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

