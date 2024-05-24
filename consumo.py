def calculate_consumption_generation(df_copy):
    # Agrega os dados mensais somando os consumos e somente as gerações não nulas
    monthly_data = df_copy.groupby('Período').agg({
        'Consumo': 'sum', 
        'Geração': lambda x: x[x != 0].sum()
    })
    
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
    monthly_data = monthly_data.rename(columns={
        'Consumo': 'Consumo [kWh]', 
        'Geração': 'Energia Injetada [kWh]'
    })
    
    # Calcula a média do consumo e geração e adiciona ao dataframe como uma nova linha 'Média'
    average_consumption = monthly_data['Consumo [kWh]'].mean()
    average_generation = monthly_data['Energia Injetada [kWh]'].mean()
    monthly_data.loc['Média'] = [int(average_consumption), int(average_generation)]
    
    # Reseta o índice para transformar os períodos em uma coluna novamente
    monthly_data.reset_index(inplace=True)

    return monthly_data
