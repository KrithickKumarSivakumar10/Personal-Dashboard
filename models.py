from datetime import datetime

class Task:
    """Task model"""
    def __init__(self, task_id, name, color):
        self.id = task_id
        self.name = name
        self.color = color
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat()
        }


class Completion:
    """Completion model"""
    def __init__(self, task_id, day_index, status):
        self.task_id = task_id
        self.day_index = day_index
        self.status = status
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'day_index': self.day_index,
            'status': self.status,
            'updated_at': self.updated_at.isoformat()
        }


class Statistics:
    """Statistics calculator"""
    @staticmethod
    def calculate_completion_rate(completions, task_id, total_days=30):
        """Calculate completion percentage for a task"""
        completed = sum(1 for k, v in completions.items() 
                       if k.startswith(f"{task_id}-") and v)
        return (completed / total_days * 100) if total_days > 0 else 0
    
    @staticmethod
    def get_task_stats(completions, task_id, total_days=30):
        """Get all stats for a task"""
        completed = sum(1 for k, v in completions.items() 
                       if k.startswith(f"{task_id}-") and v)
        return {
            'completed': completed,
            'total': total_days,
            'percentage': int((completed / total_days * 100)) if total_days > 0 else 0
        }
