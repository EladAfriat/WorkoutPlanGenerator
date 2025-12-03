# Workout Plan Generator 💪

A smart workout plan generator using BFS (Breadth-First Search) algorithm, built with Streamlit for an interactive web interface.

## Features

- **BFS Algorithm**: Intelligent workout plan generation based on exercise prerequisites and progression
- **Flexible Data Source**: Load exercise data from local JSON files or web URLs
- **Interactive UI**: Beautiful Streamlit interface with user-friendly questions
- **Personalization**: Customizable based on:
  - Fitness level (beginner, intermediate, advanced)
  - Training goals (strength, hypertrophy, endurance)
  - Available equipment
  - Training days per week
  - Training split (Full Body or A/B Split)
- **Visualization**: Interactive exercise progression graph showing prerequisites and relationships

## Project Structure

```
hakbaz2/
├── data/
│   └── exercises.json          # Exercise database (separated from code)
├── src/
│   ├── bfs_algorithm.py        # Core BFS algorithm logic
│   ├── data_handler.py         # Data loading from file/web
│   └── streamlit_app.py        # Streamlit web application
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running Locally

```bash
streamlit run src/streamlit_app.py
```

The app will open in your default web browser at `http://localhost:8501`

### Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file path: `src/streamlit_app.py`
7. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

### Using Web Data Source

1. Host your `exercises.json` file on a web server or use a GitHub raw URL
2. In the Streamlit app sidebar, enter the URL in the "Optional: Load from URL" field
3. The app will automatically load data from the URL

Example:
```
https://raw.githubusercontent.com/username/repo/main/data/exercises.json
```

## Data Format

The `exercises.json` file should follow this structure:

```json
{
  "exercises": {
    "Exercise Name": {
      "prerequisites": ["Prerequisite Exercise 1", "Prerequisite Exercise 2"],
      "level": "beginner|intermediate|advanced",
      "equipment": ["equipment1", "equipment2"],
      "muscle": "chest|back|legs|shoulders|triceps|core"
    }
  },
  "goal_set_rep": {
    "strength": {
      "beginner": "4x6-8",
      "intermediate": "5x4-6",
      "advanced": "6x3-5"
    }
  },
  "equipment_options": [
    {"id": "dumbbells", "name": "Dumbbells"}
  ]
}
```

## How It Works

1. **Data Loading**: Exercises are loaded from a JSON file (local or web)
2. **User Input**: Users answer questions about their fitness profile and preferences
3. **BFS Algorithm**: The algorithm creates a workout plan by:
   - Filtering exercises based on user level and equipment
   - Grouping exercises by muscle groups
   - Using BFS-style queue to distribute exercises across training days
   - Ensuring variety and progression in the plan
4. **Visualization**: A graph shows exercise prerequisites and progression paths

## Contributing

Feel free to expand the exercise database or improve the algorithm!

## License

This project is open source and available for educational purposes.

