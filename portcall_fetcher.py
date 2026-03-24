"""
Portcall Fetcher - API query handler
This module handles fetching portcall data from your API
using the shared API connection functions.
"""

from datetime import datetime, timedelta, timezone
import sys
import os
import json
import urllib.parse
import urllib.request

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

OSLO_TZ = ZoneInfo('Europe/Oslo')
UTC_TZ = timezone.utc

# Add includes directory to path to import database module
includes_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dev/includes'))
sys.path.insert(0, includes_path)


def _to_oslo(dt):
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)

    return dt.astimezone(OSLO_TZ)


def _parse_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return _to_oslo(value)

    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None

        candidates = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%H:%M:%S',
            '%H:%M',
        ]
        for fmt in candidates:
            try:
                parsed = datetime.strptime(v, fmt)
                return _to_oslo(parsed)
            except ValueError:
                pass

        if v.endswith('Z'):
            try:
                parsed = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return _to_oslo(parsed)
            except Exception:
                pass

        try:
            parsed = datetime.fromisoformat(v)
            return _to_oslo(parsed)
        except Exception:
            pass

    return None


def _format_time(value):
    if value is None:
        return ''

    if isinstance(value, datetime):
        d = _to_oslo(value)
        return d.strftime('%H:%M') if d else ''

    if isinstance(value, str):
        parsed = _parse_datetime(value)
        if parsed:
            return parsed.strftime('%H:%M')
        try:
            t = datetime.strptime(value.strip(), '%H:%M:%S')
            t = _to_oslo(t)
            return t.strftime('%H:%M') if t else ''
        except Exception:
            try:
                t = datetime.strptime(value.strip(), '%H:%M')
                t = _to_oslo(t)
                return t.strftime('%H:%M') if t else ''
            except Exception:
                return ''

    if hasattr(value, 'hour') and hasattr(value, 'minute'):
        try:
            v = _to_oslo(value)
            return v.strftime('%H:%M')
        except Exception:
            return ''

    return ''


def _date_key(value, arrival_time_value=None):
    if value is None and arrival_time_value is not None:
        value = arrival_time_value

    if value is None:
        return ''

    if isinstance(value, str):
        parsed = _parse_datetime(value)
        if parsed:
            d = _to_oslo(parsed)
            return d.date().strftime('%Y-%m-%d') if d else ''
        return ''

    if isinstance(value, datetime):
        d = _to_oslo(value)
        return d.date().strftime('%Y-%m-%d') if d else ''

    if hasattr(value, 'isoformat'):
        try:
            d = _parse_datetime(value.isoformat())
            if d:
                return d.date().strftime('%Y-%m-%d')
        except Exception:
            pass

    return ''


def get_portcalls_for_week_api(start_date, end_date, year, month, api_base_url=None, api_resource=None, api_token=None):
    if not api_base_url:
        raise ValueError('api_base_url is required for API mode')

    date_from = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
    date_to = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)

    endpoint = api_base_url + api_resource
    query = urllib.parse.urlencode({'timeWindowStart': date_from, 'timeWindowEnd': date_to})
    url = endpoint + '?' + query
    
    headers = {'Accept': 'application/json','Accept-Version': '1.0'}
    if api_token:
        headers['Authorization'] = f'Bearer {api_token}'

    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8')
        api_data = json.loads(raw)

    if isinstance(api_data, dict):
        candidates = ['data', 'results', 'portcalls', 'items', 'cruises', 'payload']
        rows = None
        for c in candidates:
            if c in api_data and isinstance(api_data[c], list):
                rows = api_data[c]
                break
        if rows is None:
            if isinstance(api_data, list):
                rows = api_data
            else:
                raise ValueError('Unexpected API response format for portcalls')
    elif isinstance(api_data, list):
        rows = api_data
    else:
        raise ValueError('Unexpected API response type')

    portcalls_by_date = {}

    for row in rows:
        if not isinstance(row, dict):
            continue

        vessel_name = row.get('vessel', {}).get('name') or row.get('vessel_name') or row.get('vesselName') or row.get('fartøynavn') or row.get('name') or 'n/a'
        portcall_id = row.get('portCallId') or row.get('portcall_id') or row.get('id') or row.get('anløpid')
        pier = row.get('quayVisit', [{}])[0].get('quayUsage', {}).get('physicalObjectCode', 'N/A') or row.get('pier') or row.get('ressursid') or row.get('berth') or row.get('terminal') or ''

        arrival_raw = row.get('arrival_time') or row.get('arrivalTime') or row.get('ankomst') or row.get('arrival_date') or row.get('date')
        departure_raw = row.get('departure_time') or row.get('departureTime') or row.get('avgang')
        arrival_date_raw = row.get('arrival_date') or row.get('arrivalDate') or row.get('date') or arrival_raw

        passengers = row.get('passengers') or row.get('passenger_count') or row.get('antallpassasjerer') or row.get('totalPassengers')

        arrival_str = _format_time(arrival_raw)
        departure_str = _format_time(departure_raw)
        date_key = _date_key(arrival_date_raw, arrival_raw)

        if not date_key:
            continue

        portcall = {
            'vessel_name': vessel_name,
            'portcall_id': portcall_id,
            'pier': pier,
            'arrival_time': arrival_str,
            'departure_time': departure_str,
        }
        if passengers is not None:
            portcall['passengers'] = passengers

        portcalls_by_date.setdefault(date_key, []).append(portcall)

    return portcalls_by_date


def get_portcalls_for_week(start_date, end_date, year, month, *, api_base_url=None, api_resource=None, api_token=None):
    try:
        return get_portcalls_for_week_api(start_date, end_date, year, month,
                                         api_base_url=api_base_url,
                                         api_resource=api_resource,
                                         api_token=api_token)
    except Exception as e:
        print(f"API fetch failed ({str(e)})", file=sys.stderr)



# ============================================================================
# IMPLEMENTATION NOTES
# ============================================================================
#
# 1. API CONNECTION
#    This module uses your shared API functions to get token, endpoint configuration etc. (included in index.py)
#
# 2. API QUERY CUSTOMIZATION
#    Update the API query in get_portcalls_for_week() to match your:
#    - Endpoint URLs (or put these in a seperate config file)
#    - Query parameters
#    - Column names (vessel_name, portcall_id, pier, etc.)
#    - Date filtering logic
#
# 3. COLUMN MAPPING
#    Customize the mapping from your API response to the expected portcall fields:
#    1. vessel_name
#    2. portcall_id
#    3. pier
#    4. arrival_time (as TIME or DATETIME)
#    5. departure_time (as TIME or DATETIME)
#    6. passengers (optional)
#
#    Adjust as needed for your API's response structure. The code includes some common fallbacks for field names, but you may need to add more based on your specific API.
#
# 4. DATE FIELDS
#    arrival_time and departure_time is being converted to Europe/OSLO timezone and formatted as HH:MM for display. 
#    If your API provides separate date and time fields, you can combine them in the code to ensure correct timezone handling.
#
# 5. HANDLING MULTIPLE PORTCALLS
#    The code automatically groups multiple portcalls on the same date
#    They'll display as separate cards sorted by arrival time
#
# ============================================================================