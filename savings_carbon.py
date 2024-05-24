from datetime import datetime

def calculate_total_savings_and_carbon_emissions(df_copy02, data_desejada, VALOR_KWH_CEMIG, VALOR_KWH_FATURADO):
    # Calcula a economia total e as emissões de carbono evitadas

    # Converte a data desejada em formato datetime para filtragem
    data_limite = datetime.strptime(data_desejada, '%m/%Y')
    df_filtrado = df_copy02[df_copy02['Período'] <= data_limite]
    
    # Soma a geração total a partir dos dados filtrados
    total_gerado = df_filtrado['Geração'].sum()
    
    # Calcula o custo sem desconto e com desconto para a energia gerada
    custo_sem_desconto = total_gerado * VALOR_KWH_CEMIG
    custo_com_desconto = total_gerado * VALOR_KWH_FATURADO
    
    # Calcula a economia total baseada nos custos calculados
    total_economia = custo_sem_desconto - custo_com_desconto
    
    # Calcula as emissões de CO2 evitadas, assumindo que cada kWh evita 0.4 kg de CO2
    total_emissoes_evitadas = 0.4 * total_gerado

    return total_economia, total_emissoes_evitadas
