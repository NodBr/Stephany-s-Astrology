import streamlit as st
import swisseph as swe
import datetime as dt
from utils import initialize_session, datetime_to_julday, calculate_sign, birth_data
import pandas as pd
import pydeck as pdk

initialize_session()

# Page title and input section headers
st.title('Natal Chart Calculator')
st.header('Birth Data')

birth_data()

st.session_state.bday_rs_year = st.number_input(label='Solar Revolution Year', min_value=st.session_state.bday_date.year, max_value=st.session_state.bday_date.year+120, value=st.session_state.bday_date.year, step=1, label_visibility='visible')

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

    # Color Dictionary and corresponding signs
    colors = ['#C60000', '#179559', '#FFB100', '#B8C2CA', '#A12600', '#A66018', '#EA987F', '#080808', '#EC6F29', '#B68C74', '#197E91', '#598F88']
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    # Calculate ascendant for every coordinate
    results = []
    for latitude in range(-66, 67, 1):
        for longitude in range(-180, 180, 1):
            asc_lon = swe.houses(solcross_jd, latitude, longitude)[0][0]
            asc_sign = calculate_sign(asc_lon)
            results.append({
                'latitude': latitude,
                'longitude': longitude,
                'asc_lon': asc_lon,
                'asc_sign': asc_sign,
                'color': colors[asc_sign]
            })
    results_df = pd.DataFrame(results)
    
    # Convert hexadecimal colors to RGBA format with transparency
    def hex_to_rgba(hex_color, alpha=120):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return [r, g, b, alpha]

    # Add RGBA color column to the DataFrame
    results_df['rgba_color'] = results_df['color'].apply(lambda x: hex_to_rgba(x))

    # Create a Pydeck layer for the map with colors from DataFrame
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=results_df,
        get_position='[longitude, latitude]',
        get_fill_color='rgba_color',
        get_radius=30000,  # Set the radius size of the points
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
    cols = st.columns(4)  # Create three columns

    for i, (color, sign) in enumerate(zip(colors, signs)):
        col = cols[i % 4]  # Distribute items across the four columns
        col.markdown(f'<span style="display: inline-block; width: 16px; height: 16px; background-color: {color}; margin-right: 8px;"></span> {sign}', unsafe_allow_html=True)