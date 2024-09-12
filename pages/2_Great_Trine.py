import streamlit as st
import pandas as pd
from utils import calculate_sign, is_aspect, start_end_date, datetime_to_julday, initialize_session, calculate_planet_positions, julday_to_datetime
import datetime

def get_trine_element(sign1_id, sign2_id, sign3_id):
    # Obter os elementos dos três signos
    element1 = st.session_state.signs[sign1_id]['element']
    element2 = st.session_state.signs[sign2_id]['element']
    element3 = st.session_state.signs[sign3_id]['element']

    # Verificar se todos os elementos são iguais
    if element1 == element2 == element3:
        return element1
    else:
        return "Dissociate"

initialize_session()

# Configuração inicial da página
st.title('Great Trines Finder')

start_end_date()

if st.button('Find Great Trines'):
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    step = datetime.timedelta(days=1.0)
    start_jd = datetime_to_julday(start_date)
    end_jd = datetime_to_julday(end_date)
    if end_date <= start_date:
        st.warning('End Date must be higher than Start Date')
    elif end_date > start_date + datetime.timedelta(days=366):
        st.warning('The difference between the dates cannot be longer then a year')
    else:
        resultados=[]

        df = calculate_planet_positions(datetime_to_julday(start_date), datetime_to_julday(end_date), 1)

        # Loop através de cada data no DataFrame
        for jd, group in df.groupby('julday'):
            # Lista para armazenar posições de cada planeta na data atual
            planet_positions = group[['planet_id', 'longitude']].values
                    # Loop através dos planetas para encontrar combinações que formam um Grande Triângulo
            for i in range(len(planet_positions)):
                planet1_id = planet_positions[i][0]
                lon1 = planet_positions[i][1]
                sign1_id = calculate_sign(lon1)

                for j in range(i + 1, len(planet_positions)):
                    planet2_id = planet_positions[j][0]
                    lon2 = planet_positions[j][1]
                    sign2_id = calculate_sign(lon2)

                    # Calcular o ângulo entre planet1 e planet2
                    if not is_aspect(lon1, lon2, 2): continue

                    for k in range(j + 1, len(planet_positions)):
                        planet3_id = planet_positions[k][0]
                        lon3 = planet_positions[k][1]
                        sign3_id = calculate_sign(lon3)

                        # Calcular ângulos entre planet2 e planet3, e planet1 e planet3
                        if not is_aspect(lon2, lon3, 2): continue
                        if not is_aspect(lon1, lon3, 2): continue

                        # Obter o elemento do triângulo
                        trine_element = get_trine_element(sign1_id, sign2_id, sign3_id)
                        
                        resultados.append({
                            'Data': jd,
                            'planet1_id': planet1_id,
                            'signo_planet1': sign1_id,
                            'planet2_id': planet2_id,
                            'signo_planet2': sign2_id,
                            'planet3_id': planet3_id,
                            'signo_planet3': sign3_id,
                            'Elemento': trine_element
                        })

        # Converter a lista de resultados para DataFrame
        df_resultados = pd.DataFrame(resultados)

        # Mostrar os resultados no Streamlit
        if not df_resultados.empty:

            # Inicializar lista para armazenar períodos de Grandes Triângulos
            triângulos_períodos = []

            # Ordenar o DataFrame por 'Data' para garantir a continuidade
            df_resultados = df_resultados.sort_values(by='Data')

            # Inicializar variáveis para rastrear o início de um triângulo contínuo
            triângulo_atual = None
            data_início = None

            # Iterar sobre cada linha do DataFrame de resultados
            for index, row in df_resultados.iterrows():
                # Identificar o triângulo atual baseado nos planetas e signos
                triângulo_id = (
                    row['planet1_id'], row['signo_planet1'],
                    row['planet2_id'], row['signo_planet2'],
                    row['planet3_id'], row['signo_planet3']
                )

                if triângulo_atual is None:
                    # Primeiro triângulo encontrado
                    triângulo_atual = triângulo_id
                    data_início = row['Data']
                elif triângulo_id != triângulo_atual:
                    # Novo triângulo encontrado, armazenar o período do triângulo anterior
                    triângulos_períodos.append({
                        'Start': julday_to_datetime(data_início),
                        'End': julday_to_datetime(df_resultados.loc[index - 1, 'Data']),
                        'Planet 1': st.session_state.planets[triângulo_atual[0]]['symbol'],
                        'Sign 1': st.session_state.signs[triângulo_atual[1]]['symbol'],
                        'Planet 2': st.session_state.planets[triângulo_atual[2]]['symbol'],
                        'Sign 2': st.session_state.signs[triângulo_atual[3]]['symbol'],
                        'Planet 3': st.session_state.planets[triângulo_atual[4]]['symbol'],
                        'Sign 3': st.session_state.signs[triângulo_atual[5]]['symbol'],
                        'Element': get_trine_element(triângulo_atual[1], triângulo_atual[3], triângulo_atual[5]),                        
                    })
                    # Atualizar triângulo atual e data de início
                    triângulo_atual = triângulo_id
                    data_início = row['Data']

            # Adicionar o último triângulo ao final da lista
            if triângulo_atual is not None:
                triângulos_períodos.append({
                    'Start': julday_to_datetime(data_início),
                    'End': julday_to_datetime(df_resultados.iloc[-1]['Data']),
                    'Planet 1': st.session_state.planets[triângulo_atual[0]]['symbol'],
                    'Sign 1': st.session_state.signs[triângulo_atual[1]]['symbol'],
                    'Planet 2': st.session_state.planets[triângulo_atual[2]]['symbol'],
                    'Sign 2': st.session_state.signs[triângulo_atual[3]]['symbol'],
                    'Planet 3': st.session_state.planets[triângulo_atual[4]]['symbol'],
                    'Sign 3': st.session_state.signs[triângulo_atual[5]]['symbol'],
                    'Element': get_trine_element(triângulo_atual[1], triângulo_atual[3], triângulo_atual[5]),
                })

            # Converter a lista de períodos para DataFrame
            df_triângulos_períodos = pd.DataFrame(triângulos_períodos)

            # Exibir o DataFrame de períodos de Grandes Triângulos
            st.subheader('Great Trines Found')
            st.write(df_triângulos_períodos)

            