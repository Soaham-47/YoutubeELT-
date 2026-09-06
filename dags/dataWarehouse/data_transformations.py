import re
from datetime import timedelta


def parse_duration(duration_str):
    if not duration_str or duration_str == "P0D":
        return timedelta(0)

    # Robust regex matching ISO 8601 duration (e.g. PT1H2M30S, PT45S, P1DT2H)
    pattern = re.compile(
        r"P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?"
    )
    match = pattern.match(duration_str)
    if not match:
        return timedelta(0)

    parts = {k: int(v) for k, v in match.groupdict().items() if v and v.isdigit()}
    return timedelta(**parts)


def transform_data(row):
    raw_duration = row.get("Duration") or ""
    total_duration = parse_duration(raw_duration)

    # Format cleanly as HH:MM:SS without overflowing if duration >= 24 hours
    total_seconds = int(total_duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    row["Duration"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Videos under 60 seconds are Shorts
    row["Video_type"] = "Short" if total_seconds < 60 else "Normal"

    return row






