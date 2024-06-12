import streamlit as st
from datetime import datetime

def process_data(df, data_desejada, numero_instalacao):
    # Converte a data desejada para o formato datetime se estiver em string
    if isinstance(data_desejada, str):
        data_desejada = datetime.strptime(data_desejada, '%m/%Y')

    # Filtra o dataframe por período e modalidade usando condições específicas
    mes_periodo = data_desejada.strftime('%m/%Y')
    df_filtered = df[(df['Período'] == mes_periodo) & (df['Modalidade'].isin(numero_instalacao))]

    # Depuração: Verificar dados filtrados por período e modalidade
    st.write("Dados filtrados por período e modalidade:", df_filtered)

    # Arredonda os valores do saldo atual para duas casas decimais
    df_filtered['Saldo Atual'] = df_filtered['Saldo Atual'].round(2)

    # Armazena a data desejada no estado da sessão para uso posterior
    st.session_state.data_desejada = data_desejada

    return df_filtered, mes_periodo


