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
    latitude_decimal = st.session_state.bday_latitude_deg + st.session_state.bday_latitude_min / 60
    longitude_decimal = st.session_state.bday_longitude_deg + st.session_state.bday_longitude_min / 60
    latitude_decimal *= -1 if st.session_state.bday_latitude_direction == 'S' else 1
    longitude_decimal *= -1 if st.session_state.bday_longitude_direction == 'W' else 1

    # Calculate houses directly into a DataFrame
    house_system = b'P'  # Placidus system
    house_cusps, ascmc = swe.houses(st.session_state.bday_julday_utc, latitude_decimal, longitude_decimal, house_system)
    
    houses_df = pd.DataFrame({
        'House': range(1, len(house_cusps) + 1),
        'Longitude': house_cusps,
    })
    houses_df['Sign'] = houses_df['Longitude'].apply(calculate_sign)
    houses_df['Longitude_str'] = houses_df['Longitude'].apply(sign_string)

    # Calculate planet positions into a DataFrame
    planet_data = []
    for id, planet in st.session_state.planets.items():
        lon, lat, dist, lon_speed, lat_speed, dist_speed = swe.calc_ut(st.session_state.bday_julday_utc, id)[0]
        retrograde_status = '℞' if lon_speed < 0 else ""
        planet_data.append([id, planet["name"], retrograde_status, planet['symbol'], find_house(st.session_state.bday_julday_utc, id, latitude_decimal, longitude_decimal), calculate_sign(lon), lon, lat, dist, lon_speed, lat_speed, dist_speed, sign_string(lon)])

    planets_df = pd.DataFrame(planet_data, columns=['id', 'Name', 'Direction', 'Symbol', 'House', 'Sign', 'Longitude', 'Latitude', 'Distance', 'Lon_speed', 'Lat_speed', 'Dist_speed', 'Longitude_str'])

    # Calculate aspects using vectorized approach (if possible)
    planetary_symbols = planets_df['Symbol'].tolist()
    planetary_aspect_matrix = pd.DataFrame('', index=planetary_symbols, columns=planetary_symbols)

    for i, lon1 in enumerate(planets_df['Longitude']):
        for j in range(i + 1, len(planets_df)):
            lon2 = planets_df.loc[j, 'Longitude']
            aspect = find_aspect(lon1, lon2)
            if aspect is not None:
                planetary_aspect_matrix.iloc[j, i] = st.session_state.aspects[aspect]['symbol']

    # Filter visible columns (excluding helper columns like Longitude_str)
    planets_df_visible = planets_df[['Name', 'Direction', 'Symbol', 'House', 'Longitude_str']]
    houses_df_visible = houses_df[['House', 'Longitude_str']]

    # Display DataFrames
    planets_col, houses_col = st.columns([2, 1])
    planets_col.subheader('Planet Positions')
    planets_col.write(planets_df_visible.to_html(index=False), unsafe_allow_html=True)
    houses_col.subheader('House Cusps')
    houses_col.write(houses_df_visible.to_html(index=False), unsafe_allow_html=True)

    # Display the aspect matrix with maximum width
    st.subheader('Aspects Matrix')
    st.dataframe(planetary_aspect_matrix, use_container_width=True)

    # Display Elements and Modalities Graphs
    weights = [3, 3, 2, 2, 2, 2, 1, 1, 1, 1]  # Planetary weights in order

    # Initialize counts for elements and modalities
    elements = {'Fire': 0, 'Earth': 0, 'Water': 0, 'Air': 0}
    modalities = {'Cardinal': 0, 'Fixed': 0, 'Mutable': 0}

    # Helper function to update elements and modalities based on sign
    def update_element_and_modality_by_sign(sign, weight):
        """Updates the element and modality totals based on the given sign and weight."""
        element = st.session_state.signs[sign]['element']
        modality = st.session_state.signs[sign]['modality']
        elements[element] += weight
        modalities[modality] += weight

    # Add house elements and modalities (using weight of 3 for ASC and MC)
    update_element_and_modality_by_sign(houses_df.loc[0, 'Sign'], 3)  # ASC
    update_element_and_modality_by_sign(houses_df.loc[9, 'Sign'], 3)  # MC

    # Add planet elements and modalities
    for idx, row in planets_df.iterrows():
        update_element_and_modality_by_sign(row['Sign'], weights[idx])

    # Display the elements bar chart using Streamlit st.bar_chart
    el, mod = st.columns(2)
    el.subheader('Element Distribution')

    # Create DataFrame for element distribution and use st.bar_chart
    elements_df = pd.DataFrame(elements.items(), columns=['Element', 'Weight']).set_index('Element')
    el.bar_chart(elements_df)

    # Display the modalities bar chart using Streamlit st.bar_chart
    mod.subheader('Modality Distribution')

    # Create DataFrame for modality distribution and use st.bar_chart
    modalities_df = pd.DataFrame(modalities.items(), columns=['Modality', 'Weight']).set_index('Modality')
    mod.bar_chart(modalities_df)
