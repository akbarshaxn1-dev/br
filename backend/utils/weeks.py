from datetime import datetime, timedelta, timezone
import calendar

def get_week_boundaries(date: datetime = None) -> tuple:
    """Get Monday and Sunday for the week containing the given date"""
    if date is None:
        date = datetime.now(timezone.utc)
    
    # Get the weekday (0=Monday, 6=Sunday)
    weekday = date.weekday()
    
    # Calculate Monday
    monday = date - timedelta(days=weekday)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate Sunday
    sunday = monday + timedelta(days=6)
    sunday = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return monday, sunday

def format_week_label(monday: datetime) -> str:
    """Format week label like 'Week 3-9 Feb 2024'"""
    sunday = monday + timedelta(days=6)
    
    # If same month
    if monday.month == sunday.month:
        return f"Неделя {monday.day}-{sunday.day} {get_month_name_ru(monday.month)} {monday.year}"
    else:
        return f"Неделя {monday.day} {get_month_name_ru(monday.month)} - {sunday.day} {get_month_name_ru(sunday.month)} {monday.year}"

def get_month_name_ru(month: int) -> str:
    """Get Russian month name"""
    months = [
        "Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
        "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"
    ]
    return months[month - 1]
