from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class Task(db.Model):
    """
    Task model for storing productivity tasks
    
    Attributes:
        id: Primary key
        title: Task description
        category: Category (Work, Health, Personal, etc.)
        is_completed: Completion status
        date_created: Timestamp when task was created
        recurrence_type: Type of recurrence (daily, weekly, monthly, yearly, none)
        recurrence_value: Number of days/weeks/months/years
        last_reset: Last time the task was reset
    """
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Personal')
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # New recurrence fields
    recurrence_type = db.Column(db.String(20), default='daily', nullable=False)  # daily, weekly, monthly, yearly, none
    recurrence_value = db.Column(db.Integer, default=1, nullable=False)  # e.g., 7 for "every 7 days"
    last_reset = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title} ({self.category}) - {self.recurrence_type}>'
    
    def to_dict(self):
        """Convert task object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'is_completed': self.is_completed,
            'date_created': self.date_created.isoformat(),
            'recurrence_type': self.recurrence_type,
            'recurrence_value': self.recurrence_value,
            'last_reset': self.last_reset.isoformat()
        }