from datetime import datetime, timedelta


def parse_duration(duration_str):
    duration_str = duration_str.replace("P", "").replace("T", "")
    components = ['D', 'H', 'M', 'S']
    time_params = {'D': 0, 'H': 0, 'M': 0, 'S': 0}
    for component in components:
        if component in duration_str:
            value, duration_str = duration_str.split(component)
            time_params[component] = int(value)
    total_duration = timedelta(
        days=time_params['D'],
        hours=time_params['H'],
        minutes=time_params['M'],
        seconds=time_params['S'],
    )
    return total_duration


def transform_data(row):
    total_duration = parse_duration(row['Duration'])
    # Convert duration object to standard string "HH:MM:SS" for Snowflake VARCHAR
    time_obj = (datetime.min + total_duration).time()
    row['Duration'] = time_obj.strftime("%H:%M:%S")
    row['Video_type'] = 'Short' if total_duration < timedelta(minutes=1) else 'Normal'
    return row






