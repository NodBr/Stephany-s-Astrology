import streamlit as st
import swisseph as swe
import datetime as dt
from utils import initialize_session, datetime_to_julday, calculate_sign, birth_data, find_house
import pandas as pd
import pydeck as pdk

# Initialize session state variables
initialize_session()

# Page title and input section
st.title('Solar Revolution Calculator')
st.header('Birth Data')
birth_data()  # Collect birth data input

# Check if birth date is provided
if st.session_state.bday_date is not None:
    st.header('Solar Revolution Criteria')
    col1, col2, col3 = st.columns(3)
    
    # Select Solar Revolution Year
    st.session_state.sr_year = col1.number_input(
        label='Solar Revolution Year', 
        min_value=st.session_state.bday_date.year,
        max_value=st.session_state.bday_date.year + 120, 
        value=st.session_state.bday_date.year, 
        step=1
    )
    
    # Get planet names for selection
    planet_names = ['Ascendant'] + [planet['name'] for planet in st.session_state.planets.values()]
    
    # Select view (planet or Ascendant)
    st.session_state.sr_view = col2.selectbox(label='View', options=planet_names)
    
    # Set filter criteria based on the view selected
    if st.session_state.sr_view == 'Ascendant':
        sign_options = ['All'] + [sign['name'] for sign in st.session_state.signs.values()]
        st.session_state.sr_filter = col3.selectbox(
            label='Sign Filter', 
            options=sign_options
        )
    else:
        st.session_state.sr_filter = col3.selectbox(
            label='House Filter', 
            options=['All houses'] + [house['name'] for house in st.session_state.houses.values()]
        )

# Run button to execute calculations
if st.button(label='Run'):
    # Convert birth date and time to Julian Day
    birth_datetime = dt.datetime(
        st.session_state.bday_date.year, 
        st.session_state.bday_date.month, 
        st.session_state.bday_date.day, 
        st.session_state.bday_hour, 
        st.session_state.bday_minute
    )
    birth_julian_day = datetime_to_julday(birth_datetime)
    
    # Get Sun's longitude at birth time
    sun_longitude = swe.calc_ut(birth_julian_day, 0)[0][0]
    
    # Find the Julian Day for the start of the Solar Revolution year
    year_start_datetime = dt.datetime(st.session_state.sr_year, 1, 1)
    year_start_julian_day = datetime_to_julday(year_start_datetime)
    
    # Calculate the Julian Day of the Solar Revolution
    solar_cross_julian_day = swe.solcross(sun_longitude, year_start_julian_day)
    
    if st.session_state.sr_view == 'Ascendant':
        # Calculate Ascendant for a range of coordinates and store results
        results = [
            {
                'latitude': lat,
                'longitude': lon,
                'number': calculate_sign(swe.houses(solar_cross_julian_day, lat, lon)[0][0]),
                'rgb_color': tuple(st.session_state.signs[calculate_sign(swe.houses(solar_cross_julian_day, lat, lon)[0][0])]['rgb_color']),  # Convert list to tuple
                'caption': st.session_state.signs[calculate_sign(swe.houses(solar_cross_julian_day, lat, lon)[0][0])]['name']
            }
            for lat in range(-66, 67)
            for lon in range(-180, 179)
        ]
    else:
        results=[]
        planet_id = None
        for pid, planet in st.session_state.planets.items():
            if planet['name'] == st.session_state.sr_view:
                planet_id = pid
                break
        for lat in range(-66,67):
            for lon in range(-180, 180):
                number = find_house(solar_cross_julian_day, pid, lat, lon)
                results.append({
                    'latitude': lat,
                    'longitude': lon,
                    'number': number,
                    'rgb_color': tuple(st.session_state.signs[number-1]['rgb_color']),
                    'caption': st.session_state.houses[number]['name']
                })

    results_df = pd.DataFrame(results)

    # Apply the sign filter if the view is 'Ascendant'
    if st.session_state.sr_view == 'Ascendant' and st.session_state.sr_filter != 'All':
        filtered_df = results_df[results_df['caption'] == st.session_state.sr_filter]
    elif st.session_state.sr_view != 'Ascendant' and st.session_state.sr_filter != 'All houses':
        filtered_df = results_df[results_df['caption'] == st.session_state.sr_filter]
    else:
        filtered_df = results_df  # No filtering or "All" selected

    # Sort the DataFrame by 'number' to maintain natural order of signs
    results_df_sorted = filtered_df[['number', 'caption', 'rgb_color']].drop_duplicates().sort_values(by='number')

    # Create a Pydeck layer for the map using the filtered DataFrame
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_df,
        get_position='[longitude, latitude]',
        get_fill_color='[rgb_color[0], rgb_color[1], rgb_color[2], 120]',  # RGBA with transparency
        get_radius=30000,
        pickable=True
    )

    # Set up the map view
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1
    )

    # Render the map with Pydeck
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    # Create a legend using the sorted DataFrame
    unique_signs = results_df_sorted.to_dict(orient='records')
    cols = st.columns(4)

    # Distribute 12 items across 4 columns
    for idx, sign_data in enumerate(unique_signs):
        color = sign_data['rgb_color']
        caption = sign_data['caption']
        col_idx = idx % 4
        cols[col_idx].markdown(
            f'<span style="display: inline-block; width: 16px; height: 16px; background-color: rgb({color[0]}, {color[1]}, {color[2]}); margin-right: 8px;"></span> {caption}', 
            unsafe_allow_html=True
        )
