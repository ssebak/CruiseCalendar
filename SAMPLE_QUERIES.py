"""
SAMPLE SQL QUERIES FOR CRUISE CALENDAR

This file contains example SQL queries for Microsoft SQL Server.
Use these as templates for implementing get_portcalls_for_week() in portcall_fetcher.py

Adjust table names, column names, and filtering logic to match your actual schema.
"""

# ============================================================================
# BASIC QUERY - Simple portcall retrieval
# ============================================================================

BASIC_QUERY = """
SELECT 
    vessel_name,
    portcall_id,
    pier,
    arrival_time,
    departure_time
FROM portcalls
WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
ORDER BY arrival_time ASC
"""

# Usage in Python:
"""
cursor.execute(BASIC_QUERY, (start_date.date(), end_date.date()))
"""


# ============================================================================
# WITH FILTERED COLUMNS - Extract time from datetime fields
# ============================================================================

FILTERED_QUERY = """
SELECT 
    vessel_name,
    portcall_id,
    pier,
    CAST(arrival_time AS TIME) as arrival_time,
    CAST(departure_time AS TIME) as departure_time,
    CAST(arrival_time AS DATE) as arrival_date
FROM portcalls
WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
    AND status = 'SCHEDULED'
ORDER BY arrival_date ASC, arrival_time ASC
"""


# ============================================================================
# WITH VESSEL INFO JOIN - Include additional vessel details
# ============================================================================

WITH_VESSEL_INFO = """
SELECT 
    v.vessel_name,
    p.portcall_id,
    p.pier,
    CAST(p.arrival_time AS TIME) as arrival_time,
    CAST(p.departure_time AS TIME) as departure_time,
    CAST(p.arrival_time AS DATE) as arrival_date,
    v.vessel_imo,
    v.capacity,
    v.flag
FROM portcalls p
JOIN vessels v ON p.vessel_id = v.vessel_id
WHERE CAST(p.arrival_time AS DATE) BETWEEN ? AND ?
    AND p.status = 'SCHEDULED'
ORDER BY arrival_date ASC, arrival_time ASC
"""


# ============================================================================
# WITH YEAR/MONTH FILTERING - Additional filtering by selected month
# ============================================================================

WITH_MONTH_FILTER = """
SELECT 
    vessel_name,
    portcall_id,
    pier,
    CAST(arrival_time AS TIME) as arrival_time,
    CAST(departure_time AS TIME) as departure_time,
    CAST(arrival_time AS DATE) as arrival_date
FROM portcalls
WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
    AND YEAR(arrival_time) = ?
    AND MONTH(arrival_time) = ?
    AND status = 'SCHEDULED'
ORDER BY arrival_date ASC, arrival_time ASC
"""

# Usage in Python:
"""
cursor.execute(WITH_MONTH_FILTER, (
    start_date.date(), 
    end_date.date(),
    year,
    month
))
"""


# ============================================================================
# WITH PORT INFO - Join with port/location information
# ============================================================================

WITH_PORT_INFO = """
SELECT 
    v.vessel_name,
    p.portcall_id,
    p.pier,
    CAST(p.arrival_time AS TIME) as arrival_time,
    CAST(p.departure_time AS TIME) as departure_time,
    CAST(p.arrival_time AS DATE) as arrival_date,
    port.port_name,
    port.port_code
FROM portcalls p
JOIN vessels v ON p.vessel_id = v.vessel_id
JOIN ports port ON p.port_id = port.port_id
WHERE CAST(p.arrival_time AS DATE) BETWEEN ? AND ?
    AND p.status = 'SCHEDULED'
ORDER BY arrival_date ASC, arrival_time ASC
"""


# ============================================================================
# HANDLING MULTI-DAY STAYS - Portcalls spanning multiple days
# ============================================================================

MULTI_DAY_HANDLING = """
/* Option 1: Show only on arrival date */
SELECT 
    vessel_name,
    portcall_id,
    pier,
    CAST(arrival_time AS TIME) as arrival_time,
    CAST(departure_time AS TIME) as departure_time,
    CAST(arrival_time AS DATE) as arrival_date
FROM portcalls
WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
ORDER BY arrival_date ASC, arrival_time ASC

/* Option 2: Show on each day of stay (using generate series) */
WITH date_range AS (
    SELECT 
        vessel_name,
        portcall_id,
        pier,
        arrival_time,
        departure_time,
        CAST(arrival_time AS DATE) as start_date,
        CAST(departure_time AS DATE) as end_date
    FROM portcalls
    WHERE arrival_time <= ?
        AND departure_time >= ?
),
expanded_dates AS (
    SELECT 
        vessel_name,
        portcall_id,
        pier,
        CAST(arrival_time AS TIME) as arrival_time,
        CAST(departure_time AS TIME) as departure_time,
        DATE_FROM_PARTS(YEAR(start_date), MONTH(start_date), DAY(start_date)) 
            + offset.value as arrival_date
    FROM date_range
    CROSS APPLY (SELECT value FROM (
        SELECT 0 as value
        UNION ALL
        SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
        SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6
    ) offsets
    WHERE value <= DATEDIFF(DAY, start_date, end_date)
    ) offset
)
SELECT * FROM expanded_dates
ORDER BY arrival_date ASC, arrival_time ASC
"""


# ============================================================================
# HANDLING TIME ZONES - If storing times in UTC
# ============================================================================

WITH_TIMEZONE_CONVERSION = """
SELECT 
    vessel_name,
    portcall_id,
    pier,
    /* Convert UTC to local time (example: EST is -5 hours) */
    CAST(DATEADD(HOUR, -5, arrival_time) AS TIME) as arrival_time,
    CAST(DATEADD(HOUR, -5, departure_time) AS TIME) as departure_time,
    CAST(DATEADD(HOUR, -5, arrival_time) AS DATE) as arrival_date
FROM portcalls
WHERE CAST(DATEADD(HOUR, -5, arrival_time) AS DATE) BETWEEN ? AND ?
ORDER BY arrival_date ASC, arrival_time ASC
"""

# Timezones in SQL Server:
# EST/EDT: DATEADD(HOUR, -5, utc_time)
# CST/CDT: DATEADD(HOUR, -6, utc_time)
# MST/MDT: DATEADD(HOUR, -7, utc_time)
# PST/PDT: DATEADD(HOUR, -8, utc_time)
# Or use AT TIME ZONE in SQL Server 2016+


# ============================================================================
# DATABASE TABLE SCHEMA EXAMPLES
# ============================================================================

"""
Example table definitions that would work with these queries:

CREATE TABLE vessels (
    vessel_id INT PRIMARY KEY,
    vessel_name NVARCHAR(255) NOT NULL,
    vessel_imo INT,
    capacity INT,
    flag NVARCHAR(50)
);

CREATE TABLE ports (
    port_id INT PRIMARY KEY,
    port_name NVARCHAR(255) NOT NULL,
    port_code NVARCHAR(10)
);

CREATE TABLE portcalls (
    portcall_id INT PRIMARY KEY IDENTITY(1,1),
    vessel_id INT NOT NULL,
    port_id INT NOT NULL,
    pier NVARCHAR(50) NOT NULL,
    arrival_time DATETIME2 NOT NULL,
    departure_time DATETIME2 NOT NULL,
    status NVARCHAR(50) DEFAULT 'SCHEDULED',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (vessel_id) REFERENCES vessels(vessel_id),
    FOREIGN KEY (port_id) REFERENCES ports(port_id)
);

-- Recommended indexes for performance
CREATE INDEX idx_portcalls_arrival 
on portcalls(CAST(arrival_time AS DATE)) 
INCLUDE (vessel_id, pier, departure_time);

CREATE INDEX idx_portcalls_status 
on portcalls(status) 
INCLUDE (arrival_time, departure_time);
"""


# ============================================================================
# PYTHON IMPLEMENTATION EXAMPLE
# ============================================================================

"""
In portcall_fetcher.py, replace the placeholder query with:

def get_portcalls_for_week(start_date, end_date, year, month):
    portcalls_by_date = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use one of the query examples above
        query = '''
            SELECT 
                vessel_name,
                portcall_id,
                pier,
                CAST(arrival_time AS TIME) as arrival_time,
                CAST(departure_time AS TIME) as departure_time,
                CAST(arrival_time AS DATE) as arrival_date
            FROM portcalls
            WHERE CAST(arrival_time AS DATE) BETWEEN ? AND ?
            ORDER BY arrival_date, arrival_time
        '''
        
        cursor.execute(query, (start_date.date(), end_date.date()))
        rows = cursor.fetchall()
        
        for row in rows:
            vessel_name = row[0]
            portcall_id = row[1]
            pier = row[2]
            arrival_time = row[3]
            departure_time = row[4]
            arrival_date = row[5]
            
            arrival_str = arrival_time.strftime('%H:%M') if arrival_time else ''
            departure_str = departure_time.strftime('%H:%M') if departure_time else ''
            
            date_key = arrival_date.strftime('%Y-%m-%d')
            
            portcall = {
                'vessel_name': vessel_name,
                'portcall_id': portcall_id,
                'pier': pier,
                'arrival_time': arrival_str,
                'departure_time': departure_str,
            }
            
            if date_key not in portcalls_by_date:
                portcalls_by_date[date_key] = []
            portcalls_by_date[date_key].append(portcall)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}", file=__import__('sys').stderr)
    
    return portcalls_by_date
"""
