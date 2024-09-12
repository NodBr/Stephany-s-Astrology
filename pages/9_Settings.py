import streamlit as st
import datetime
import swisseph as swe
import pandas as pd
from utils import initialize_session

# Inicializar o session_state e carregar dados necessários
initialize_session()

# Calcular o Julian Day para a data inicial e final
julday_start = swe.julday(st.session_state.start_date.year, st.session_state.start_date.month, st.session_state.start_date.day, 0.0)
julday_end = swe.julday(st.session_state.end_date.year, st.session_state.end_date.month, st.session_state.end_date.day, 0.0)

# Calcular o step dinâmico
julday_step = (julday_end - julday_start) / 500

# Entrada dos orbes para cada aspecto
st.subheader('Orbs')
for aspect_id, aspect in st.session_state.aspects.items():
    title_col, orb_col, deg_col = st.columns(3)
    title_col.write(aspect['name'])
    st.session_state.aspects[aspect_id]['orb']=orb_col.number_input(
        label=f'{aspect["name"]}_orb', 
        min_value=0, 
        max_value=15, 
        value=st.session_state.aspects[aspect_id]['orb'],
        step=1, 
        key=f'{aspect["name"]}_orb',
        label_visibility='collapsed'
    )
    deg_col.write('degrees')

# Função para calcular posições dos planetas com step dinâmico
def calculate_planet_positions(julday_start, julday_end, julday_step):
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

# Botão para salvar informações e calcular posições planetárias
if st.button('Save settings'):    
    st.info('Settings saved.', icon="🖋️")