import json
import streamlit as st
import datetime
import swisseph as swe
import pandas as pd
import datetime as dt

def load_json_file(file_path):
    """
    Load data from a JSON file with error handling.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed data from the JSON file if successful.
    
    Raises:
        FileNotFoundError: If the file is not found.
        JSONDecodeError: If there is an error decoding the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON in file: {file_path}")

def initialize_session():
    # Load sign data
    if 'signs' not in st.session_state:
        signs_data = load_json_file('data/signs.json')
        st.session_state.signs = {
            sign['id']: {
                'name': sign['name'], 
                'symbol': sign['symbol'], 
                'element': sign['element'], 
                'modality': sign['modality']
            } for sign in signs_data
        }

    # Load planet data
    if 'planets' not in st.session_state:
        planets_data = load_json_file('data/planets.json')
        st.session_state.planets = {
            planet['id']: {
                'name': planet['name'], 
                'symbol': planet['symbol'], 
                'type': planet['type']
            } for planet in planets_data
        }

    # Load aspect data
    if 'aspects' not in st.session_state:
        aspects_data = load_json_file('data/aspects.json')
        st.session_state.aspects = {
            aspect['id']: {
                'name': aspect['name'], 
                'symbol': aspect['symbol'], 
                'angle': aspect['angle'], 
                'orb': aspect['orb']
            } for aspect in aspects_data
        }
    
    # Initialize default date range in session_state
    if 'start_date' not in st.session_state:
        st.session_state.start_date = datetime.date.today()
    if 'end_date' not in st.session_state:
        st.session_state.end_date = datetime.date.today() + datetime.timedelta(days=365)

    # Initialize other session_state variables
    if 'first_name' not in st.session_state:
        st.session_state.first_name = None
    if 'last_name' not in st.session_state:
        st.session_state.last_name = None
    if 'bday_date' not in st.session_state:
        st.session_state.bday_date = None
    if 'bday_hour' not in st.session_state:
        st.session_state.bday_hour = None
    if 'bday_minute' not in st.session_state:
        st.session_state.bday_minute = None
    if 'bday_latitude_deg' not in st.session_state:
        st.session_state.bday_latitude_deg = None
    if 'bday_latitude_min' not in st.session_state:
        st.session_state.bday_latitude_min = None
    if 'bday_latitude_direction' not in st.session_state:
        st.session_state.bday_latitude_direction = None
    if 'bday_longitude_deg' not in st.session_state:
        st.session_state.bday_longitude_deg = None
    if 'bday_longitude_min' not in st.session_state:
        st.session_state.bday_longitude_min = None
    if 'bday_longitude_direction' not in st.session_state:
        st.session_state.bday_longitude_direction = None   

def birth_data():
    # Input columns for first and last names
    first_name_col, last_name_col = st.columns(2)
    st.session_state.first_name = first_name_col.text_input(label='First Name', value=st.session_state.first_name)
    st.session_state.last_name = last_name_col.text_input(label='Last Name', value=st.session_state.last_name)

    # Date, hour, and minute inputs
    min_date, max_date = dt.date(1000, 1, 1), dt.date(3000, 12, 31)
    date_col, hour_col, minute_col = st.columns([2, 1, 1])
    st.session_state.bday_date = date_col.date_input('Birthday', value=st.session_state.bday_date, min_value=min_date, max_value=max_date, format='DD/MM/YYYY')
    st.session_state.bday_hour = hour_col.number_input(label='Hour (UTC)', min_value=0, max_value=23, value=st.session_state.bday_hour, step=1)
    st.session_state.bday_minute = minute_col.number_input(label='Minute', min_value=0, max_value=59, value=st.session_state.bday_minute, step=1)

    # Latitude and Longitude inputs with direction selection
    st.subheader('Birth Location Coordinates')
    lat_deg_col, lat_min_col, lat_dir_col = st.columns(3)
    st.session_state.bday_latitude_deg = lat_deg_col.number_input(label='Latitude Degrees', min_value=0, max_value=90, value=st.session_state.bday_latitude_deg, step=1)
    st.session_state.bday_latitude_min = lat_min_col.number_input(label='Latitude Minutes', min_value=0, max_value=59, value=st.session_state.bday_latitude_min, step=1)
    st.session_state.bday_latitude_direction = lat_dir_col.selectbox(label='Direction', options=('N', 'S'), index=None if st.session_state.bday_latitude_direction is None else ['N', 'S'].index(st.session_state.bday_latitude_direction))

    lon_deg_col, lon_min_col, lon_dir_col = st.columns(3)
    st.session_state.bday_longitude_deg = lon_deg_col.number_input(label='Longitude Degrees', min_value=0, max_value=180, value=st.session_state.bday_longitude_deg, step=1)
    st.session_state.bday_longitude_min = lon_min_col.number_input(label='Longitude Minutes', min_value=0, max_value=59, value=st.session_state.bday_longitude_min, step=1)
    st.session_state.bday_longitude_direction = lon_dir_col.selectbox(label='Direction', options=['E', 'W'], index=None if st.session_state.bday_longitude_direction is None else ['E', 'W'].index(st.session_state.bday_longitude_direction))

def start_end_date():
    """
    Allow user to input start and end dates using Streamlit widgets.
    
    This function creates two columns for date input: start date and end date. 
    It updates the session state with the selected dates.
    """
    start_date_col, end_date_col = st.columns(2)
    start_date_col.subheader('Start Date')
    st.session_state.start_date = start_date_col.date_input(
        label='Start', 
        value=st.session_state.start_date, 
        format="DD/MM/YYYY",
        label_visibility='collapsed'
    )
    end_date_col.subheader('End Date')
    st.session_state.end_date = end_date_col.date_input(
        label='End Date', 
        value=st.session_state.end_date, 
        format="DD/MM/YYYY",
        label_visibility='collapsed'
    )

def calculate_sign(longitude):
    """
    Calculate the zodiac sign for a given planetary longitude.

    Args:
        longitude (float): Longitude of the planet in degrees.

    Returns:
        int: The zodiac sign corresponding to the longitude (0-11).
    """
    return int(longitude // 30)

def datetime_to_julday(date):
    """
    Convert a datetime object to a Julian day.

    Args:
        date (datetime): A Python datetime object.

    Returns:
        float: The Julian day corresponding to the given date.
    """
    year = date.year
    month = date.month
    day = date.day
    hour = getattr(date, 'hour', 0)
    minute = getattr(date, 'minute', 0)
    second = getattr(date, 'second', 0)
    microsecond = getattr(date, 'microsecond', 0)
    
    hour_float = hour + minute / 60 + second / 3600 + microsecond / 3600000
    return swe.julday(year, month, day, hour_float)

def julday_to_datetime(julday: float) -> datetime:
    """
    Convert a Julian day to a datetime object.

    Args:
        julday (float): Julian day to be converted.

    Returns:
        datetime: A Python datetime object representing the given Julian day.
    """
    year, month, day, hour = swe.revjul(julday)
    
    # Extract hours, minutes, and seconds from the fractional part of the day
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int((((hour - hours) * 60) - minutes) * 60)
    
    # Create the datetime object
    return datetime.datetime(year, month, day, hours, minutes, seconds)

def calculate_planet_positions(julday_start, julday_end, julday_step):
    """
    Calculate planetary positions over a specified date range.

    Args:
        julday_start (float): The starting Julian day.
        julday_end (float): The ending Julian day.
        julday_step (float): The increment in Julian days for each calculation step.

    Returns:
        pd.DataFrame: A DataFrame containing the calculated planetary positions.
    """
    data = []
    julday = julday_start
    while julday <= julday_end:
        for planet_id, planet in st.session_state.planets.items():
            lon = swe.calc_ut(julday, planet_id)[0][0]
            data.append({
                'julday': julday,
                'planet_id': planet_id,
                'longitude': lon,
            })
        julday += julday_step
    return pd.DataFrame(data)

def is_aspect(angle1, angle2, aspect_id):
    """
    Check if two planetary angles form a specific aspect.

    Args:
        angle1 (float): The first planetary angle in degrees.
        angle2 (float): The second planetary angle in degrees.
        aspect_id (str): The ID of the aspect to check from session state.

    Returns:
        bool: True if the aspect is formed, False otherwise.
    """
    aspect = st.session_state.aspects[aspect_id]
    angle = aspect['angle']
    orb = aspect['orb']
    return angle - orb <= abs(swe.difdeg2n(angle1, angle2)) <= angle + orb

def find_aspect(lon1, lon2):
    for id in st.session_state.aspects.keys():
        if is_aspect(lon1, lon2, id):
            return id
    return None

def sign_string(lon):
    # Determine the sign based on the longitude
    sign = calculate_sign(lon)
    # Retrieve the symbol for the sign from session_state
    sign_symbol = st.session_state.signs[sign]['symbol']
    # Calculate the degrees within the sign (0-29)
    degree = lon - sign * 30
    deg_int = int(degree)
    # Calculate minutes and seconds
    minute = (degree - deg_int) * 60
    min_int = int(minute)
    second = (minute - min_int) * 60
    sec_int = round(second)  # Rounded to avoid float precision issues
    # Return formatted string
    return f'{sign_symbol} {deg_int}° {min_int}\' {sec_int}\"'
