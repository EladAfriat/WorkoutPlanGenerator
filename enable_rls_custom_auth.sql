-- Enable Row Level Security for Custom Authentication System
-- Run this in Supabase SQL Editor

-- ============================================
-- STEP 1: Enable RLS on All Tables
-- ============================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_workout_history ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 2: Drop Existing Policies (if any)
-- ============================================

DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;

DROP POLICY IF EXISTS "Users can view own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Users can insert own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Users can update own preferences" ON user_preferences;

DROP POLICY IF EXISTS "Users can view own workout history" ON user_workout_history;
DROP POLICY IF EXISTS "Users can insert own workout history" ON user_workout_history;

-- ============================================
-- STEP 3: Create Policies for Custom Auth
-- ============================================
-- Note: Since we're using custom auth (not Supabase Auth),
-- these policies allow operations but your app must validate
-- user permissions. For better security, use service role key
-- in your app and enforce security there.

-- Users table policies
-- Allow SELECT: Your app will filter by user_id from session
CREATE POLICY "Allow authenticated users to view own data"
    ON users FOR SELECT
    USING (true);  -- App validates user_id matches session

-- Allow UPDATE: Your app validates user_id matches session
CREATE POLICY "Allow authenticated users to update own data"
    ON users FOR UPDATE
    USING (true);  -- App validates user_id matches session

-- Allow INSERT: Your app handles signup
CREATE POLICY "Allow user registration"
    ON users FOR INSERT
    WITH CHECK (true);  -- App handles validation

-- User preferences policies
CREATE POLICY "Allow authenticated users to view own preferences"
    ON user_preferences FOR SELECT
    USING (true);  -- App filters by user_id from session

CREATE POLICY "Allow authenticated users to insert own preferences"
    ON user_preferences FOR INSERT
    WITH CHECK (true);  -- App ensures user_id matches session

CREATE POLICY "Allow authenticated users to update own preferences"
    ON user_preferences FOR UPDATE
    USING (true);  -- App ensures user_id matches session

-- Workout history policies
CREATE POLICY "Allow authenticated users to view own workout history"
    ON user_workout_history FOR SELECT
    USING (true);  -- App filters by user_id from session

CREATE POLICY "Allow authenticated users to insert own workout history"
    ON user_workout_history FOR INSERT
    WITH CHECK (true);  -- App ensures user_id matches session

-- ============================================
-- STEP 4: Verify RLS is Enabled
-- ============================================
-- After running this, check:
-- 1. Go to Authentication → Policies
-- 2. Verify all tables show "RLS Enabled" ✅
-- 3. Verify policies are created for each table

-- ============================================
-- IMPORTANT SECURITY NOTE:
-- ============================================
-- Since you're using custom authentication, RLS policies
-- can't use auth.uid(). Your application MUST:
--
-- 1. Always validate user_id matches the logged-in user
-- 2. Use service role key for authenticated operations
-- 3. Never trust client-side user_id - validate server-side
-- 4. Use parameterized queries to prevent SQL injection
--
-- Example in your app:
--   user_id = st.session_state.user['id']  # From session
--   result = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
--   # Always filter by user_id from session, never from user input!

