"""
Streamlit Application
Main interface for the Workout Plan Generator using BFS algorithm.
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from collections import defaultdict
from typing import Dict, List, Any
from io import BytesIO

# Optional PDF imports - app will work without reportlab, but PDF export won't be available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_handler import load_exercises_data, get_exercises_dict, get_goal_set_rep, get_equipment_options
from bfs_algorithm import bfs_reserve_workout_plan
from auth import (
    create_user, login_user, verify_email_token, 
    get_current_user, logout_user, is_authenticated,
    request_password_reset, reset_password_with_code
)
from user_data import save_user_workout_preferences


# Page configuration
st.set_page_config(
    page_title="Workout Plan Generator",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .workout-day {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
    }
    .stColumn > div {
        padding-top: 0 !important;
    }
    div[data-testid="column"] {
        padding-top: 0 !important;
    }
    .exercise-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        background-color: white;
        color: #333333;
        border-radius: 5px;
        border-left: 3px solid #ff6b6b;
    }
    .exercise-item strong {
        color: #1f77b4;
        font-size: 1.1rem;
    }
    .exercise-item small {
        color: #666666;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    
    /* Video button styling */
    .video-button {
        background-color: #ff0000 !important;
        color: white !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        font-weight: bold !important;
        text-decoration: none !important;
        display: inline-block !important;
        margin-right: 0.3rem !important;
        transition: background-color 0.3s ease !important;
    }
    
    .video-button:hover {
        background-color: #cc0000 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(31, 119, 180, 0.2);
    }
    
    [data-testid="stSidebar"] .sidebar-section-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #1f77b4;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 1.25rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    
    [data-testid="stSidebar"] .sidebar-section-title:first-child {
        margin-top: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #155a8a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
    }
    
    [data-testid="stSidebar"] .stButton>button:active {
        transform: translateY(0);
    }
    
    [data-testid="stSidebar"] .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    [data-testid="stSidebar"] .stExpander {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(31, 119, 180, 0.3);
        border-radius: 8px;
        padding: 0.5rem;
        margin: 1rem 0;
    }
    
    [data-testid="stSidebar"] .stExpander label {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .stExpander .stMarkdown {
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        border-radius: 5px;
        padding: 0.75rem;
    }
    
    [data-testid="stSidebar"] .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        border-radius: 5px;
        padding: 0.75rem;
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: #666666;
        font-size: 0.85rem;
    }
    
    /* Add spacing between sidebar elements */
    [data-testid="stSidebar"] > div {
        padding: 1rem;
    }
    
    /* Sidebar divider */
    .sidebar-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #e0e0e0, transparent);
        margin: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def load_data(web_source=None):
    """Load exercise data and cache it."""
    if 'exercise_data' not in st.session_state:
        try:
            # Use provided web_source or check session state
            source = web_source if web_source else st.session_state.get('web_data_source', None)
            # Only use if it's not empty
            source = source if source and source.strip() else None
            
            st.session_state.exercise_data = load_exercises_data(source)
            st.session_state.exercises = get_exercises_dict(st.session_state.exercise_data)
            st.session_state.goal_set_rep = get_goal_set_rep(st.session_state.exercise_data)
            st.session_state.equipment_options = get_equipment_options(st.session_state.exercise_data)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()


def render_user_questions():
    """Render interactive user questions and return user preferences."""
    st.header("📋 Tell Us About Yourself")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Fitness Profile")
        user_level = st.selectbox(
            "What is your fitness level?",
            options=['beginner', 'intermediate', 'advanced'],
            format_func=lambda x: {
                'beginner': '1. Beginner - No experience',
                'intermediate': '2. Intermediate - 6 months to 2 years training',
                'advanced': '3. Advanced - Over 2 years training'
            }[x],
            help="Select the option that best describes your experience"
        )
        
        user_goal = st.selectbox(
            "What is your main fitness goal?",
            options=['strength', 'hypertrophy', 'endurance', 'weight_loss', 'power', 'flexibility', 'general_fitness'],
            format_func=lambda x: {
                'strength': '1. Strength',
                'hypertrophy': '2. Hypertrophy (Muscle Mass)',
                'endurance': '3. Endurance',
                'weight_loss': '4. Weight Loss',
                'power': '5. Power & Explosiveness',
                'flexibility': '6. Flexibility & Mobility',
                'general_fitness': '7. General Fitness'
            }[x],
            help="Choose your primary training goal"
        )
    
    with col2:
        st.subheader("Training Preferences")
        days = st.slider(
            "How many training days per week?",
            min_value=1,
            max_value=7,
            value=3,
            help="Select the number of days you want to train"
        )
        
        split = st.selectbox(
            "Choose your preferred training split:",
            options=['FB', 'AB'],
            format_func=lambda x: {
                'FB': '1. Full Body (FB) - recommended for beginners',
                'AB': '2. A/B Split (AB) - recommended for intermediate and advanced'
            }[x],
            help="Full Body trains all muscles each day. A/B Split alternates muscle groups."
        )
    
    # Workout location question - use session state to track changes
    st.subheader("📍 Workout Location")
    
    # Initialize workout location in session state
    if 'workout_location' not in st.session_state:
        st.session_state.workout_location = 'home'
    
    workout_location = st.selectbox(
        "Where do you work out?",
        options=['home', 'limited_equipment_gym', 'well_equipped_gym', 'outdoor', 'travel', 'bodyweight_only'],
        format_func=lambda x: {
            'home': '🏠 Home Gym',
            'limited_equipment_gym': '🏋️ Limited Equipment Gym',
            'well_equipped_gym': '🏢 Well Equipped Gym',
            'outdoor': '🌳 Outdoor Training',
            'travel': '✈️ Travel / Hotel Room',
            'bodyweight_only': '🤸 Bodyweight Only'
        }[x],
        index=['home', 'limited_equipment_gym', 'well_equipped_gym', 'outdoor', 'travel', 'bodyweight_only'].index(st.session_state.workout_location) if st.session_state.workout_location in ['home', 'limited_equipment_gym', 'well_equipped_gym', 'outdoor', 'travel', 'bodyweight_only'] else 0,
        key='workout_location_select',
        help="Select your workout location to set default equipment"
    )
    
    st.subheader("🏋️ Available Equipment")
    equipment_options = st.session_state.get('equipment_options', [])
    
    # Fallback equipment list if not in database
    if not equipment_options:
        equipment_options = [
            {"id": "none", "name": "None"},
            {"id": "yoga mat", "name": "Yoga Mat"},
            {"id": "dumbbells", "name": "Dumbbells"},
            {"id": "resistance bands", "name": "Resistance Bands"},
            {"id": "pull-up bar", "name": "Pull-up Bar"},
            {"id": "kettlebells", "name": "Kettlebells"},
            {"id": "barbell", "name": "Barbell"},
            {"id": "cable machine", "name": "Cable Machine"},
            {"id": "foam roller", "name": "Foam Roller"},
            {"id": "medicine ball", "name": "Medicine Ball"},
            {"id": "suspension trainer", "name": "Suspension Trainer (TRX)"},
            {"id": "exercise ball", "name": "Exercise Ball"},
            {"id": "bench", "name": "Workout Bench"},
            {"id": "power rack", "name": "Power Rack"},
            {"id": "smith machine", "name": "Smith Machine"}
        ]
    
    # Determine default equipment based on location
    default_equipment = []
    if workout_location == 'home':
        # Home: basic home equipment
        default_equipment = ['yoga mat', 'dumbbells', 'resistance bands', 'pull-up bar']
    elif workout_location == 'limited_equipment_gym':
        # Limited equipment gym: basic gym equipment
        default_equipment = [
            'dumbbells', 'barbell', 'bench', 'pull-up bar', 'kettlebells',
            'yoga mat', 'foam roller'
        ]
    elif workout_location == 'well_equipped_gym':
        # Well equipped gym: full access to almost everything
        default_equipment = [
            'dumbbells', 'barbell', 'bench', 'pull-up bar', 'cable machine',
            'power rack', 'smith machine', 'kettlebells', 'yoga mat',
            'foam roller', 'medicine ball', 'exercise ball'
        ]
    elif workout_location == 'outdoor':
        # Outdoor: pull-up bar and minimal portable equipment
        default_equipment = ['pull-up bar', 'resistance bands', 'yoga mat']
    elif workout_location == 'travel':
        # Travel/Hotel: portable equipment only
        default_equipment = ['resistance bands', 'yoga mat']
    elif workout_location == 'bodyweight_only':
        # Bodyweight only: no equipment
        default_equipment = []
    
    # Check if location changed and update defaults
    location_changed = False
    if workout_location != st.session_state.workout_location:
        st.session_state.workout_location = workout_location
        location_changed = True
    
    # Initialize or update equipment checkboxes based on location
    if 'equipment_checkboxes' not in st.session_state or location_changed:
        st.session_state.equipment_checkboxes = {}
        for equipment in equipment_options:
            st.session_state.equipment_checkboxes[equipment['id']] = equipment['id'] in default_equipment
    
    # Create checkboxes in columns for better layout
    st.write("**Select all equipment you have access to:**")
    
    user_equipment = []
    # Group equipment into rows of 3 columns
    for i in range(0, len(equipment_options), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(equipment_options):
                equipment = equipment_options[idx]
                with col:
                    # Get checkbox value from session state
                    checkbox_value = st.session_state.equipment_checkboxes.get(equipment['id'], False)
                    
                    # Use a unique key that includes location to reset when location changes
                    checkbox_key = f"equip_{equipment['id']}_{workout_location}"
                    
                    # Update session state if this is a new location (new key)
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = checkbox_value
                    elif location_changed:
                        # Location changed, update checkbox value
                        st.session_state[checkbox_key] = checkbox_value
                    
                    # Create checkbox
                    new_value = st.checkbox(
                        equipment['name'], 
                        key=checkbox_key
                    )
                    
                    # Update session state for equipment checkboxes
                    st.session_state.equipment_checkboxes[equipment['id']] = new_value
                    
                    if new_value and equipment['id'] != 'none':  # Don't add 'none' to the list
                        user_equipment.append(equipment['id'])
    
    return user_level, user_goal, user_equipment, days, split


def render_exercise_details(exercise_name: str, exercise_data: Dict[str, Any]):
    """
    Render exercise details in an expandable section.
    Only available to logged-in users.
    
    Args:
        exercise_name: Name of the exercise
        exercise_data: Exercise data dictionary
    """
    # Only show details to authenticated users
    if not is_authenticated():
        st.info("🔒 Sign up or login to unlock exercise details, tips, and video tutorials!")
        return
    
    has_details = any(key in exercise_data for key in ['instructions', 'tips', 'common_mistakes'])
    
    if not has_details:
        return
    
    with st.expander(f"ℹ️ Exercise Details: {exercise_name}"):
        # Instructions
        if 'instructions' in exercise_data and exercise_data['instructions']:
            st.subheader("📋 Instructions")
            for i, instruction in enumerate(exercise_data['instructions'], 1):
                st.write(f"{i}. {instruction}")
            st.markdown("---")
        
        # Tips
        if 'tips' in exercise_data and exercise_data['tips']:
            st.subheader("💡 Pro Tips")
            for tip in exercise_data['tips']:
                st.write(f"• {tip}")
            st.markdown("---")
        
        # Common Mistakes
        if 'common_mistakes' in exercise_data and exercise_data['common_mistakes']:
            st.subheader("⚠️ Common Mistakes to Avoid")
            for mistake in exercise_data['common_mistakes']:
                st.write(f"• {mistake}")
        
        # Video link
        if 'video' in exercise_data and exercise_data['video']:
            st.markdown("---")
            st.subheader("🎥 Video Tutorial")
            st.markdown(f"[Watch on YouTube]({exercise_data['video']})")


def find_exercise_alternatives(exercise_name: str, exercises: Dict[str, Dict[str, Any]], 
                              user_level: str, user_equipment: List[str]) -> List[str]:
    """
    Find alternative exercises for a given exercise.
    Alternatives must target the same muscle group and be appropriate for user level/equipment.
    
    Args:
        exercise_name: Name of the exercise to find alternatives for
        exercises: Dictionary of all exercises
        user_level: User's fitness level
        user_equipment: User's available equipment
        
    Returns:
        List of alternative exercise names
    """
    if exercise_name not in exercises:
        return []
    
    original_ex = exercises[exercise_name]
    target_muscle = original_ex['muscle']
    original_level = original_ex['level']
    original_equipment = set(original_ex.get('equipment', []))
    
    alternatives = []
    for name, ex in exercises.items():
        if name == exercise_name:
            continue  # Skip the original exercise
        
        # Must target the same muscle group
        if ex['muscle'] != target_muscle:
            continue
        
        # Must be appropriate for user level
        levels = ['beginner', 'intermediate', 'advanced']
        if levels.index(user_level) < levels.index(ex['level']):
            continue
        
        # Must use equipment user has (or no equipment)
        ex_equipment = set(ex.get('equipment', []))
        if ex_equipment and not ex_equipment.issubset(set(user_equipment)):
            continue
        
        alternatives.append(name)
    
    # Sort by level similarity (prefer same level, then similar)
    def sort_key(name: str) -> tuple:
        ex = exercises[name]
        level_match = 0 if ex['level'] == original_level else 1
        equipment_similarity = len(original_equipment & set(ex.get('equipment', [])))
        return (level_match, -equipment_similarity)
    
    alternatives.sort(key=sort_key)
    return alternatives[:5]  # Return top 5 alternatives


def render_workout_plan(daily_plan, user_level, user_goal, exercises, goal_set_rep):
    """Render the generated workout plan as a table with days as columns."""
    # Check if there's actually any content to display
    has_content = any(len(day_exercises) > 0 for day_exercises in daily_plan) if daily_plan else False
    
    if not has_content:
        return  # Don't render anything if there's no content
    
    st.header("💪 Your Personalized Workout Plan")
    st.markdown("---")
    
    # Get sets/reps with fallback
    sets_reps = goal_set_rep.get(user_goal, {}).get(user_level, "3x10-12")
    
    # Create table columns (one for each day)
    num_days = len(daily_plan)
    cols = st.columns(num_days)
    
    # Muscle group display names with emojis
    muscle_display_names = {
        'chest': '💪 Chest',
        'back': '🔙 Back',
        'legs': '🦵 Legs',
        'triceps': '💪 Triceps',
        'shoulders': '🏋️ Shoulders',
        'core': '🔥 Core',
        'biceps': '💪 Biceps'
    }
    
    # Find the maximum number of exercises across all days for table height
    max_exercises = max(len(day_exercises) for day_exercises in daily_plan) if daily_plan else 0
    
    # Group exercises by muscle group for each day
    # Store mapping from exercise name to its position for replacement
    exercise_positions = {}  # {(day_idx, ex_name): (muscle_group, index_in_muscle_group)}
    
    days_data = []
    for day, exs in enumerate(daily_plan):
        if not exs:
            days_data.append([("Rest day", "Enjoy your recovery! 🧘")])
        else:
            # Group exercises by muscle group
            muscle_groups = defaultdict(list)
            for ex in exs:
                muscle = exercises[ex]['muscle']
                muscle_groups[muscle].append(ex)
            
            # Format exercises with muscle group headers
            formatted_exercises = []
            for muscle_group in sorted(muscle_groups.keys()):
                display_name = muscle_display_names.get(muscle_group, muscle_group.title())
                formatted_exercises.append((f"**{display_name}**", ""))
                for idx, ex in enumerate(muscle_groups[muscle_group]):
                    level = exercises[ex]['level'].title()
                    formatted_exercises.append((ex, f"Level: {level} | {sets_reps}"))
                    # Store position for replacement
                    exercise_positions[(day, ex)] = (muscle_group, idx)
            days_data.append(formatted_exercises)
    
    # Store exercise positions in session state for replacement
    st.session_state.exercise_positions = exercise_positions
    
    # Display each day in its column
    for day_idx, col in enumerate(cols):
        with col:
            st.markdown(f"### Day {day_idx + 1}")
            st.markdown(f'<div class="workout-day">', unsafe_allow_html=True)
            
            day_exercises = days_data[day_idx] if day_idx < len(days_data) else []
            
            if not day_exercises or (len(day_exercises) == 1 and day_exercises[0][0] == "Rest day"):
                if day_exercises and day_exercises[0][0] == "Rest day":
                    st.info(day_exercises[0][1])
                else:
                    st.info("Rest day - Enjoy your recovery! 🧘")
            else:
                exercise_counter = 0
                for ex_name, ex_details in day_exercises:
                    if ex_details == "":  # Muscle group header
                        st.markdown(ex_name)
                    else:  # Exercise
                        exercise_counter += 1
                        
                        # Find alternatives for this exercise
                        user_equipment_list = st.session_state.get('user_equipment', [])
                        alternatives = find_exercise_alternatives(
                            ex_name, exercises, user_level, user_equipment_list
                        )
                        
                        # Create unique key for this exercise
                        exercise_key = f"day_{day_idx}_ex_{exercise_counter}_{ex_name}"
                        
                        # Display exercise with details and video buttons
                        col_ex_name, col_buttons = st.columns([4, 2])
                        
                        with col_ex_name:
                            st.markdown(f"""
                            <div class="exercise-item">
                                <strong>{ex_name}</strong><br>
                                <small>{ex_details}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_buttons:
                            # Video button - only for logged-in users
                            if is_authenticated() and ex_name in exercises and exercises[ex_name].get('video'):
                                video_url = exercises[ex_name]['video']
                                video_key = f"{exercise_key}_video"
                                st.markdown(f'<a href="{video_url}" target="_blank" class="video-button">🎥 Video</a>', unsafe_allow_html=True)
                            elif ex_name in exercises and exercises[ex_name].get('video'):
                                # Show locked icon for guests
                                st.markdown('<span title="Sign up to unlock video tutorials">🔒</span>', unsafe_allow_html=True)
                            
                            # Details button - only for logged-in users
                            if is_authenticated() and ex_name in exercises and any(key in exercises[ex_name] 
                                                           for key in ['instructions', 'tips', 'common_mistakes']):
                                details_key = f"{exercise_key}_details"
                                if st.button("ℹ️", key=details_key):
                                    # Toggle exercise details
                                    if 'selected_exercise' in st.session_state and st.session_state.selected_exercise == ex_name:
                                        del st.session_state.selected_exercise
                                    else:
                                        st.session_state.selected_exercise = ex_name
                                    st.rerun()
                            elif ex_name in exercises and any(key in exercises[ex_name] 
                                                           for key in ['instructions', 'tips', 'common_mistakes']):
                                # Show locked icon for guests
                                st.markdown('<span title="Sign up to unlock exercise details">🔒</span>', unsafe_allow_html=True)
                        
                        # Show exercise details if selected
                        if 'selected_exercise' in st.session_state and st.session_state.selected_exercise == ex_name:
                            render_exercise_details(ex_name, exercises[ex_name])
                        
                        # Display alternatives expander below the exercise
                        if alternatives:
                            with st.expander("🔄 See Alternatives"):
                                st.write("**Alternatives:**")
                                for alt_idx, alt in enumerate(alternatives):
                                    alt_level = exercises[alt]['level'].title()
                                    alt_equipment = ", ".join(exercises[alt].get('equipment', ['None']))
                                    
                                    # Use a unique key for each alternative button
                                    alt_button_key = f"{exercise_key}_alt_{alt_idx}"
                                    
                                    if st.button(f"→ {alt}", key=alt_button_key, 
                                                use_container_width=True):
                                        # Replace exercise in the plan
                                        if 'workout_plan' in st.session_state:
                                            day_plan = st.session_state.workout_plan[day_idx]
                                            # Find and replace the first occurrence of this exercise
                                            if ex_name in day_plan:
                                                replace_idx = day_plan.index(ex_name)
                                                day_plan[replace_idx] = alt
                                                st.session_state.workout_plan[day_idx] = day_plan
                                                st.rerun()
                                    
                                    st.caption(f"{alt_level} | {alt_equipment}")
                
                st.caption("⏱️ Rest: 60-90s between sets")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def generate_pdf(daily_plan: List[List[str]], user_level: str, user_goal: str, 
                exercises: Dict[str, Dict[str, Any]], goal_set_rep: Dict[str, Dict[str, str]]) -> BytesIO:
    """
    Generate a PDF document of the workout plan.
    
    Args:
        daily_plan: List of daily workout plans
        user_level: User's fitness level
        user_goal: User's training goal
        exercises: Dictionary of all exercises
        goal_set_rep: Dictionary of set/rep schemes
        
    Returns:
        BytesIO object containing the PDF
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is not installed. Please install it with: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("💪 Your Personalized Workout Plan", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # User info
    elements.append(Paragraph(f"<b>Level:</b> {user_level.title()} | <b>Goal:</b> {user_goal.replace('_', ' ').title()}", 
                             styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get sets/reps
    sets_reps = goal_set_rep.get(user_goal, {}).get(user_level, "3x10-12")
    
    # Muscle group display names
    muscle_display_names = {
        'chest': '💪 Chest',
        'back': '🔙 Back',
        'legs': '🦵 Legs',
        'triceps': '💪 Triceps',
        'shoulders': '🏋️ Shoulders',
        'core': '🔥 Core',
        'biceps': '💪 Biceps'
    }
    
    # Process each day
    for day_idx, day_exercises in enumerate(daily_plan):
        if day_idx > 0:
            elements.append(PageBreak())
        
        # Day header
        elements.append(Paragraph(f"Day {day_idx + 1}", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        if not day_exercises:
            elements.append(Paragraph("Rest day - Enjoy your recovery! 🧘", styles['Normal']))
            continue
        
        # Group exercises by muscle group
        muscle_groups = defaultdict(list)
        for ex in day_exercises:
            muscle = exercises[ex]['muscle']
            muscle_groups[muscle].append(ex)
        
        # Create table data
        table_data = [['Exercise', 'Level', 'Sets & Reps']]
        
        for muscle_group in sorted(muscle_groups.keys()):
            display_name = muscle_display_names.get(muscle_group, muscle_group.title())
            # Add muscle group as a merged row
            table_data.append([f"<b>{display_name}</b>", "", ""])
            
            for ex in muscle_groups[muscle_group]:
                level = exercises[ex]['level'].title()
                table_data.append([ex, level, sets_reps])
            
            # Add spacing row
            table_data.append(["", "", ""])
        
        # Create table
        table = Table(table_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<i>⏱️ Rest: 60-90s between sets</i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def plot_exercise_graph(exercises):
    """Generate and display the exercise progression graph."""
    G = nx.DiGraph()
    
    for ex, data in exercises.items():
        G.add_node(ex, level=data['level'])
        for pre in data['prerequisites']:
            if pre in exercises:  # Only add edge if prerequisite exists
                G.add_edge(pre, ex)
    
    if len(G.nodes()) == 0:
        st.warning("No exercises to visualize.")
        return
    
    pos = nx.spring_layout(G, seed=42, k=1.5, iterations=50)
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Color nodes by level
    node_colors = []
    for n in G.nodes():
        level = exercises[n]['level']
        color_map = {
            'beginner': '#90ee90',
            'intermediate': '#add8e6',
            'advanced': '#ffb3b3'
        }
        node_colors.append(color_map.get(level, '#cccccc'))
    
    nx.draw(
        G, pos, 
        with_labels=True,
        node_color=node_colors,
        node_size=2500,
        font_size=10,
        edge_color='gray',
        arrows=True,
        font_weight='bold',
        ax=ax,
        alpha=0.8
    )
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#90ee90', label='Beginner'),
        Patch(facecolor='#add8e6', label='Intermediate'),
        Patch(facecolor='#ffb3b3', label='Advanced')
    ]
    ax.legend(handles=legend_elements, loc='upper left')
    
    ax.set_title("Exercise Progression Graph (BFS Path)", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)


def render_signup_page():
    """Render the sign up page."""
    st.markdown('<div class="main-header">📝 Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sign up to get started</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        name = st.text_input("Full Name (Optional)")
        email = st.text_input("Email Address *", placeholder="your.email@example.com")
        password = st.text_input("Password *", type="password", help="At least 6 characters")
        password_confirm = st.text_input("Confirm Password *", type="password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("📝 Sign Up", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not email or not password:
                st.error("Please fill in all required fields")
            elif password != password_confirm:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                # Create user account
                with st.spinner("Creating your account..."):
                    result = create_user(email, password, name)
                    
                    if result["success"]:
                        st.success(result["message"])
                        if result.get("email_sent"):
                            st.info("📧 Check your email for verification link. You can sign up again after verifying.")
                        else:
                            st.info("✅ Account created! Email service not configured, so your account is automatically verified. You can log in now!")
                        # Set flag to show login button after form
                        st.session_state.show_login_after_signup = True
                    else:
                        st.error(result["message"])
    
    # Show login button after successful signup (outside the form)
    if st.session_state.get("show_login_after_signup", False):
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔐 Go to Login", type="primary", use_container_width=True):
                st.session_state.show_login_after_signup = False
                st.session_state.current_page = "login"
                st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("🔐 Login Instead", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.current_page = "welcome"
            st.rerun()


def render_login_page():
    """Render the login page."""
    st.markdown('<div class="main-header">🔐 Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sign in to your account</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Logging in..."):
                    result = login_user(email, password)
                    
                    if result["success"]:
                        # Store user in session state
                        st.session_state.user = result["user"]
                        st.success(f"Welcome back, {result['user'].get('name', 'User')}!")
                        # Navigate to input page
                        st.session_state.current_page = "input"
                        st.rerun()
                    else:
                        st.error(result["message"])
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("📝 Sign Up", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔑 Forgot Password?", use_container_width=True):
            st.session_state.current_page = "forgot_password"
            st.rerun()
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.current_page = "welcome"
            st.rerun()


def render_forgot_password_page():
    """Render the forgot password page."""
    st.markdown('<div class="main-header">🔑 Reset Password</div>', unsafe_allow_html=True)
    
    # Check if we're in reset mode (code entry)
    if st.session_state.get("password_reset_mode") == "enter_code":
        email = st.session_state.get("reset_email", "")
        reset_code = st.session_state.get("reset_code", "")
        email_sent = st.session_state.get("email_sent", False)
        
        st.markdown('<div class="sub-header">Enter your reset code</div>', unsafe_allow_html=True)
        
        if email_sent:
            st.success(f"📧 Password reset code sent to **{email}**")
            st.info("Please check your email (including spam folder) for the 6-digit reset code.")
        else:
            # Only show code if email service is NOT configured (fallback mode)
            if reset_code:
                st.info(f"📧 Reset code generated for **{email}**")
                # Display the reset code prominently if email wasn't sent (fallback only)
                st.markdown("---")
                st.markdown("### Your Reset Code:")
                st.markdown(f"<h1 style='text-align: center; color: #1f77b4; font-size: 3rem; letter-spacing: 0.5rem;'>{reset_code}</h1>", unsafe_allow_html=True)
                st.warning("⚠️ **Save this code!** You'll need it to reset your password. It expires in 1 hour.")
            else:
                # Email service is configured but failed - don't show code
                st.error("❌ Email service is configured but failed to send. Please check your email or try again.")
                st.info("💡 If you didn't receive an email, check your spam folder or contact support.")
        
        st.markdown("---")
        
        with st.form("reset_password_form"):
            st.text_input("Email Address", value=email, disabled=True)
            code = st.text_input("Reset Code", placeholder="Enter the 6-digit code", help="Enter the code from your email" if email_sent else "Enter the code shown above")
            new_password = st.text_input("New Password", type="password", placeholder="Enter your new password")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm your new password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🔑 Reset Password", type="primary", use_container_width=True)
            
            if submitted:
                if not code or not new_password or not confirm_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif len(code) != 6 or not code.isdigit():
                    st.error("Reset code must be 6 digits")
                else:
                    with st.spinner("Resetting password..."):
                        result = reset_password_with_code(email, code, new_password)
                        
                        if result["success"]:
                            st.success(result["message"])
                            st.session_state.password_reset_mode = None
                            st.session_state.reset_email = None
                            st.session_state.reset_code = None
                            st.session_state.email_sent = None
                            st.info("You can now log in with your new password.")
                            if st.button("🔐 Go to Login", type="primary", use_container_width=True):
                                st.session_state.current_page = "login"
                                st.rerun()
                        else:
                            st.error(result["message"])
    else:
        # Request reset code
        st.markdown('<div class="sub-header">Enter your email to receive a reset code</div>', unsafe_allow_html=True)
        st.info("💡 A 6-digit reset code will be sent to your email address.")
        
        with st.form("forgot_password_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("📧 Send Reset Code", type="primary", use_container_width=True)
            
            if submitted:
                if not email:
                    st.error("Please enter your email address")
                else:
                    with st.spinner("Sending reset code..."):
                        result = request_password_reset(email)
                        
                        if result["success"]:
                            if result.get("email_sent"):
                                # Email sent successfully
                                st.success(result["message"])
                                st.session_state.password_reset_mode = "enter_code"
                                st.session_state.reset_email = result["email"]
                                st.session_state.email_sent = True
                                st.rerun()
                            elif result.get("reset_code"):
                                # Email not configured - show code on screen (fallback only)
                                st.success(result["message"])
                                st.session_state.password_reset_mode = "enter_code"
                                st.session_state.reset_email = result["email"]
                                st.session_state.reset_code = result["reset_code"]
                                st.session_state.email_sent = False
                                st.rerun()
                            else:
                                # Email doesn't exist (security - don't reveal)
                                st.info(result["message"])
                        else:
                            # Email failed - show error, don't show code
                            st.error(result["message"])
                            st.info("💡 Please check your email (including spam folder). If you didn't receive it, the code may have been sent. Try entering the code from your email.")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.password_reset_mode = None
            st.session_state.reset_email = None
            st.session_state.reset_code = None
            st.session_state.email_sent = None
            st.session_state.current_page = "login"
            st.rerun()
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.password_reset_mode = None
            st.session_state.reset_email = None
            st.session_state.reset_code = None
            st.session_state.email_sent = None
            st.session_state.current_page = "welcome"
            st.rerun()


def render_welcome_page():
    """Render the welcome/home page."""
    # Check for email verification token in URL parameters
    query_params = st.query_params
    if "token" in query_params and "email" in query_params:
        token = query_params["token"]
        email = query_params["email"]
        
        # Create a unique key for this verification attempt to process it only once
        verification_key = f"verified_{email}_{token}"
        
        # Only process verification if we haven't processed this token/email combination before
        if verification_key not in st.session_state:
            st.session_state[verification_key] = True  # Mark as processed
            
            with st.spinner("Verifying your email..."):
                result = verify_email_token(email, token)
                st.session_state['last_verification_result'] = result
                
                # Clear query parameters from URL after processing
                new_params = dict(query_params)
                new_params.pop("token", None)
                new_params.pop("email", None)
                # Clear all params and set new ones (without token/email)
                st.query_params.clear()
                if new_params:
                    st.query_params.update(new_params)
        
        # Display verification result (from cache if already processed)
        if 'last_verification_result' in st.session_state:
            result = st.session_state['last_verification_result']
            if result.get("success"):
                st.success("✅ " + result["message"])
                st.info("You can now log in with your email and password.")
            else:
                st.error("❌ " + result.get("message", "Verification failed. Please try signing up again or contact support."))
                st.info("💡 If you didn't receive an email, your account may have been auto-verified. Try logging in.")
    
    st.markdown('<div class="main-header">💪 Workout Plan Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by BFS Algorithm</div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if user is already logged in
        if is_authenticated():
            user = get_current_user()
            st.success(f"Welcome back, {user.get('name', user.get('email', 'User'))}!")
            if st.button("🚀 Continue to Workout Generator", type="primary", use_container_width=True):
                st.session_state.current_page = "input"
                st.rerun()
            if st.button("🔐 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            # Show login/signup options
            if st.button("📝 Sign Up", type="primary", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
            
            # Require signup/login - no guest access
            st.markdown("---")
            st.info("🔒 **Sign up or login required** to access the workout generator and unlock exercise details, tips, and video tutorials!")


def render_input_page():
    """Render the user input page."""
    # Require authentication to access this page
    if not is_authenticated():
        st.warning("🔒 Please sign up or login to access the workout generator!")
        st.info("Create a free account to unlock exercise details, tips, and video tutorials.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📝 Sign Up", type="primary", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.current_page = "welcome"
                st.rerun()
        return  # Stop rendering the rest of the page
    
    # Load data (will use web_source from sidebar if provided)
    load_data(st.session_state.get('web_data_source'))
    
    # Sidebar
    with st.sidebar:
        # Show user info if logged in
        if is_authenticated():
            user = get_current_user()
            st.markdown('<p class="sidebar-section-title">👤 Account</p>', unsafe_allow_html=True)
            st.info(f"**{user.get('name', 'User')}**\n{user.get('email', '')}")
            if st.button("🔐 Logout", use_container_width=True):
                logout_user()
                st.session_state.current_page = "welcome"
                st.rerun()
            st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">⚙️ Settings</p>', unsafe_allow_html=True)
        
        st.markdown("**💡 Quick Tip**")
        st.info("You can load exercise data from a web URL for maximum flexibility!")
        
        st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">🌐 Load Data Source</p>', unsafe_allow_html=True)
        st.caption("Load exercise data from a web URL (optional)")
        web_source = st.text_input(
            "Data URL",
            value=st.session_state.get('web_data_source', ''),
            placeholder="https://example.com/exercises.json",
            help="Enter a URL to load exercise data from the web. Leave empty to use the local file.",
            key="web_data_source_input"
        )
        
        # Store in session state
        if web_source and web_source.strip():
            st.session_state.web_data_source = web_source.strip()
            st.caption(f"📡 Will load from: {web_source[:50]}...")
        else:
            st.session_state.web_data_source = None
            st.caption("📁 Using local data file")
        
        st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">📊 Data Management</p>', unsafe_allow_html=True)
        if st.button("🔄 Reload Data", use_container_width=True):
            if 'exercise_data' in st.session_state:
                del st.session_state.exercise_data
            # Reload with current web source
            load_data(st.session_state.get('web_data_source'))
            st.success("Data reloaded!")
            st.rerun()
        
        st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">🔧 System Status</p>', unsafe_allow_html=True)
        with st.expander("View Status", expanded=False):
            if REPORTLAB_AVAILABLE:
                st.success("✅ PDF Export Available")
                st.caption("reportlab is installed and ready")
            else:
                st.warning("⚠️ PDF Export Disabled")
                st.caption("Install: pip install reportlab")
                st.caption("Then restart Streamlit")
    
    # User questions
    user_level, user_goal, user_equipment, days, split = render_user_questions()
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate My Workout Plan", type="primary", use_container_width=True)
    
    if generate_button:
        # Generate workout plan
        # The BFS algorithm will filter exercises based on user level and equipment
        with st.spinner("Generating your personalized workout plan..."):
            try:
                daily_plan = bfs_reserve_workout_plan(
                    st.session_state.exercises,
                    user_level,
                    user_equipment,
                    days,
                    split
                )
                
                # Check if plan was generated successfully
                total_exercises = sum(len(day) for day in daily_plan)
                if total_exercises == 0:
                    st.warning("⚠️ No exercises available with your selected criteria. Please adjust your equipment selection or fitness level.")
                else:
                    # Store in session state only if plan has exercises
                    st.session_state.workout_plan = daily_plan
                    st.session_state.user_level = user_level
                    st.session_state.user_goal = user_goal
                    st.session_state.user_equipment = user_equipment
                    
                    # Save user preferences if logged in
                    if is_authenticated():
                        try:
                            from user_data import save_user_workout_preferences
                            user = get_current_user()
                            user_id = user.get('id') or user.get('email')
                            workout_location = st.session_state.get('workout_location', 'home')
                            
                            save_result = save_user_workout_preferences(
                                user_id=user_id,
                                fitness_level=user_level,
                                fitness_goal=user_goal,
                                training_days=days,
                                training_split=split,
                                workout_location=workout_location,
                                equipment=user_equipment,
                                workout_plan=daily_plan
                            )
                            # Don't show message here, it will interrupt the flow
                        except Exception as e:
                            pass  # Silently fail if saving preferences fails
                    
                    # Navigate to results page
                    st.session_state.current_page = "results"
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error generating workout plan: {e}")
                return


def render_results_page():
    """Render the workout plan results page."""
    # Require authentication to view results
    if not is_authenticated():
        st.warning("🔒 Please sign up or login to view workout plans!")
        st.info("Create a free account to unlock exercise details, tips, and video tutorials.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📝 Sign Up", type="primary", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
            if st.button("← Back to Home", use_container_width=True):
                st.session_state.current_page = "welcome"
                st.rerun()
        return  # Stop rendering the rest of the page
    
    # Load data if not already loaded (will use web_source from session state if provided)
    load_data(st.session_state.get('web_data_source'))
    
    # Sidebar
    with st.sidebar:
        # Show user info if logged in
        if is_authenticated():
            user = get_current_user()
            st.markdown('<p class="sidebar-section-title">👤 Account</p>', unsafe_allow_html=True)
            st.info(f"**{user.get('name', 'User')}**\n{user.get('email', '')}")
            if st.button("🔐 Logout", use_container_width=True):
                logout_user()
                st.session_state.current_page = "welcome"
                st.rerun()
            st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">🎯 Navigation</p>', unsafe_allow_html=True)
        
        if st.button("🔄 Generate New Plan", use_container_width=True):
            # Clear workout plan and go back to input
            if 'workout_plan' in st.session_state:
                del st.session_state.workout_plan
            st.session_state.current_page = "input"
            st.rerun()
        
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "welcome"
            st.rerun()
        
        st.markdown("---")
        
        st.markdown('<p class="sidebar-section-title">🔧 System Status</p>', unsafe_allow_html=True)
        with st.expander("View Status", expanded=False):
            if REPORTLAB_AVAILABLE:
                st.success("✅ PDF Export Available")
                st.caption("reportlab is installed and ready")
            else:
                st.warning("⚠️ PDF Export Disabled")
                st.caption("Install: pip install reportlab")
                st.caption("Then restart Streamlit")
    
    # Display workout plan
    if 'workout_plan' in st.session_state:
        render_workout_plan(
            st.session_state.workout_plan,
            st.session_state.user_level,
            st.session_state.user_goal,
            st.session_state.exercises,
            st.session_state.goal_set_rep
        )
        
        # Export PDF button - after the workout plan
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if REPORTLAB_AVAILABLE:
                try:
                    pdf_buffer = generate_pdf(
                        st.session_state.workout_plan,
                        st.session_state.user_level,
                        st.session_state.user_goal,
                        st.session_state.exercises,
                        st.session_state.goal_set_rep
                    )
                    st.download_button(
                        label="📥 Export Plan to PDF",
                        data=pdf_buffer,
                        file_name=f"workout_plan_{st.session_state.user_level}_{st.session_state.user_goal}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {e}")
                    st.info("💡 Make sure reportlab is installed in the same Python environment as Streamlit")
            else:
                st.button(
                    label="📥 Export Plan to PDF",
                    disabled=True,
                    use_container_width=True,
                    help="reportlab is not available. Install with: pip install reportlab"
                )
                st.caption("⚠️ reportlab not detected. Restart Streamlit after installing.")
        
        # Visualization tab
        st.markdown("---")
        with st.expander("📊 View Exercise Progression Graph", expanded=False):
            plot_exercise_graph(st.session_state.exercises)
    else:
        st.warning("No workout plan found. Please generate a plan first.")
        if st.button("Go to Input Page"):
            st.session_state.current_page = "input"
            st.rerun()


def main():
    """Main application function."""
    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "welcome"
    
    # Handle email verification from URL - only redirect on first detection, not every rerun
    query_params = st.query_params
    if "token" in query_params and "email" in query_params:
        token = query_params.get("token")
        email = query_params.get("email")
        verification_redirect_key = f"verification_redirect_{email}_{token}"
        
        # Only redirect if we haven't seen this verification before
        if verification_redirect_key not in st.session_state:
            st.session_state[verification_redirect_key] = True
            st.session_state.current_page = "welcome"  # Show welcome page for verification message
    
    # Render appropriate page based on current_page
    if st.session_state.current_page == "welcome":
        render_welcome_page()
    elif st.session_state.current_page == "signup":
        render_signup_page()
    elif st.session_state.current_page == "login":
        render_login_page()
    elif st.session_state.current_page == "forgot_password":
        render_forgot_password_page()
    elif st.session_state.current_page == "input":
        render_input_page()
    elif st.session_state.current_page == "results":
        render_results_page()


if __name__ == "__main__":
    main()