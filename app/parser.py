import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

def parse_cdr_line(line: str) -> Optional[Tuple[datetime, int, str, str, str]]:
    """Parse a CDR line similar to the original Node.js logic.

    Expected format: <date> <time> <duration> ... fields ...
    Example fields are space-separated. The function returns a tuple:
    (call_start_str, duration_seconds, calling_number, called_number, call_code)
    where call_start_str is 'YYYY-MM-DD HH:MM:SS' (local time).
    """
    s = line.strip()
    if not s:
        return None
    parts = re.split(r'\s+', s)
    if len(parts) < 6:
        return None
    # parts[0] = date in format like DDMMYY? Original code used .match(/.{1,2}/g) and "20" + parts[0][2]
    # We'll follow same transformation: assume parts[0] is 6 digits DDMMYY
    date_field = parts[0]
    time_field = parts[1]
    dur_field = parts[2]

    # if not (len(date_field) >=6 and len(time_field) >=6):
    #     return None
    if len(date_field) < 6:
        return None

    # Для времени — достаточно 4 (HHMM) или 6 (HHMMSS)
    if len(time_field) not in (4, 6):
        return None

    # split into two-digit groups (like original)
    d_chunks = [date_field[i:i+2] for i in range(0, len(date_field), 2)]
    # t_chunks = [time_field[i:i+2] for i in range(0, len(time_field), 2)]

    # handle time
    if len(time_field) == 4:  # HHMM
        t_chunks = [time_field[0:2], time_field[2:4], "00"]
    elif len(time_field) == 6:  # HHMMSS
        t_chunks = [time_field[0:2], time_field[2:4], time_field[4:6]]
    else:
        return None

    try:
        year = int('20' + d_chunks[2])
        month = int(d_chunks[1])
        day = int(d_chunks[0])
        hour = int(t_chunks[0])
        minute = int(t_chunks[1])
        second = int(t_chunks[2])
        # Build end datetime (naive)
        end_dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    except Exception:
        return None

    # duration parsing: original code took substring positions
    # It used substring(0,1)*3600 + substring(1,3)*60 + substring(3)
    # We'll tolerate variable length but follow the same if possible.
    try:
        # ensure numeric string
        dur_digits = ''.join(ch for ch in dur_field if ch.isdigit())
        # pad left to at least 4 for hhmmss logic
        if len(dur_digits) <= 3:
            # treat as seconds
            duration_seconds = int(dur_digits)
        else:
            # use slicing similar to original: first char = hours, next two = minutes, rest = seconds
            hours = int(dur_digits[0])
            minutes = int(dur_digits[1:3]) if len(dur_digits) >=3 else 0
            seconds = int(dur_digits[3:]) if len(dur_digits) >3 else 0
            duration_seconds = hours*3600 + minutes*60 + seconds
    except Exception:
        return None

    # compute start time as end_dt - duration + timezone correction similar to original
    # Original code used getTimezoneOffset adjustments; here we will assume server local time (naive).
    start_dt = end_dt - timedelta(seconds=duration_seconds)
    # start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    calling_number = parts[5]
    called_number = parts[3]
    call_code = parts[4]
    return start_dt, duration_seconds, calling_number, called_number, call_code
