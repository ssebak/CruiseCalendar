from local_functions import build_calendar_grid
from calendar_manager import CalendarManager
from datetime import datetime

cm = CalendarManager(2026, 1)
week = cm.get_week_for_month(0)

# prepare fake data
portcalls = {}
portcalls[week[0].strftime('%Y-%m-%d')] = [
    {'vessel_name': 'A', 'portcall_id': 1, 'pier': 'X', 'arrival_time': '10:00', 'departure_time': '12:00', 'passengers':50},
    {'vessel_name': 'B', 'portcall_id': 2, 'pier': 'Y', 'arrival_time': '14:00', 'departure_time': '16:00', 'passengers':20},
]
portcalls[week[1].strftime('%Y-%m-%d')] = [
    {'vessel_name': 'C', 'portcall_id': 3, 'pier': 'Z', 'arrival_time': '09:00', 'departure_time': '11:00'}
]

html = build_calendar_grid(week, portcalls)
print(html)
