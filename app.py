from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from models import db, Task
from sqlalchemy import func

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables before first request
with app.app_context():
    db.create_all()

def check_and_reset_tasks():
    """Check all tasks and reset those that need to be reset based on their recurrence"""
    now = datetime.now()
    tasks = Task.query.all()
    
    for task in tasks:
        if task.recurrence_type == 'none':
            continue
            
        # Calculate when the task should reset
        time_diff = now - task.last_reset
        should_reset = False
        
        if task.recurrence_type == 'daily':
            should_reset = time_diff.days >= task.recurrence_value
        elif task.recurrence_type == 'weekly':
            should_reset = time_diff.days >= (task.recurrence_value * 7)
        elif task.recurrence_type == 'monthly':
            # Approximate: 30 days per month
            should_reset = time_diff.days >= (task.recurrence_value * 30)
        elif task.recurrence_type == 'yearly':
            # Approximate: 365 days per year
            should_reset = time_diff.days >= (task.recurrence_value * 365)
        
        if should_reset:
            task.is_completed = False
            task.last_reset = now
    
    db.session.commit()

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all active tasks (check and reset recurring ones first)"""
    check_and_reset_tasks()
    
    # Get all tasks ordered by creation date
    tasks = Task.query.order_by(Task.date_created.desc()).all()
    
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task with recurrence options"""
    data = request.json
    
    new_task = Task(
        title=data['title'],
        category=data.get('category', 'Personal'),
        is_completed=False,
        date_created=datetime.now(),
        recurrence_type=data.get('recurrence_type', 'daily'),
        recurrence_value=data.get('recurrence_value', 1),
        last_reset=datetime.now()
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Toggle task completion status or update recurrence"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    if 'is_completed' in data:
        task.is_completed = data['is_completed']
    
    if 'recurrence_type' in data:
        task.recurrence_type = data['recurrence_type']
    
    if 'recurrence_value' in data:
        task.recurrence_value = data['recurrence_value']
    
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/api/stats/weekly', methods=['GET'])
def get_weekly_stats():
    """Get completion stats for the last 7 days"""
    stats = []
    
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        
        # Get all tasks that were active on this date
        total_tasks = Task.query.filter(
            Task.date_created <= datetime.combine(date, datetime.max.time())
        ).count()
        
        # Get completed tasks - this is an approximation
        # In a real app, you'd want to track completion history
        completed_tasks = Task.query.filter(
            Task.date_created <= datetime.combine(date, datetime.max.time()),
            Task.is_completed == True
        ).count()
        
        # Calculate percentage
        percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        stats.append({
            'date': date.strftime('%m/%d'),
            'percentage': round(percentage, 1),
            'total': total_tasks,
            'completed': completed_tasks
        })
    
    return jsonify(stats)

@app.route('/api/stats/categories', methods=['GET'])
def get_category_stats():
    """Get task breakdown by category"""
    # Query tasks grouped by category
    categories = db.session.query(
        Task.category,
        func.count(Task.id).label('count')
    ).group_by(Task.category).all()
    
    return jsonify([{
        'category': cat[0],
        'count': cat[1]
    } for cat in categories])

@app.route('/api/stats/recurrence', methods=['GET'])
def get_recurrence_stats():
    """Get task breakdown by recurrence type"""
    recurrence = db.session.query(
        Task.recurrence_type,
        func.count(Task.id).label('count')
    ).group_by(Task.recurrence_type).all()
    
    return jsonify([{
        'type': rec[0],
        'count': rec[1]
    } for rec in recurrence])

@app.route('/api/reset-day', methods=['POST'])
def reset_day():
    """Manually reset all daily tasks"""
    Task.query.filter(
        Task.recurrence_type == 'daily'
    ).update({'is_completed': False, 'last_reset': datetime.now()})
    
    db.session.commit()
    
    return jsonify({'message': 'Daily tasks reset successfully'})

@app.route('/api/check-resets', methods=['POST'])
def manual_check_resets():
    """Manually trigger the automatic reset check"""
    check_and_reset_tasks()
    return jsonify({'message': 'Tasks checked and reset as needed'})

if __name__ == '__main__':
    # Run the Flask development server
    # For production, use a WSGI server like Gunicorn
    app.run(debug=True, host='127.0.0.1', port=5000)