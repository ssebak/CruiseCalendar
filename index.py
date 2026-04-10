#!/usr/bin/env python3
"""
Single entry-point script for the cruise calendar.

This module can be called directly from Apache (as a CGI program) or
directly on the command line for quick debugging.  It pulls the query
parameters, fetches port‑call data and renders the HTML page.

The ``local_functions`` module contains the helpers that build the
various sections of the page; the CSS has been moved into
``style.css`` so that the layout and colours are no longer embedded
inline.

If you prefer to keep the old ``calendar.cgi`` around for backwards
compatibility you can simply replace its contents with:

    #!/usr/bin/env python3
    from index import main
    if __name__ == '__main__':
        main()

and make it executable in the cgi‑bin directory.
"""

import sys
import cgi

from calendar_manager import CalendarManager
from portcall_fetcher import get_portcalls_for_week
from local_functions import (
    get_query_params,
    build_page_header,
    build_navigation_controls,
    build_calendar_grid,
    build_page_footer,
)

# get the API token functions
sys.path.append('../../includes')
import krakentools_secrets
import krakentools_utils
from krakentools_endpoints import API_BASE_URL, API_PORTCALLS_CRUISES

def main():
    # ensure the output stream uses utf-8 on Windows so emojis and
    # diacritics are handled correctly
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # the CGI spec requires an explicit content-type header followed by
    # a blank line
    sys.stdout.write("Content-Type: text/html; charset=utf-8\n\n")

    year, month, week_offset = get_query_params()

    cal = CalendarManager(year, month)
    week_dates = cal.get_week_for_month(week_offset)

    #Get token to access the API
    valid_token = krakentools_utils.get_valid_bearer_token(krakentools_secrets.CLIENT_ID, krakentools_secrets.CLIENT_SECRET, krakentools_secrets.AUDIENCE, krakentools_secrets.TOKEN_URL, krakentools_secrets.GRANT_TYPE)

    # Fetch REAL portcall data from your API/database
    portcalls_by_date = get_portcalls_for_week(
        week_dates[0],
        week_dates[-1],
        year,
        month,
        source='api',
        api_base_url=API_BASE_URL,
        api_resource=API_PORTCALLS_CRUISES,
        api_token=valid_token
    )

    html = build_page_header(year, month)
    html += build_navigation_controls(year, month, week_offset, cal)
    html += build_calendar_grid(
        week_dates,
        portcalls_by_date,
        future_vessel_name_threshold_months=12,
        future_vessel_name_mask='TBA'
    )
    html += build_page_footer()

    sys.stdout.write(html)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pragma: no cover - simple error page
        sys.stdout.write("Content-Type: text/html; charset=utf-8\n\n")
        sys.stdout.write("<h1>Unexpected Error</h1>\n")
        sys.stdout.write(f"<pre>{exc}</pre>\n")


