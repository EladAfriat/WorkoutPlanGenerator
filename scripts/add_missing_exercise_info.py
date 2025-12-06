"""
Script to add missing exercise information (instructions, tips, common_mistakes) to exercises.json
FIXED: Counter now properly tracks all info types added, not just instructions.
"""

import json
from typing import Dict, Any

# Dictionary of exercise information to add
EXERCISE_INFO = {
    # Add exercise information here as needed
    # Format: "Exercise Name": {
    #     "instructions": [...],
    #     "tips": [...],
    #     "common_mistakes": [...]
    # }
}

def add_missing_info():
    """Add missing instructions, tips, and common_mistakes to exercises."""
    
    # Load exercises data
    with open('data/exercises.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    exercises = data.get('exercises', {})
    
    # Counter for tracking exercises that received ANY info (FIXED)
    info_added = 0
    
    # Process each exercise
    for exercise_name, exercise_data in exercises.items():
        # Track if ANY info was added for this exercise (FIXED)
        any_info_added = False
        
        # Check if we have info for this exercise
        if exercise_name in EXERCISE_INFO:
            info_to_add = EXERCISE_INFO[exercise_name]
            
            # Add instructions if missing
            if 'instructions' in info_to_add and (
                'instructions' not in exercise_data or 
                not exercise_data.get('instructions')
            ):
                exercise_data['instructions'] = info_to_add['instructions']
                any_info_added = True
            
            # Add tips if missing (FIXED: Now tracked in counter)
            if 'tips' in info_to_add and (
                'tips' not in exercise_data or 
                not exercise_data.get('tips')
            ):
                exercise_data['tips'] = info_to_add['tips']
                any_info_added = True
            
            # Add common_mistakes if missing (FIXED: Now tracked in counter)
            if 'common_mistakes' in info_to_add and (
                'common_mistakes' not in exercise_data or 
                not exercise_data.get('common_mistakes')
            ):
                exercise_data['common_mistakes'] = info_to_add['common_mistakes']
                any_info_added = True
        
        # Increment counter if ANY info was added (instructions, tips, OR common_mistakes) (FIXED)
        if any_info_added:
            info_added += 1
    
    # Save updated data
    with open('data/exercises.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print accurate report (FIXED: Now accurately reports exercises with ANY info added)
    print(f"✅ Added info to {info_added} exercises")
    print(f"✅ Total exercises processed: {len(exercises)}")


if __name__ == "__main__":
    add_missing_info()
