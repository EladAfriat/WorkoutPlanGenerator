# Workout Plan Generator 💪

A smart, personalized workout plan generator using BFS (Breadth-First Search) algorithm, built with Streamlit for an interactive web interface. Features user authentication, exercise details, video tutorials, and PDF export.

## ✨ Features

### Core Functionality
- **🧠 BFS Algorithm**: Intelligent workout plan generation based on exercise prerequisites, muscle groups, and user preferences
- **📊 Personalized Plans**: Custom workout plans tailored to your fitness profile
- **🎯 Multiple Goals**: Support for strength, hypertrophy, endurance, weight loss, power, flexibility, and general fitness
- **📅 Flexible Scheduling**: Choose your training days per week (1-7 days)
- **💪 Training Splits**: Full Body (FB) or A/B Split (AB) options

### User Experience
- **🔐 User Authentication**: Sign up, login, and user accounts with Supabase integration
- **👤 User Profiles**: Save workout preferences and history per user
- **📝 Exercise Details**: Detailed instructions, pro tips, and common mistakes for each exercise
- **🎥 Video Tutorials**: YouTube video links for every exercise
- **📄 PDF Export**: Export your workout plan as a PDF document
- **📈 Exercise Graph**: Visualize exercise progression and prerequisites
- **🔄 Alternative Exercises**: Get exercise alternatives based on equipment and level

### Data & Customization
- **📂 Flexible Data Source**: Load exercise data from local JSON files or web URLs
- **🏋️ Equipment Options**: Support for various equipment (dumbbells, barbells, resistance bands, etc.)
- **📊 Level-Based Filtering**: Exercises filtered by fitness level (beginner, intermediate, advanced)
- **🎨 Dark Theme**: Modern, user-friendly dark theme interface

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/workout-plan-generator.git
   cd workout-plan-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional, for full features)
   
   Create a `.env` file in the project root:
   ```env
   # Supabase Configuration (for user accounts)
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-key-here
   
   # SendGrid Configuration (optional, for email verification)
   SENDGRID_API_KEY=your-sendgrid-api-key
   SENDGRID_FROM_EMAIL=your-verified-email@example.com
   
   # App Configuration
   APP_URL=http://localhost:8501
   ```

### Running Locally

```bash
streamlit run src/streamlit_app.py
```

Or use the batch file (Windows):
```bash
run_app.bat
```

The app will open in your default web browser at `http://localhost:8501`

## 📦 Project Structure

```
hakbaz2/
├── data/
│   └── exercises.json          # Exercise database with instructions, tips, videos
├── src/
│   ├── streamlit_app.py        # Main Streamlit web application
│   ├── bfs_algorithm.py         # Core BFS algorithm for workout generation
│   ├── data_handler.py         # Data loading from file/web
│   ├── auth.py                  # User authentication (signup, login, verification)
│   └── user_data.py             # User preferences and workout history storage
├── scripts/
│   └── add_missing_exercise_info.py  # Utility script for updating exercise data
├── database_schema.sql          # Supabase database schema
├── requirements.txt             # Python dependencies
├── run_app.bat                 # Windows batch file to run the app
└── README.md                   # This file
```

## 🌐 Deployment

### Deploying to Streamlit Cloud

1. **Push your code to GitHub**

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Sign in with GitHub**

4. **Click "New app"**

5. **Configure your app:**
   - Select your repository and branch
   - Set main file path: `src/streamlit_app.py`
   - Click "Deploy"

6. **Add Secrets** (for user accounts):
   - Go to your app → "Manage app" → "Settings" → "Secrets"
   - Add your Supabase credentials:
     ```toml
     SUPABASE_URL = "https://your-project-id.supabase.co"
     SUPABASE_KEY = "your-publishable-key-here"
     APP_URL = "https://your-app-name.streamlit.app"
     ```

7. **Set up Supabase Database:**
   - Create a Supabase project at https://supabase.com
   - Run the SQL from `database_schema.sql` in Supabase SQL Editor
   - Copy your Project URL and API key to Streamlit Cloud secrets

Your app will be live at: `https://your-app-name.streamlit.app`

## 📚 How It Works

### 1. User Input
Users provide:
- Fitness level (beginner, intermediate, advanced)
- Training goal (strength, hypertrophy, endurance, etc.)
- Available equipment
- Training days per week
- Training split (Full Body or A/B Split)

### 2. BFS Algorithm
The algorithm:
- Filters exercises based on user level and equipment
- Groups exercises by muscle groups
- Uses quota-based round-robin system to distribute exercises
- Ensures balanced muscle group coverage across days
- Provides variety and progression in the plan

### 3. Workout Plan Generation
- Each day gets exercises targeting specific muscle groups
- Exercises are rotated to ensure variety
- Sets and reps are determined by goal and level
- Alternative exercises are available for each exercise

### 4. Additional Features
- **Exercise Details**: Click the ℹ️ button to see instructions, tips, and common mistakes
- **Video Tutorials**: Click the 🎥 button to watch YouTube tutorials
- **PDF Export**: Download your workout plan as a PDF
- **Exercise Graph**: Visualize exercise prerequisites and progression

## 🔧 Configuration

### Using Web Data Source

1. Host your `exercises.json` file on a web server or use a GitHub raw URL
2. In the Streamlit app sidebar, enter the URL in "Optional: Load from URL"
3. The app will automatically load data from the URL

Example:
```
https://raw.githubusercontent.com/username/repo/main/data/exercises.json
```

### Data Format

The `exercises.json` file should follow this structure:

```json
{
  "exercises": {
    "Exercise Name": {
      "prerequisites": ["Prerequisite Exercise 1"],
      "level": "beginner|intermediate|advanced",
      "equipment": ["dumbbells", "barbell"],
      "muscle": "chest|back|legs|shoulders|triceps|biceps|core",
      "instructions": ["Step 1", "Step 2"],
      "tips": ["Tip 1", "Tip 2"],
      "common_mistakes": ["Mistake 1"],
      "video": "https://youtube.com/watch?v=..."
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

## 🔐 Authentication

The app supports user authentication with:
- **Sign Up**: Create an account with email and password
- **Login**: Sign in to access your saved preferences
- **Email Verification**: Optional email verification (requires SendGrid)
- **Auto-Verification**: If email service is not configured, users are auto-verified
- **User Data**: Workout preferences and history are saved per user

### Without Email Service
- Users are automatically verified upon signup
- All features work immediately
- Users can log in right away

### With Email Service (SendGrid)
- Users receive verification emails
- Must verify email before logging in
- More secure authentication flow

## 📋 Requirements

- Python 3.8+
- Streamlit
- NetworkX (for graph visualization)
- Matplotlib (for plotting)
- ReportLab (for PDF export)
- Supabase (for user accounts - optional)
- SendGrid (for email verification - optional)

See `requirements.txt` for complete list.

## 🛠️ Development

### Running Tests
```bash
# Run the app locally
streamlit run src/streamlit_app.py
```

### Updating Exercise Data
Use the utility script in `scripts/add_missing_exercise_info.py` to add exercise information.

### Database Setup
1. Create a Supabase project
2. Run `database_schema.sql` in Supabase SQL Editor
3. Configure secrets in Streamlit Cloud

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to:
- Expand the exercise database
- Improve the BFS algorithm
- Add new features
- Report bugs or suggest improvements

## 📞 Support

For issues or questions:
- Check the code comments for implementation details
- Review the database schema in `database_schema.sql`
- Check Supabase and Streamlit Cloud documentation

---

**Built with ❤️ using Streamlit, Supabase, and Python**
