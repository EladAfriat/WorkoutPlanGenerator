from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

def get_user_level():
    print("\nWhat is your fitness level?")
    print("1. No experience")
    print("2. 6 months to 2 years training")
    print("3. Over 2 years training")
    while True:
        level_input = input("Select your level (1-3): ").strip()
        if level_input in ['1', '2', '3']:
            return {'1': 'beginner', '2': 'intermediate', '3': 'advanced'}[level_input]
        print("Invalid input. Please try again.")

def get_user_goal():
    print("\nWhat is your main fitness goal?")
    print("1. Strength")
    print("2. Hypertrophy (Muscle Mass)")
    print("3. Endurance")
    while True:
        goal_input = input("Select your goal (1-3): ").strip()
        if goal_input in ['1', '2', '3']:
            return {'1': 'strength', '2': 'hypertrophy', '3': 'endurance'}[goal_input]
        print("Invalid input. Please try again.")

def get_user_equipment():
    print("\nSelect available equipment:")
    print("1. None")
    print("2. Dumbbells")
    print("3. Resistance Bands")
    print("4. Pull-up Bar")
    print("5. Barbell")
    print("6. Cable Machine")
    print("(Enter numbers separated by comma, e.g., 2,3,5)")
    equipment_input = input("Available equipment: ")
    equipment_numbers = [num.strip() for num in equipment_input.split(',')]
    equipment_map = {
        '1': 'none',
        '2': 'dumbbells',
        '3': 'resistance bands',
        '4': 'pull-up bar',
        '5': 'barbell',
        '6': 'cable machine'
    }
    equipment = [equipment_map[num] for num in equipment_numbers if num in equipment_map]
    if 'none' in equipment:
        equipment = []
    return equipment

def get_training_days():
    print("\nHow many training days per week? (1-7)")
    while True:
        try:
            days = int(input("Enter number of training days (1–7): "))
            if 1 <= days <= 7:
                return days
            print("Please enter a number between 1 and 7.")
        except ValueError:
            print("Please enter a valid number.")

def get_split_type():
    print("\nChoose your preferred training split:")
    print("1. Full Body (FB) - recommended for beginners")
    print("2. A/B Split (AB) - recommended for intermediate and advanced")
    while True:
        split_input = input("Select your split (1-2): ").strip()
        if split_input in ['1', '2']:
            return {'1': 'FB', '2': 'AB'}[split_input]
        print("Invalid input. Please try again.")

def level_allowed(ex_level, user_level):
    levels = ['beginner', 'intermediate', 'advanced']
    return levels.index(user_level) >= levels.index(ex_level)

def equipment_allowed(ex_equipment, user_equipment):
    return all(eq in user_equipment for eq in ex_equipment)

def load_exercises_data(file_path=None):
    """
    Load exercise data from JSON file.
    
    Args:
        file_path: Path to JSON file. If None, uses default location.
        
    Returns:
        Dictionary containing exercises and goal_set_rep data
    """
    if file_path is None:
        # Default path relative to script location
        script_dir = Path(__file__).parent
        file_path = script_dir / "data" / "exercises.json"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Exercise data file not found at {file_path}. "
            "Please ensure the data/exercises.json file exists."
        )
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

# Load exercise data from external JSON file
try:
    exercise_data = load_exercises_data()
    exercises = exercise_data.get('exercises', {})
    goal_set_rep = exercise_data.get('goal_set_rep', {})
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Falling back to empty database. Please ensure data/exercises.json exists.")
    exercises = {}
    goal_set_rep = {}

def get_muscle_groups(split, day):
    if split == 'FB':
        return ['chest', 'back', 'legs', 'triceps', 'shoulders', 'core', 'biceps']
    elif split == 'AB':
        if day % 2 == 1:
            return ['chest', 'triceps', 'shoulders', 'core']
        else:
            return ['back', 'legs', 'biceps', 'core']

def bfs_reserve_workout_plan(exercises, user_level, user_equipment, days, split):
    available = {name: ex for name, ex in exercises.items()
                 if level_allowed(ex['level'], user_level) and equipment_allowed(ex['equipment'], user_equipment)}

    muscle_dict = defaultdict(list)
    for name, ex in available.items():
        muscle_dict[ex['muscle']].append(name)

    muscle_groups = [get_muscle_groups(split, i+1) for i in range(days)]
    used_per_muscle = defaultdict(set)
    reserve_per_muscle = {muscle: deque(muscle_dict[muscle]) for muscle in muscle_dict}

    daily_plan = []
    for day in range(days):
        plan_for_day = []
        for muscle in muscle_groups[day]:
            chosen = []
            reserve = reserve_per_muscle.get(muscle, deque())
            # Take up to 2 unused exercises for the day
            while reserve and len(chosen) < 2:
                ex = reserve.popleft()
                if ex not in used_per_muscle[muscle]:
                    chosen.append(ex)
                    used_per_muscle[muscle].add(ex)
            # If not enough, reset and start again
            if len(chosen) < 2:
                # refill reserve (allow repetition after all used)
                used_per_muscle[muscle] = set()
                reserve = deque(muscle_dict[muscle])
                while reserve and len(chosen) < 2:
                    ex = reserve.popleft()
                    if ex not in chosen:  # avoid double
                        chosen.append(ex)
                        used_per_muscle[muscle].add(ex)
                reserve_per_muscle[muscle] = reserve
            else:
                reserve_per_muscle[muscle] = reserve
            plan_for_day.extend(chosen)
        daily_plan.append(plan_for_day)
    return daily_plan

def print_plan(daily_plan, user_level, user_goal):
    print("\nYour Personalized Workout Plan:")
    print("=" * 50)
    for day, exs in enumerate(daily_plan, 1):
        print(f"\nDay {day}:")
        if not exs:
            print("Rest day")
        for i, ex in enumerate(exs, 1):
            sets_reps = goal_set_rep[user_goal][user_level]
            print(f"{i}. {ex}\t({exercises[ex]['muscle']})\t→\t{sets_reps}")
        print("Rest: 60-90s between sets")

def plot_graph(exercises):
    G = nx.DiGraph()
    for ex, data in exercises.items():
        G.add_node(ex, level=data['level'])
        for pre in data['prerequisites']:
            G.add_edge(pre, ex)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(13, 7))
    nx.draw(
        G, pos, with_labels=True,
        node_color=[{'beginner':'#90ee90', 'intermediate':'#add8e6', 'advanced':'#ffb3b3'}[exercises[n]['level']] for n in G.nodes()],
        node_size=2000, font_size=11, edge_color='gray', arrows=True, font_weight='bold'
    )
    plt.title("Exercise Progression Graph (BFS Path)")
    plt.savefig("workout_bfs_graph.png")
    print("Graph saved as workout_bfs_graph.png")
    plt.close()

if __name__ == "__main__":
    print("=== Workout Plan Generator ===")
    user_level = get_user_level()
    user_goal = get_user_goal()
    user_equipment = get_user_equipment()
    days = get_training_days()
    split = get_split_type()
    daily_plan = bfs_reserve_workout_plan(exercises, user_level, user_equipment, days, split)
    print_plan(daily_plan, user_level, user_goal)
    plot_graph(exercises)
