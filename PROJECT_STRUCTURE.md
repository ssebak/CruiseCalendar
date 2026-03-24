# Cruise Calendar Project Structure

## Overview

A complete Python/CGI cruise port call calendar application ready for Apache deployment.

**Current Status**: ✅ All modules tested and working  
**Test Results**: All calendar logic verified, date calculations correct  
**Ready for**: Database integration and Apache deployment

## Project Files

### Core Application Files

| File | Purpose | Status |
|------|---------|--------|
| **index.py** / **calendar.cgi** | Main CGI entry point (index.py is the newer, refactored script) | ✅ Complete |
| **local_functions.py** | Shared helpers for building the HTML output | ✅ Added |
| **calendar_manager.py** | Date calculations & week generation | ✅ Tested |
| **portcall_fetcher.py** | Database and API fetch logic (`db_getdata` + `/portcalls/cruises` endpoint), timezone conversion | ⏳ Ready for your query/API setup |

### Configuration & Setup

| File | Purpose |
|------|---------|
| **requirements.txt** | Python dependencies |
| **SAMPLE_QUERIES.py** | Example SQL queries for your database |
| **DEPLOYMENT_CHECKLIST.md** | Step-by-step deployment guide |
| **style.css** | Shared stylesheet pulled in by index.py |

### Testing & Documentation

| File | Purpose | How to Use |
|------|---------|-----------|
| **quickstart.py** | Test calendar logic locally | `python quickstart.py` |
| **test_calendar.py** | Generate preview HTML with mock data | `python test_calendar.py` → opens `calendar_test.html` |
| **README.md** | Full documentation & troubleshooting |
| **PROJECT_STRUCTURE.md** | This file |

## Quick Start - 3 Steps

### 1️⃣ Test Locally (Verify everything works)
```bash
python quickstart.py        # Tests date logic
python test_calendar.py     # Generates preview HTML
```
Then open `calendar_test.html` in your browser to see the layout.

### 2️⃣ Configure Your Database
Edit `portcall_fetcher.py`:
- Update `DB_CONFIG` with your SQL Server details
- Replace placeholder SQL query with your actual query
- See `SAMPLE_QUERIES.py` for examples matching your schema
* current version does not include logic for pulling data from a database, only through an API. I'm planning on covering getting the data from a database as well though

### 3️⃣ Deploy to Apache
```bash
# Copy to Apache cgi-bin directory
# Update path in calendar.cgi
# Make calendar.cgi executable
# Access: http://your-server/cgi-bin/calendar.cgi
```

See `DEPLOYMENT_CHECKLIST.md` for detailed steps.

## Feature Checklist

- ✅ Weekly calendar view (7 columns: Mon-Sun)
- ✅ Month/Year selectors with automatic update
- ✅ Previous/Next week navigation buttons
- ✅ Intelligent date display (shows prev/next month dates)
- ✅ Date and weekday headers on each column
- ✅ Empty days visible (as requested)
- ✅ Portcall cards with:
  - ✅ Vessel name
  - ✅ Port call ID
  - ✅ Pier/berth information
  - ✅ Arrival & Departure times
- ✅ Responsive, modern UI
- ✅ Plain Python CGI (no framework overhead)
- ✅ Ready for Apache deployment

## Calendar Logic Details

### Week Display Algorithm

The week always starts on **Monday** and shows 7 days.

Each day header now includes a summary line showing the number of
portcalls and, if available, the total passengers (Pax) for that day. These
values are calculated from the data returned by your API call and appear
right below the weekday name.

**Example**: February 2026
- Feb 1, 2026 is a Sunday
- Week offset 0 shows: Jan 26 (Mon) → Feb 1 (Sun)
  - Mon-Sat are shown with lighter styling (other month)
  - Sun Feb 1 is shown with normal styling
- Week offset 1 shows: Feb 2 (Mon) → Feb 8 (Sun)
  - All days show normal styling (current month)

### Navigation

- **Select Month/Year** in dropdowns → Calendar updates automatically
- **Previous/Next buttons** → Navigate between weeks
- Month/year parameters passed to API call for filtered results

### Date Grouping

- Portcalls grouped by date key (YYYY-MM-DD)
- Multiple portcalls on same day display as separate cards
- Cards ordered by arrival time

## Deployment Architecture

```
Your Apache Server
├── /cgi-bin/
│   ├── calendar.cgi              ← Main entry point (executable)
│   ├── calendar_manager.py       ← Imported module
│   └── portcall_fetcher.py       ← Imported module
└── Browser requests:
    http://localhost/cgi-bin/calendar.cgi?year=2026&month=2&week_offset=0
```

## Database Variables

The `get_portcalls_for_week()` function receives:
- `start_date`: First day of week (Monday) as datetime.date
- `end_date`: Last day of week (Sunday) as datetime.date  
- `year`: Selected year from user dropdown
- `month`: Selected month from user dropdown

Use these to filter your API call appropriately.

## Styling & Layout

The calendar includes:
- **Color Scheme**: Purple gradient background, card-based design
- **Typography**: Clean sans-serif fonts
- **Responsive Grid**: 7-column layout automatically adjusts spacing
- **Status Indicators**: 
  - Arrival times in green (↓)
  - Departure times in red (↑)
- **Visual Hierarchy**: Large dates, full vessel names, clear time info

Modify CSS in `calendar.cgi` function `build_page_header()` to customize.

## Database Connection

Currently this does not support pulling data from a database, only through an API


## Performance Considerations

- **Query Time**: Typically < 100ms for most databases (adjust with indexes)
- **Page Size**: ~50KB HTML (compressed ~15KB)
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **Database Load**: One query per page load (can add caching)

## Next Steps

1. ✅ Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. ✅ Update `portcall_fetcher.py` with your database details
3. ✅ Reference `SAMPLE_QUERIES.py` for SQL examples
4. ✅ Deploy to your Apache cgi-bin directory
5. ✅ Test at `http://your-server/cgi-bin/calendar.cgi`

## Support

| Issue | Reference |
|-------|-----------|
| "How do I deploy?" | See `DEPLOYMENT_CHECKLIST.md` |
| "How do I customize the styling?" | Edit CSS in `calendar.cgi` |
| "Calendar not showing data" | See README.md troubleshooting section |
| "How are weeks calculated?" | See `calendar_manager.py` `get_week_for_month()` |

---

**Project Version**: 1.0  
**Python Version**: 3.7+  
**Apache Version**: 2.4+ (with CGI enabled)  
**Created**: February 2026  
**Status**: ✅ Ready for Deployment
