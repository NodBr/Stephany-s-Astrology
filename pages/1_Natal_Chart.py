import streamlit as st
import pandas as pd
import swisseph as swe
from utils import initialize_session, sign_string, find_aspect, birth_data, find_house, calculate_sign

initialize_session()

# Page title and input section headers
st.title('Natal Chart Calculator')

birth_data()

# Chart display logic
if st.button('Show Chart'):
    st.header(f'{st.session_state.first_name} {st.session_state.last_name}\'s Natal Chart')

    # Convert latitude and longitude to decimal format
    latitude_direction = st.session_state.bday_latitude_direction
    longitude_direction = st.session_state.bday_longitude_direction
    latitude_decimal = (st.session_state.bday_latitude_deg + st.session_state.bday_latitude_min / 60) * (-1 if latitude_direction == 'S' else 1)
    longitude_decimal = (st.session_state.bday_longitude_deg + st.session_state.bday_longitude_min / 60) * (-1 if longitude_direction == 'W' else 1)

    # Create a list to store data and convert it to a DataFrame later
    data_list = []

    # Calculate houses and add the data to the list
    house_system = b'P'  # Placidus system
    house_cusps, ascmc = swe.houses(st.session_state.bday_julday_utc, latitude_decimal, longitude_decimal, house_system)

    for i, cusp in enumerate(house_cusps):
        data_list.append({
            'Name': None, 'Type': 'House', 'House': i + 1, 'Lon': cusp, 'Symbol': None, 'Direction': None, 'Weight': 3 if i == 0 or i == 9 else 0
        })

    # Calculate planet positions and add the data to the list
    for id, planet in st.session_state.planets.items():
        lon, lat, dist, lon_speed, lat_speed, dist_speed = swe.calc_ut(st.session_state.bday_julday_utc, id)[0]
        retrograde_status = '℞' if lon_speed < 0 else ""
        data_list.append({
            'Name': planet['name'],
            'Type': 'Planet',
            'House': find_house(st.session_state.bday_julday_utc, id, latitude_decimal, longitude_decimal),
            'Lon': lon,
            'Symbol': planet['symbol'],
            'Direction': retrograde_status,
            'Weight': 3 if id <= 1 else 2 if id <= 5 else 1
        })

    # Create the DataFrame all at once from the list of dictionaries
    data = pd.DataFrame(data_list)

    # Add Sign and Longitude columns
    data['Sign'] = data['Lon'].apply(calculate_sign)
    data['Longitude'] = data['Lon'].apply(sign_string)

    # Split the DataFrame into two: planets and houses
    planets_df = data[data['Type'] == 'Planet']
    houses_df = data[data['Type'] == 'House']

    # Display DataFrames separately
    planets_col, houses_col = st.columns([2, 1])
    planets_col.subheader('Planet Positions')
    planets_col.dataframe(planets_df[['Name', 'Symbol', 'Direction', 'House', 'Longitude']], hide_index=True)

    houses_col.subheader('House Cusps')
    houses_col.dataframe(houses_df[['House', 'Longitude']], hide_index=True, height=450)

    # Calculate aspects
    planetary_symbols = planets_df['Symbol'].tolist()
    planetary_aspect_matrix = pd.DataFrame('', index=planetary_symbols, columns=planetary_symbols)

    for i, lon1 in enumerate(planets_df['Lon']):
        for j in range(i + 1, len(planets_df)):
            lon2 = planets_df.iloc[j]['Lon']
            aspect = find_aspect(lon1, lon2)
            if aspect:
                planetary_aspect_matrix.iloc[j, i] = st.session_state.aspects[aspect]['symbol']

    # Display the aspect matrix
    st.subheader('Aspects Matrix')
    st.dataframe(planetary_aspect_matrix)

    # Calculate the distribution of elements and modalities in a vectorized manner
    data['Element'] = pd.Categorical(data['Sign'].apply(lambda x: st.session_state.signs[x]['element']), categories=['Fire', 'Earth', 'Air', 'Water'], ordered=True)
    data['Modality'] = pd.Categorical(data['Sign'].apply(lambda x: st.session_state.signs[x]['modality']), categories=['Cardinal', 'Fixed', 'Mutable'], ordered=True)

    total_weight = data['Weight'].sum()
    elements_df = data.groupby('Element', observed=False)['Weight'].sum() / total_weight * 100
    modalities_df = data.groupby('Modality', observed=False)['Weight'].sum() / total_weight * 100

    # Display element and modality bar charts
    el, mod = st.columns(2)
    el.subheader('Element Distribution (%)')
    el.bar_chart(elements_df)

    mod.subheader('Modality Distribution (%)')
    mod.bar_chart(modalities_df)