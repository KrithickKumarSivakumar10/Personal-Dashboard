# 📊 Daily Habits Tracker

A beautiful, modern web application to track your daily habits and build consistent routines. Set custom date ranges for each habit and monitor your progress with visual charts and statistics.

## ✨ Features

- **📅 Custom Date Ranges**: Create habits with specific start and end dates
- **📈 Progress Tracking**: Visual statistics showing completion percentage with 2 decimal precision
- **📊 Multiple Charts**: Bar chart and pie chart visualizations of your progress
- **✅ Daily Checkboxes**: Mark each day as complete/incomplete
- **🎨 Color Coded**: Assign custom colors to each habit for easy identification
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **💾 Persistent Storage**: All data saved in SQLite database
- **⚡ Real-time Updates**: See changes instantly as you mark days complete

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradient backgrounds
- **JavaScript (Vanilla)** - No framework dependencies
- **Chart.js** - Beautiful data visualizations

### Backend
- **Flask** - Lightweight Python web framework
- **SQLite** - Local database for data persistence
- **Python 3** - Backend logic

## 📦 Installation

### Prerequisites
- Python 3.7+
- Flask (`pip install flask`)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd daily-habits-tracker
```

2. **Install dependencies**
```bash
pip install flask
```

3. **Create the folder structure**
```
daily-habits-tracker/
├── app.py
├── templates/
│   └── index.html
└── instance/
    └── (database created automatically)
```

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
Navigate to `http://127.0.0.1:5000`

## 🎯 How to Use

### Adding a Habit

1. Enter the habit name in the "Add New Task" section
2. Click on a color to assign to your habit
3. Click "Add Task"
4. Select your start date and end date
5. Click "Add Task" to confirm

### Tracking Progress

1. Click the checkbox (○) to mark a day as complete
2. The checkbox will turn into a checkmark (✓) with your habit's color
3. Your progress percentage updates instantly
4. Future dates are disabled to prevent marking incomplete days

### Viewing Statistics

- **Stat Cards**: Shows completion percentage for each habit with 2 decimal places
- **Bar Chart**: Horizontal bar chart showing all habits' progress
- **Pie Chart**: Circular chart showing proportional completion rates

### Deleting a Habit

1. Click the 🗑️ trash icon at the end of the habit row
2. Confirm the deletion in the modal
3. The habit and all its completion data will be removed

## 🗄️ Database Schema

### Tables

**tasks**
- `id` (TEXT PRIMARY KEY) - Unique task identifier
- `name` (TEXT) - Task name
- `color` (TEXT) - Hex color code
- `created_at` (TIMESTAMP) - Creation timestamp

**completions**
- `id` (INTEGER PRIMARY KEY) - Auto-increment ID
- `task_id` (TEXT FOREIGN KEY) - References tasks table
- `day_index` (INTEGER) - Day number (0 = start date)
- `status` (INTEGER) - 0 = incomplete, 1 = complete
- `created_at` (TIMESTAMP) - Creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

**task_durations**
- `task_id` (TEXT PRIMARY KEY) - References tasks table
- `duration` (INTEGER) - Total days in habit
- `start_date` (TEXT) - Habit start date (YYYY-MM-DD)
- `end_date` (TEXT) - Habit end date (YYYY-MM-DD)
- `created_at` (TIMESTAMP) - Creation timestamp

**settings**
- `id` (INTEGER PRIMARY KEY) - Settings ID
- `duration` (INTEGER) - Default duration (currently unused)
- `created_at` (TIMESTAMP) - Creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

## 🔌 API Endpoints

### Tasks
- `GET /api/tasks` - Fetch all tasks
- `POST /api/tasks` - Create new task
- `DELETE /api/tasks/<task_id>` - Delete a task

### Completions
- `GET /api/completions` - Get all completion records
- `POST /api/completions/<task_id>/<day_index>` - Toggle day completion status

### Task Durations
- `GET /api/task-durations` - Get duration info for all tasks

### Statistics
- `GET /api/stats/<task_id>` - Get completion stats for a task
- `GET /api/progress-data/<task_id>` - Get daily progress data for a task
- `GET /api/overall-progress` - Get overall progress across all tasks

## 🐛 Bug Fixes Applied

### Issue: Percentages showing as 0%
**Root Cause**: Backend was using global default duration (30 days) instead of task-specific durations.

**Solution**: Updated all statistics endpoints to query the `task_durations` table:
- `get_stats()` - Now fetches task-specific duration
- `get_progress_data()` - Now fetches task-specific duration
- `get_overall_progress()` - Now uses max duration from all tasks

### Issue: Checkboxes not working
**Root Cause**: Date handling and timezone issues in frontend calculations.

**Solution**: 
- Added proper date string formatting with `'T00:00:00'`
- Added error handling with try-catch blocks
- Fixed date offset calculations for proper day indexing

### Issue: Multiple tasks with different date ranges misaligned
**Root Cause**: Table header was using only first task's dates.

**Solution**:
- Header now starts from earliest task date
- Each task's days are aligned to correct columns with offset calculation
- Days outside task range show "-" placeholder

## 📊 Percentage Calculation

Percentages are calculated with 2 decimal precision:
```
Percentage = (Completed Days / Total Days) × 100
Example: 1 completed out of 366 days = 0.27%
```

## 🎨 Color Palette

Available habit colors:
- `#FF6B6B` - Red
- `#4ECDC4` - Teal
- `#45B7D1` - Blue
- `#95E1D3` - Mint
- `#FFA07A` - Coral
- `#FFD93D` - Yellow
- `#6BCB77` - Green
- `#A78BFA` - Purple

## 📝 File Structure

```
daily-habits-tracker/
├── app.py                 # Flask backend
├── models.py              # Data models (optional)
├── templates/
│   └── index.html         # Frontend UI
├── instance/
│   └── tasks.db          # SQLite database (auto-created)
└── README.md             # This file
```

## 🚀 Deployment

### Development
```bash
python app.py
```
Flask runs on `http://127.0.0.1:5000` with debug mode enabled.

### Production
For production deployment, use a production WSGI server:
```bash
pip install gunicorn
gunicorn app:app
```

## 📱 Browser Support

- Chrome/Chromium (Latest)
- Firefox (Latest)
- Safari (Latest)
- Edge (Latest)

## ⚙️ Configuration

### Change Debug Mode
In `app.py`, modify:
```python
if __name__ == '__main__':
    app.run(debug=False)  # Set to False for production
```

### Change Database Location
In `app.py`, modify:
```python
DATABASE = 'instance/tasks.db'  # Change path here
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Krithick Kumar Sivakumar**

📧 [krithickkumarsivakumar@gmail.com](mailto:krithickkumarsivakumar@gmail.com)

---

**Last Updated**: January 23, 2026
**Version**: 1.0.0 (Fixed)
