from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import json
import os

app = Flask(__name__)
DATABASE = 'instance/tasks.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Delete old database if it exists
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
            print(f"Deleted old database: {DATABASE}")
        except Exception as e:
            print(f"Could not delete database: {e}")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            duration INTEGER DEFAULT 30,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            day_index INTEGER NOT NULL,
            status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            UNIQUE(task_id, day_index)
        )
    ''')
    
    # Initialize default settings
    cursor.execute('SELECT COUNT(*) as count FROM settings')
    if cursor.fetchone()['count'] == 0:
        cursor.execute('INSERT INTO settings (duration) VALUES (30)')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Fetch duration setting"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT duration FROM settings ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    
    duration = row['duration'] if row else 30
    return jsonify({'duration': duration})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update duration setting"""
    data = request.json
    duration = data.get('duration', 30)
    
    if duration < 7 or duration > 365:
        return jsonify({'error': 'Duration must be between 7 and 365 days'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE settings SET duration = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1', (duration,))
    conn.commit()
    conn.close()
    
    return jsonify({'duration': duration}), 200

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Fetch all tasks"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    data = request.json
    task_id = str(int(datetime.now().timestamp() * 1000))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (id, name, color) VALUES (?, ?, ?)',
        (task_id, data.get('name'), data.get('color'))
    )
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': task_id,
        'name': data.get('name'),
        'color': data.get('color'),
        'created_at': datetime.now().isoformat()
    }), 201

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    cursor.execute('DELETE FROM completions WHERE task_id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'deleted'}), 200

@app.route('/api/completions', methods=['GET'])
def get_completions():
    """Fetch all completions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT task_id, day_index, status FROM completions')
    rows = cursor.fetchall()
    conn.close()
    
    completions = {}
    for row in rows:
        key = f"{row['task_id']}-{row['day_index']}"
        completions[key] = bool(row['status'])
    
    return jsonify(completions)

@app.route('/api/completions/<task_id>/<int:day_index>', methods=['POST'])
def toggle_completion(task_id, day_index):
    """Toggle completion status for a task on a specific day"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if completion exists
    cursor.execute(
        'SELECT status FROM completions WHERE task_id = ? AND day_index = ?',
        (task_id, day_index)
    )
    row = cursor.fetchone()
    
    if row:
        new_status = 1 if row['status'] == 0 else 0
        cursor.execute(
            'UPDATE completions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ? AND day_index = ?',
            (new_status, task_id, day_index)
        )
    else:
        cursor.execute(
            'INSERT INTO completions (task_id, day_index, status) VALUES (?, ?, ?)',
            (task_id, day_index, 1)
        )
    
    conn.commit()
    
    # Get updated status
    cursor.execute(
        'SELECT status FROM completions WHERE task_id = ? AND day_index = ?',
        (task_id, day_index)
    )
    result = cursor.fetchone()
    conn.close()
    
    key = f"{task_id}-{day_index}"
    status = bool(result['status']) if result else False
    
    return jsonify({'key': key, 'status': status}), 200

@app.route('/api/stats/<task_id>', methods=['GET'])
def get_stats(task_id):
    """Get completion stats for a task"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get duration
    cursor.execute('SELECT duration FROM settings ORDER BY id DESC LIMIT 1')
    duration_row = cursor.fetchone()
    duration = duration_row['duration'] if duration_row else 30
    
    # Get completed count
    cursor.execute(
        'SELECT COUNT(*) as completed FROM completions WHERE task_id = ? AND status = 1',
        (task_id,)
    )
    completed = cursor.fetchone()['completed']
    conn.close()
    
    percentage = (completed / duration * 100) if duration > 0 else 0
    
    return jsonify({
        'completed': completed,
        'total': duration,
        'percentage': int(percentage)
    })

@app.route('/api/progress-data/<task_id>', methods=['GET'])
def get_progress_data(task_id):
    """Get daily progress data for bar graph"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get duration
    cursor.execute('SELECT duration FROM settings ORDER BY id DESC LIMIT 1')
    duration_row = cursor.fetchone()
    duration = duration_row['duration'] if duration_row else 30
    
    days = []
    completions_count = []
    
    for i in range(duration):
        cursor.execute(
            'SELECT status FROM completions WHERE task_id = ? AND day_index = ?',
            (task_id, i)
        )
        row = cursor.fetchone()
        completions_count.append(1 if row and row['status'] else 0)
        
        date = datetime.now() - timedelta(days=(duration - 1 - i))
        days.append(date.strftime('%m/%d'))
    
    conn.close()
    
    return jsonify({
        'days': days,
        'completions': completions_count
    })

@app.route('/api/overall-progress', methods=['GET'])
def get_overall_progress():
    """Get overall progress data for line graph"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get duration
    cursor.execute('SELECT duration FROM settings ORDER BY id DESC LIMIT 1')
    duration_row = cursor.fetchone()
    duration = duration_row['duration'] if duration_row else 30
    
    # Get all tasks
    cursor.execute('SELECT id FROM tasks')
    tasks = [row['id'] for row in cursor.fetchall()]
    
    days = []
    daily_completion_rates = []
    
    if not tasks:
        conn.close()
        return jsonify({'days': [], 'rates': []})
    
    for i in range(duration):
        total_completions = 0
        total_tasks = len(tasks)
        
        for task_id in tasks:
            cursor.execute(
                'SELECT status FROM completions WHERE task_id = ? AND day_index = ? AND status = 1',
                (task_id, i)
            )
            if cursor.fetchone():
                total_completions += 1
        
        completion_rate = (total_completions / total_tasks * 100) if total_tasks > 0 else 0
        daily_completion_rates.append(round(completion_rate, 1))
        
        date = datetime.now() - timedelta(days=(duration - 1 - i))
        days.append(date.strftime('%m/%d'))
    
    conn.close()
    
    return jsonify({
        'days': days,
        'rates': daily_completion_rates
    })

if __name__ == '__main__':
    app.run(debug=True)
