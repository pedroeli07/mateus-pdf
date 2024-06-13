def format_value(value):
    try:
        value = float(value)
        if value.is_integer():
            return int(value)
        return f"{value:.2f}"
    except (ValueError, TypeError):
        return value

def calculate_consumption_generation(df_copy, calc_type="Geração"):
    if calc_type == "Geração":
        aggregation = {
            'Consumo': 'sum', 
            'Geração': lambda x: x[x != 0].sum()
        }
        columns_rename = {
            'Consumo': 'Consumo [kWh]', 
            'Geração': 'Energia Injetada [kWh]'
        }
    elif calc_type == "Compensação":
        aggregation = {
            'Consumo': 'sum', 
            'Compensação': 'sum'
        }
        columns_rename = {
            'Consumo': 'Consumo [kWh]', 
            'Compensação': 'Compensação [kWh]'
        }
    
    # Agrega os dados mensais somando os consumos e somente as gerações/compensações não nulas
    monthly_data = df_copy.groupby('Período').agg(aggregation)
    
    # Mapeamento de números de meses para abreviações em português
    months_map = {
        '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr', 
        '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago', 
        '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
    }
    
    # Renomeia os índices para formato de mês abreviado/ano
    monthly_data.index = monthly_data.index.map(
        lambda x: f"{months_map[x.split('/')[0]]}/{x.split('/')[1]}"
    )
    
    # Renomeia as colunas para inclusão das unidades
    monthly_data = monthly_data.rename(columns=columns_rename)
    
    # Calcula a média do consumo e geração/compensação
    average_consumption = monthly_data['Consumo [kWh]'].astype(float).mean()
    if calc_type == "Geração":
        average_generation = monthly_data['Energia Injetada [kWh]'].astype(float).mean()
        monthly_data.loc['Média'] = [average_consumption, average_generation]
    elif calc_type == "Compensação":
        average_compensacao = monthly_data['Compensação [kWh]'].astype(float).mean()
        monthly_data.loc['Média'] = [average_consumption, average_compensacao]
    
    # Arredondar os valores para uma casa decimal e formatar os valores
    monthly_data = monthly_data.applymap(format_value)
    
    # Reseta o índice para transformar os períodos em uma coluna novamente
    monthly_data.reset_index(inplace=True)

    return monthly_data

