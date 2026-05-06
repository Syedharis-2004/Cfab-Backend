import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel

# Mocking the models for logic testing
class MockLecture:
    def __init__(self, id, duration, order_index):
        self.id = id
        self.duration = duration
        self.order_index = order_index

def generate_study_plan_logic(lectures, daily_minutes, weekly_schedule=None, start_date=None):
    plan_dict = {}
    day_counter = 1
    current_day_lectures = []
    current_day_minutes = 0
    
    weekly_schedule = weekly_schedule or {} 
    weekly_schedule = {k.lower(): v for k, v in weekly_schedule.items()}
    
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    start_date = start_date or datetime.utcnow()
    current_date = start_date
    
    lecture_idx = 0
    while lecture_idx < len(lectures):
        day_name = days_of_week[current_date.weekday()]
        available_today = weekly_schedule.get(day_name, daily_minutes)
        
        if available_today > 0:
            while lecture_idx < len(lectures):
                lecture = lectures[lecture_idx]
                
                if not current_day_lectures:
                    current_day_lectures.append(lecture.id)
                    current_day_minutes = lecture.duration
                    lecture_idx += 1
                    if current_day_minutes >= available_today:
                        break
                else:
                    if current_day_minutes + lecture.duration <= available_today:
                        current_day_lectures.append(lecture.id)
                        current_day_minutes += lecture.duration
                        lecture_idx += 1
                    else:
                        break
            
            plan_dict[f"day{day_counter}"] = {
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "lectures": current_day_lectures,
                "minutes": current_day_minutes
            }
            day_counter += 1
            current_day_lectures = []
            current_day_minutes = 0
            current_date += timedelta(days=1)
        else:
            print(f"Skipping {day_name} ({current_date.strftime('%Y-%m-%d')}) - 0 mins available")
            current_date += timedelta(days=1)
            
    return plan_dict, current_date

# Test Cases
lectures = [
    MockLecture("L1", 10, 1),
    MockLecture("L2", 20, 2),
    MockLecture("L3", 15, 3),
    MockLecture("L4", 25, 4),
    MockLecture("L5", 10, 5),
    MockLecture("L6", 30, 6),
    MockLecture("L7", 20, 7),
]

print("--- Test 1: Fixed 30 mins daily ---")
plan, end_date = generate_study_plan_logic(lectures, 30)
for day, info in plan.items():
    print(f"{day} ({info['date']} {info['day_name']}): {info['lectures']} - {info['minutes']} mins")

print("\n--- Test 2: Availability (Mon, Wed, Fri - 60 mins each) ---")
schedule = {"monday": 60, "tuesday": 0, "wednesday": 60, "thursday": 0, "friday": 60, "saturday": 0, "sunday": 0}
# Start on a Tuesday (weekday 1)
start = datetime(2026, 5, 5) # Tuesday
plan, end_date = generate_study_plan_logic(lectures, 30, weekly_schedule=schedule, start_date=start)
for day, info in plan.items():
    print(f"{day} ({info['date']} {info['day_name']}): {info['lectures']} - {info['minutes']} mins")
print(f"Completion Date: {end_date.strftime('%Y-%m-%d')}")
