import streamlit as st
import pandas as pd
import datetime as dt
import swisseph as swe
from utils import datetime_to_julday, initialize_session, sign_string, find_aspect, birth_data

initialize_session()

# Page title and input section headers
st.title('Natal Chart Calculator')
st.header('Birth Data')

birth_data()

# Chart display logic
if st.button('Show Chart'):
    st.header(f'{st.session_state.first_name} {st.session_state.last_name}\'s Natal Chart')

    # Convert input date and time to Julian Day
    birth_datetime = dt.datetime(
        st.session_state.bday_date.year,
        st.session_state.bday_date.month,
        st.session_state.bday_date.day,
        st.session_state.bday_hour,
        st.session_state.bday_minute)
    birth_julian_day = datetime_to_julday(birth_datetime)

    # Convert latitude and longitude to decimal format
    latitude_decimal = st.session_state.bday_latitude_deg + st.session_state.bday_latitude_min / 60
    longitude_decimal = st.session_state.bday_longitude_deg + st.session_state.bday_longitude_min / 60
    latitude_decimal *= -1 if st.session_state.bday_latitude_direction == 'S' else 1
    longitude_decimal *= -1 if st.session_state.bday_longitude_direction == 'W' else 1

    # Calculate astrological houses
    calculated_houses_data = []
    house_system = b'P'  # Placidus system
    house_cusps, ascmc = swe.houses(birth_julian_day, latitude_decimal, longitude_decimal, house_system)

    for id in range(len(house_cusps)):
        calculated_houses_data.append({
            'House': id+1,
            '.Longitude': house_cusps[id],
            'Longitude': sign_string(house_cusps[id])
        })

    # Prepare house cusp data
    houses_df = pd.DataFrame(calculated_houses_data)

    # Calculate planet positions
    calculated_planets_data = []
    for id, planet in st.session_state.planets.items():
        lon, lat, dist, lon_speed, lat_speed, dist_speed = swe.calc_ut(birth_julian_day, id)[0]
        retrograde_status = '℞' if lon_speed < 0 else ""
        calculated_planets_data.append({
            '.id': id,
            'Name': planet["name"],
            'Direction': retrograde_status,
            'Symbol': planet['symbol'],
            '.Longitude': lon,
            '.Latitude': lat,
            '.Distance': dist,
            '.Lon_speed': lon_speed,
            '.Lat_speed': lat_speed,
            '.Dist_speed': dist_speed,
            'Longitude': sign_string(lon)
        })

    planets_df = pd.DataFrame(calculated_planets_data)

    # Filter out columns that start with a period ('.')
    planets_df_visible = planets_df.loc[:, ~planets_df.columns.str.startswith('.')]
    houses_df_visible = houses_df.loc[:, ~houses_df.columns.str.startswith('.')]

    # Calculate aspects
    planetary_symbols = [planet['symbol'] for planet in st.session_state.planets.values()]
    planetary_aspect_matrix = pd.DataFrame('', index=planetary_symbols, columns=planetary_symbols)
    for i in range(len(calculated_planets_data)):
        lon1 = calculated_planets_data[i]['.Longitude']
        for j in range(i+1, len(calculated_planets_data)):
            lon2 = calculated_planets_data[j]['.Longitude']
            aspect = find_aspect(lon1, lon2)
            if aspect is not None:
                aspect_symbol = st.session_state.aspects[aspect]['symbol']
                # Add the aspect to both (planet1, planet2) and (planet2, planet1) positions
                planetary_aspect_matrix.iloc[j, i] = aspect_symbol

    # Display DataFrames
    planets_col, houses_col = st.columns([2, 1])
    planets_col.subheader('Planet Positions')
    planets_col.write(planets_df_visible.to_html(index=False), unsafe_allow_html=True)
    houses_col.subheader('House Cusps')
    houses_col.write(houses_df_visible.to_html(index=False), unsafe_allow_html=True)
    
    # Display the aspect matrix with maximum width
    st.subheader('Aspects Matrix')
    st.dataframe(planetary_aspect_matrix, use_container_width=True)
