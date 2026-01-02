from datetime import datetime, timedelta
from collections import Counter
from typing import List, Tuple, Dict

def calculate_daily_completion(goals: List[Tuple]) -> int:
    if not goals:
        return 0
    completed = sum(1 for g in goals if g[3] == 1) # Index 3 is 'completed'
    return int((completed / len(goals)) * 100)

def get_weekly_summary(all_goals: List[Tuple]) -> Dict[str, float]:
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    
    summary = {d: 0.0 for d in dates}
    
    for d in dates:
        day_goals = [g for g in all_goals if g[2] == d]
        if day_goals:
            completed = sum(1 for g in day_goals if g[3] == 1)
            summary[d] = (completed / len(day_goals)) * 100
        else:
            summary[d] = 0.0
            
    return summary

def calculate_streak(all_goals: List[Tuple]) -> int:
    """Standard Activity Streak: Days with at least 1 completed goal."""
    goals_by_date = {}
    for g in all_goals:
        d = g[2]
        if d not in goals_by_date: goals_by_date[d] = []
        goals_by_date[d].append(g)

    today = datetime.now().date()
    streak = 0
    check_date = today

    while True:
        d_str = check_date.isoformat()
        
        # If no goals found for this date
        if d_str not in goals_by_date:
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            else:
                break # Streak broken by empty day

        day_goals = goals_by_date[d_str]
        completed_cnt = sum(1 for g in day_goals if g[3] == 1)
        
        if completed_cnt > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today:
                check_date -= timedelta(days=1)
            else:
                break
                
    return streak

def calculate_perfect_streak(all_goals: List[Tuple]) -> int:
    """
    PERFECT STREAK: Consecutive days with 100% completion.
    Skips days where NO goals were added.
    """
    goals_by_date = {}
    for g in all_goals:
        d = g[2]
        if d not in goals_by_date: goals_by_date[d] = []
        goals_by_date[d].append(g)

    # Sort dates from newest to oldest
    sorted_dates = sorted(goals_by_date.keys(), reverse=True)
    
    if not sorted_dates:
        return 0

    streak = 0
    today_str = datetime.now().date().isoformat()

    for d_str in sorted_dates:
        day_goals = goals_by_date[d_str]
        total = len(day_goals)
        completed = sum(1 for g in day_goals if g[3] == 1)

        # Calculate percentage
        if total > 0:
            if completed == total:
                streak += 1
            else:
                # If it's today and not 100%, we ignore it (streak continues from yesterday)
                if d_str == today_str:
                    continue
                else:
                    # If it's a past day and not 100%, streak breaks.
                    break
    
    return streak

def get_most_missed(all_goals: List[Tuple]) -> str:
    missed = [g[1] for g in all_goals if g[3] == 0]
    if not missed:
        return "None"
    counts = Counter([m.lower() for m in missed])
    most_common = counts.most_common(1)
    return most_common[0][0].capitalize() if most_common else "None"