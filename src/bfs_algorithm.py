"""
BFS Algorithm Module
Contains the core BFS algorithm for workout plan generation.
"""

from collections import defaultdict, deque
from typing import Dict, List, Set, Any


def level_allowed(ex_level: str, user_level: str) -> bool:
    """
    Check if user's level is sufficient for an exercise.
    
    Args:
        ex_level: Exercise required level
        user_level: User's fitness level
        
    Returns:
        True if user level is sufficient
    """
    levels = ['beginner', 'intermediate', 'advanced']
    return levels.index(user_level) >= levels.index(ex_level)


def equipment_allowed(ex_equipment: List[str], user_equipment: List[str]) -> bool:
    """
    Check if user has all required equipment for an exercise.
    
    Args:
        ex_equipment: List of required equipment
        user_equipment: List of user's available equipment
        
    Returns:
        True if user has all required equipment
    """
    return all(eq in user_equipment for eq in ex_equipment)


def get_muscle_groups(split: str, day: int) -> List[str]:
    """
    Get muscle groups to train based on split type and day.
    
    Args:
        split: Split type ('FB' for Full Body, 'AB' for A/B Split)
        day: Day number (1-indexed)
        
    Returns:
        List of muscle groups to train on this day
    """
    if split == 'FB':
        return ['chest', 'back', 'legs', 'triceps', 'shoulders', 'core', 'biceps']
    elif split == 'AB':
        if day % 2 == 1:
            return ['chest', 'triceps', 'shoulders', 'core']
        else:
            return ['back', 'legs', 'biceps', 'core']
    else:
        return []


def get_muscle_quotas(split: str) -> Dict[str, int]:
    """
    Get the number of exercises per muscle group per day based on split type.
    Based on professional fitness recommendations for balanced workouts.
    
    Args:
        split: Training split type ('FB' or 'AB')
        
    Returns:
        Dictionary mapping muscle groups to number of exercises per day
    """
    if split == 'FB':
        # Full Body: 2 exercises for big muscle groups, 1 for smaller groups
        return {
            'chest': 2,      # Big muscle group
            'back': 2,       # Big muscle group
            'legs': 2,       # Big muscle group
            'shoulders': 1,
            'biceps': 1,
            'triceps': 1,
            'core': 1
        }
    elif split == 'AB':
        # A/B Split: Different focus per day type
        # This will be handled per day in the main function
        return {
            'chest': 2,      # Day A
            'triceps': 1,    # Day A
            'shoulders': 1,  # Day A
            'core': 1,      # Day A
            'back': 2,      # Day B
            'legs': 2,      # Day B
            'biceps': 1     # Day B
        }
    else:
        return {}


def bfs_reserve_workout_plan(
    exercises: Dict[str, Dict[str, Any]],
    user_level: str,
    user_equipment: List[str],
    days: int,
    split: str
) -> List[List[str]]:
    """
    Generate a workout plan using quota-based round-robin system.
    
    Each day gets the same number of exercises per muscle group (balanced).
    Exercises are rotated across days using round-robin to ensure variety.
    
    Args:
        exercises: Dictionary of available exercises with their properties
        user_level: User's fitness level ('beginner', 'intermediate', 'advanced')
        user_equipment: List of user's available equipment
        days: Number of training days per week
        split: Training split type ('FB' or 'AB')
        
    Returns:
        List of daily workout plans, each containing exercise names
    """
    # Filter available exercises based on level and equipment
    available = {
        name: ex for name, ex in exercises.items()
        if level_allowed(ex['level'], user_level) and 
        equipment_allowed(ex['equipment'], user_equipment)
    }
    
    # Group exercises by primary muscle group
    muscle_pools = defaultdict(list)
    for name, ex in available.items():
        muscle_pools[ex['muscle']].append(name)
    
    # Get quotas for each muscle group
    quotas = get_muscle_quotas(split)
    
    # Get muscle groups for each day
    muscle_groups = [get_muscle_groups(split, i+1) for i in range(days)]
    
    # Initialize round-robin pointers for each muscle group
    muscle_pointers = defaultdict(int)
    
    daily_plan = []
    
    for day in range(days):
        plan_for_day = []
        target_muscles = muscle_groups[day]
        
        # For each muscle group that should be trained this day
        for muscle in target_muscles:
            quota = quotas.get(muscle, 1)  # Default to 1 if not specified
            
            # Get available exercises for this muscle
            pool = muscle_pools.get(muscle, [])
            
            if not pool:
                continue  # No exercises available for this muscle
            
            # Select exercises using round-robin
            selected = []
            pool_size = len(pool)
            
            for _ in range(quota):
                if pool_size == 0:
                    break
                
                # Get exercise from current pointer position
                idx = muscle_pointers[muscle] % pool_size
                exercise = pool[idx]
                
                # Move pointer forward for next time
                muscle_pointers[muscle] += 1
                
                selected.append(exercise)
            
            plan_for_day.extend(selected)
        
        daily_plan.append(plan_for_day)
    
    return daily_plan

