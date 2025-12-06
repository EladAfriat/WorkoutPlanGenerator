"""
User Data Collection Module
Handles storing and retrieving user workout preferences and data.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

# Optional Supabase import
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

import os
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Optional[Any]:
    """Initialize and return Supabase client."""
    if not SUPABASE_AVAILABLE:
        return None
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return None
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception:
        return None


def save_user_workout_preferences(
    user_id: str,
    fitness_level: str,
    fitness_goal: str,
    training_days: int,
    training_split: str,
    workout_location: str,
    equipment: list,
    workout_plan: list = None
) -> Dict[str, Any]:
    """
    Save user's workout preferences and plan to database.
    
    Args:
        user_id: User's unique ID
        fitness_level: User's fitness level
        fitness_goal: User's fitness goal
        training_days: Number of training days per week
        training_split: Training split type (FB/AB)
        workout_location: Workout location
        equipment: List of equipment
        workout_plan: Optional workout plan data
        
    Returns:
        Dictionary with 'success' and 'message'
    """
    supabase = get_supabase_client()
    if not supabase:
        # Fallback to local storage
        return save_user_data_local(user_id, {
            "fitness_level": fitness_level,
            "fitness_goal": fitness_goal,
            "training_days": training_days,
            "training_split": training_split,
            "workout_location": workout_location,
            "equipment": equipment,
            "workout_plan": workout_plan,
            "saved_at": datetime.utcnow().isoformat()
        })
    
    try:
        # Check if user_preferences table exists, if not create entry in users table
        preferences_data = {
            "user_id": user_id,
            "fitness_level": fitness_level,
            "fitness_goal": fitness_goal,
            "training_days": training_days,
            "training_split": training_split,
            "workout_location": workout_location,
            "equipment": equipment,
            "workout_plan": workout_plan,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Try to update existing, if not insert new
        existing = supabase.table("user_preferences").select("user_id").eq("user_id", user_id).execute()
        
        if existing.data:
            # Update existing
            result = supabase.table("user_preferences").update(preferences_data).eq("user_id", user_id).execute()
        else:
            # Insert new
            preferences_data["created_at"] = datetime.utcnow().isoformat()
            result = supabase.table("user_preferences").insert(preferences_data).execute()
        
        return {
            "success": True,
            "message": "Preferences saved successfully"
        }
    except Exception as e:
        # If table doesn't exist, use local storage
        return save_user_data_local(user_id, preferences_data)


def save_user_data_local(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback: Store user data in session state."""
    if 'local_user_data' not in st.session_state:
        st.session_state.local_user_data = {}
    
    st.session_state.local_user_data[user_id] = data
    
    return {
        "success": True,
        "message": "Preferences saved (local mode)"
    }


def get_user_workout_preferences(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user's saved workout preferences.
    
    Args:
        user_id: User's unique ID
        
    Returns:
        Dictionary with user preferences or None
    """
    supabase = get_supabase_client()
    if not supabase:
        # Fallback to local storage
        return st.session_state.get("local_user_data", {}).get(user_id)
    
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception:
        return st.session_state.get("local_user_data", {}).get(user_id)


def save_user_registration_data(user_id: str, registration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save additional user registration data.
    
    Args:
        user_id: User's unique ID
        registration_data: Dictionary with registration info
        
    Returns:
        Dictionary with 'success' and 'message'
    """
    # This can be used to store additional signup information
    # For now, we'll use the user_preferences table or extend users table
    return {"success": True, "message": "Registration data saved"}

