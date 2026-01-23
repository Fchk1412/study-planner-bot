import sqlite3
from datetime import datetime

class ExamStore:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)
    def init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    prep INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.commit()

    def add_exam(self, user_id: int, name: str, date_str: str, prep: int = 0) -> int:
        name = name.strip()
        date_str = date_str.strip()
        
        # Validate date format and check if it's in the past
        try:
            exam_date = datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Please use DD-MM-YYYY (e.g., 30-01-2026)")
        
        today = datetime.now().date()
        if exam_date < today:
            raise ValueError(f"The date {date_str} has already passed. Please enter a future date.")

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO exams (user_id, name, date, prep) VALUES (?, ?, ?, ?)",
                (user_id, name, date_str, prep),
            )
            conn.commit()
            return cur.lastrowid
    def list_exams(self, user_id: int):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, date, prep FROM exams WHERE user_id = ? ORDER BY date ASC, id ASC",
                (user_id,),
            ).fetchall()

        exams = []
        for r in rows:
            exams.append(
                {"id": r[0], "name": r[1], "date": r[2], "prep": r[3]}
            )
        return exams

    def clear_exams(self, user_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM exams WHERE user_id = ?", (user_id,))
            conn.commit()
    def remove_exam(self, user_id: int, exam_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM exams WHERE id = ? AND user_id = ?", (exam_id, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
    
    def get_priority_queue(self, user_id: int):
        """Get exams sorted by priority (urgency + preparation level)"""
        exams = self.list_exams(user_id)
        today = datetime.now().date()
        
        exams_with_priority = []
        for exam in exams:
            try:
                exam_date = datetime.strptime(exam['date'], "%d-%m-%Y").date()
                days_until = (exam_date - today).days
                
                # Calculate priority score
                # Higher score = higher priority (more urgent)
                # Factors: low prep (100 - prep), less time (urgency multiplier)
                prep_gap = 100 - exam['prep']  # How much you still need to prepare
                
                # Urgency multiplier based on days remaining
                if days_until <= 0:
                    urgency = 10  # Overdue/today - maximum urgency
                elif days_until <= 3:
                    urgency = 5  # Very urgent (3 days or less)
                elif days_until <= 7:
                    urgency = 3  # Urgent (1 week)
                elif days_until <= 14:
                    urgency = 2  # Moderate (2 weeks)
                else:
                    urgency = 1  # Low urgency (more than 2 weeks)
                
                # Priority score: prep_gap * urgency
                # An exam with 0% prep and 3 days left gets 100 * 5 = 500
                # An exam with 80% prep and 3 days left gets 20 * 5 = 100
                priority_score = prep_gap * urgency
                
                exams_with_priority.append({
                    **exam,
                    'days_until': days_until,
                    'priority_score': priority_score,
                    'urgency_level': urgency
                })
            except ValueError:
                # Skip exams with invalid dates
                continue
        
        # Sort by priority score (descending) - highest priority first
        exams_with_priority.sort(key=lambda x: x['priority_score'], reverse=True)
        return exams_with_priority
