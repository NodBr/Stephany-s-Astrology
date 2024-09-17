import streamlit as st
import swisseph as swe
import datetime as dt
from utils import initialize_session, datetime_to_julday, calculate_sign, birth_data
import pandas as pd
import pydeck as pdk

initialize_session()

# Page title and input section headers
st.title('Solar Revolution Calculator')
st.header('Birth Data')

birth_data()

if st.session_state.bday_date is not None:
    st.header('Solar Revolution Criteria')
    col1, col2, col3 = st.columns(3)
    
    # Seleção do ano da Revolução Solar
    st.session_state.bday_rs_year = col1.number_input(label='Solar Revolution Year', min_value=st.session_state.bday_date.year,max_value=st.session_state.bday_date.year + 120, value=st.session_state.bday_date.year, step=1, label_visibility='visible')
    
    # Obter os nomes dos planetas da sessão
    planet_names = ['Ascendant'] + [planet['name'] for planet in st.session_state.planets.values()]
    
    # Seleção do planeta
    st.session_state.rs_view = col2.selectbox(label='View', options=planet_names, index=None)
    
    # Critérios de filtragem
    if st.session_state.rs_view == 'Ascendant':
        st.session_state.rs_filter = col3.selectbox(label='Sign Filter', options=[sign['name'] for sign in st.session_state.signs.values()], index=None)
    else:
        st.session_state.rs_filter = col3.selectbox(label='House Filter', options=['1st House', '2nd House', '3rd House', '4th House', '5th House', '6th House', '7th House', '8th House', '9th House', '10th House', '11th House', '12th House'],index=None)

if st.button(label='Run'):
    # Convert input date and time to Julian Day
    birth_dt = dt.datetime(st.session_state.bday_date.year, st.session_state.bday_date.month, st.session_state.bday_date.day, st.session_state.bday_hour, st.session_state.bday_minute)
    birth_jd = datetime_to_julday(birth_dt)
    
    # Find Sun's longitude during birth time
    sun_long = swe.calc_ut(birth_jd, 0)[0][0]
    
    # Find julian day for the start of Solar Revolution Year
    year_start_dt = dt.datetime(st.session_state.bday_rs_year, 1, 1, 0, 0, 0, 0)
    year_start_jd = datetime_to_julday(year_start_dt)
    
    # Find the julian day of the moment of the Solar Revolution
    solcross_jd = swe.solcross(sun_long, year_start_jd)
    
# Calculate ascendant for every coordinate
    results = []
    for latitude in range(-66, 67, 1):
        for longitude in range(-180, 180, 1):
            asc_lon = swe.houses(solcross_jd, latitude, longitude)[0][0]
            asc_sign = calculate_sign(asc_lon)
            sign_data = st.session_state.signs[asc_sign]
            results.append({
                'latitude': latitude,
                'longitude': longitude,
                'asc_lon': asc_lon,
                'asc_sign': sign_data['name'],
                'rgb_color': sign_data['rgb_color']
            })
    results_df = pd.DataFrame(results)

    # Create a Pydeck layer for the map with colors from DataFrame
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=results_df,
        get_position='[longitude, latitude]',
        get_fill_color='[rgb_color[0], rgb_color[1], rgb_color[2], 120]',  # Using RGB values with transparency
        get_radius=30000,
        pickable=True
    )

    # Set up the view for the map
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1
    )

    # Render the map using Pydeck
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    st.pydeck_chart(r)

    # Add a legend with colors and signs below the chart
    cols = st.columns(4)  # Create four columns

    for id, sign_data in st.session_state.signs.items():
        color = sign_data['color']
        col = cols[id % 4]  # Distribute items across the four columns
        col.markdown(f'<span style="display: inline-block; width: 16px; height: 16px; background-color: {color}; margin-right: 8px;"></span> {sign_data["name"]}', unsafe_allow_html=True)