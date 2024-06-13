import pandas as pd

def ordenar_periodo(mes_data, coluna='Período'):
    month_mapping_pt_to_en = {
        "Jan": "Jan",
        "Fev": "Feb",
        "Mar": "Mar",
        "Abr": "Apr",
        "Mai": "May",
        "Jun": "Jun",
        "Jul": "Jul",
        "Ago": "Aug",
        "Set": "Sep",
        "Out": "Oct",
        "Nov": "Nov",
        "Dez": "Dec"
    }

    month_mapping_en_to_pt = {v: k for k, v in month_mapping_pt_to_en.items()}

    # Separar a linha de média dos outros dados
    non_average = mes_data[mes_data[coluna] != 'Média'].copy()
    average = mes_data[mes_data[coluna] == 'Média'].copy()

    # Converter os nomes dos meses de português para inglês para ordenação
    non_average.loc[:, coluna] = non_average[coluna].apply(lambda x: x.replace(x[:3], month_mapping_pt_to_en[x[:3]]))
    non_average.loc[:, coluna] = pd.to_datetime(non_average[coluna], format='%b/%Y', errors='coerce')
    
    # Verificar se a conversão para datetime foi bem-sucedida
    if non_average[coluna].isnull().any():
        raise ValueError("Falha ao converter a coluna para datetime. Verifique os valores na coluna.")
    
    non_average = non_average.sort_values(by=coluna).reset_index(drop=True)
    non_average.loc[:, coluna] = non_average[coluna].dt.strftime('%b/%Y')

    # Reverter os nomes dos meses de inglês para português para exibição
    non_average.loc[:, coluna] = non_average[coluna].apply(lambda x: x.replace(x[:3], month_mapping_en_to_pt[x[:3]]))

    # Combinar os dados de volta, incluindo a linha de média
    sorted_data = pd.concat([non_average, average]).reset_index(drop=True)

    return sorted_data

