from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from utils import ordenar_periodo

# Definição de caminhos para fontes e criação de objetos de fonte com diferentes tamanhos e estilos.
fonte_bold = "fonts/OpenSans-Bold.ttf"
fonte_normal = "fonts/OpenSans-Regular.ttf"
font_bold1 = ImageFont.truetype(fonte_bold, size=38)
font_bold11111 = ImageFont.truetype(fonte_bold, size=34)
font_bold2222 = ImageFont.truetype(fonte_bold, size=36)
font_regular1 = ImageFont.truetype(fonte_normal, size=25)
font_bold_carb = ImageFont.truetype(fonte_bold, size=38)
font_bold_eco = ImageFont.truetype(fonte_bold, size=40)
font_bold12 = ImageFont.truetype(fonte_bold, size=49)
font_bold_df = ImageFont.truetype(fonte_bold, size=13)
font_bold_dff = ImageFont.truetype("fonts/OpenSans-ExtraBold.ttf", size=13)
font_df = ImageFont.truetype(fonte_normal, size=13)
font_bold_df3 = ImageFont.truetype(fonte_bold, size=18)
font_df3 = ImageFont.truetype(fonte_normal, size=18)
color_light_gray = "#F0F0F0"
color_dark_gray = "#D3D3D3"

def format_currency(value):
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def generate_image(preprocessed_df, monthly_data, selected_columns, default_columns, calculo_tipo, RECEBIDO, VALOR_A_PAGAR, VALOR_KWH_CEMIG, DESCONTO, VALOR_KWH_FATURADO, economia_total, carbono_economia, cliente_text, mes_referencia, vencimento02):
    # Abrir uma imagem existente que servirá como base.
    img = Image.open('boleto_padrao04.png')
    draw = ImageDraw.Draw(img)
    
    # Conversão e formatação de valores monetários para exibição.
    recebido_inteiro = int(RECEBIDO)
    recebido_text = f"{recebido_inteiro:,d}".replace(',', '.')

    # Calcular a posição x com base no comprimento do texto
    pos_x = 912 - (len(recebido_text) - 4) * 20

    # Adicionar texto "RECEBIDO" ou "COMPENSADO" acima do valor do recebido
    texto_acima = "RECEBIDO" if calculo_tipo == 'Recebimento' else "COMPENSADO"
    text_width_acima = draw.textlength(texto_acima, font=font_bold2222)
    pos_x_acima = 928 + (100 - text_width_acima) // 2  # Ajuste para centralizar o texto
    draw.text((pos_x_acima, 1108), texto_acima, fill="black", font=font_bold2222)  # Mover um pouco para cima

    # Adicionar textos dinâmicos à imagem, posicionando-os de acordo com os valores calculados ou fixos.
    if len(recebido_text) > 4:
        draw.text((pos_x, 1168), recebido_text, fill="black", font=font_bold1)
    else:
        draw.text((888, 1168), recebido_text, fill="black", font=font_bold1)

    mes_text = str(mes_referencia)
    draw.text((440, 667), mes_text, fill="black", font=font_regular1)
    vencimento_text = str(vencimento02)
    draw.text((360, 702), vencimento_text, fill="black", font=font_regular1)
    economia_text = format_currency(economia_total)
    draw.text((1020, 2240), economia_text, fill="black", font=font_bold_eco)
    carbono_inteiro = int(carbono_economia)
    carbono_text = f"{carbono_inteiro:,d} Kg".replace(',', '.')
    draw.text((975, 2112), carbono_text, fill="black", font=font_bold_carb)

    # Repetição deste processo para outros textos dinâmicos, incluindo tratamento de texto e posicionamento.
    valor_a_pagar_inteiro = VALOR_A_PAGAR
    valor_a_pagar_text = format_currency(valor_a_pagar_inteiro)
    draw.text((880, 1407), valor_a_pagar_text, fill="black", font=font_bold1)
    
    valortexto = "VALOR A PAGAR"
    draw.text((850, 1337), valortexto, fill="black", font=font_bold11111)
    
    draw.text((297, 631), cliente_text, fill="black", font=font_regular1)
    KWH_CEMIG_text = str(VALOR_KWH_CEMIG)
    draw.text((740, 663), KWH_CEMIG_text, fill="black", font=font_bold12)
    KWH_FATURADO_text = str(VALOR_KWH_FATURADO)
    draw.text((1310, 663), KWH_FATURADO_text, fill="black", font=font_bold12)
    DESCONTO_inteiro = int(DESCONTO)
    DESCONTO_text = str(DESCONTO_inteiro)
    # Ajuste da posição de texto baseado em seu comprimento.
    if len(DESCONTO_text) > 2:
        draw.text((970, 663), DESCONTO_text, fill="black", font=font_bold12)
    elif len(DESCONTO_text) < 2:
        draw.text((1015, 663), DESCONTO_text, fill="black", font=font_bold12)
    else:
        draw.text((990, 663), DESCONTO_text, fill="black", font=font_bold12)

    # Processamento de DataFrame para exibição em tabela na imagem, com formatação de células e textos.
    # Cada célula é desenhada individualmente, textos são centralizados.
    # Ordenar e formatar o período
    monthly_data = ordenar_periodo(monthly_data)

    # Selecionar apenas os últimos 12 meses com registro
    monthly_data01 = monthly_data.iloc[-12:]

    dataframe_position1 = (225, 1130)

    # Exemplo de posição inicial do DataFrame na imagem
    cell_width_df1 = 180 
    cell_height_base1 = 90  # Altura base para uma linha
    max_height1 = 330 # Altura máxima disponível para o DataFrame na imagem

    # Ajustando a altura das células com base no número de linhas no DataFrame
    num_rows = len(monthly_data01)
    if num_rows == 0:
        num_rows = 1  # Prevenção contra divisão por zero

    cell_height_df1 = min(cell_height_base1, max_height1 // num_rows)

    columns = list(monthly_data01.columns)
    for j, column_name in enumerate(columns):
        text_width = draw.textlength(str(column_name), font=font_bold_dff)
        text_position_x = dataframe_position1[0] + j * cell_width_df1 + (cell_width_df1 - text_width) // 2
        draw.rectangle(
            [(dataframe_position1[0] + j * cell_width_df1, dataframe_position1[1]),
            (dataframe_position1[0] + (j + 1) * cell_width_df1, dataframe_position1[1] + cell_height_df1)],
            fill=color_dark_gray,
            outline="black"
        )
        draw.text((text_position_x, dataframe_position1[1] + 2), str(column_name), fill="black", font=font_bold_df)

    for i, (_, row) in enumerate(monthly_data01.iterrows()):
        for j, cell_value in enumerate(row):
            background_color_df = color_dark_gray if i == len(monthly_data01) - 1 else color_light_gray
            draw.rectangle(
                [(dataframe_position1[0] + j * cell_width_df1, dataframe_position1[1] + (i + 1) * cell_height_df1),
                (dataframe_position1[0] + (j + 1) * cell_width_df1, dataframe_position1[1] + (i + 2) * cell_height_df1)],
                fill=background_color_df,
                outline="black"
            )
            cell_text = str(cell_value)
            if i == len(monthly_data01) - 1:
                cell_text = cell_text.upper() if columns[j] == "Período" else cell_text
                text_width = draw.textlength(cell_text, font=font_bold_df)
                text_font = font_bold_df
            else:
                text_width = draw.textlength(cell_text, font=font_df)
                text_font = font_df
            text_height = text_font.size
            text_position = (
                dataframe_position1[0] + j * cell_width_df1 + (cell_width_df1 - text_width) // 2,
                dataframe_position1[1] + (i + 1) * cell_height_df1 + (cell_height_df1 - text_height) // 2
            )
            draw.text(text_position, cell_text, fill="black", font=text_font)

    # Definir as posições e tamanhos das células dinamicamente
    dataframe_position = (220, 878)  # Exemplo de posição inicial do DataFrame na imagem

    total_width = 1250  # Largura total disponível para o DataFrame na imagem

    cell_height_base = 70  # Altura base para uma linha
    max_height = 95  # Altura máxima disponível para o DataFrame na imagem
 
    # Ajuste do DataFrame para exibição com as colunas selecionadas
    if not selected_columns:
        preprocessed_df = pd.DataFrame(columns=default_columns)  # DataFrame vazio
        cell_width_df = total_width  # Usar largura total disponível
    else:
        preprocessed_df = preprocessed_df[selected_columns].copy()
        cell_width_df = total_width // len(selected_columns)  # Ajustar a largura das células com base no número de colunas
   
    # Ajustando a altura das células com base no número de linhas no DataFrame
    num_rows = len(preprocessed_df)
    if num_rows == 0:
        num_rows = 1  # Prevenção contra divisão por zero

    cell_height_df = min(cell_height_base, max_height // num_rows)

    # Desenhando colunas e nomes de colunas
    columns = list(preprocessed_df.columns)
    for j, column_name in enumerate(columns):
        text_width = draw.textlength(str(column_name), font=font_bold_df3)
        text_position_x = dataframe_position[0] + j * cell_width_df + (cell_width_df - text_width) // 2
        draw.rectangle(
            [(dataframe_position[0] + j * cell_width_df, dataframe_position[1]),
            (dataframe_position[0] + (j + 1) * cell_width_df, dataframe_position[1] + cell_height_df)],
            fill="darkgray", outline="black"
        )
        draw.text((text_position_x, dataframe_position[1] + (cell_height_df - font_bold_df3.size) // 2),
                str(column_name), fill="white", font=font_bold_df3)

    # Desenhando dados do DataFrame
    for i, (_, row) in enumerate(preprocessed_df.iterrows()):
        background_color = "lightgray" if i % 2 == 0 else "darkgray"
        for j, cell_value in enumerate(row):
            cell_text = str(cell_value)
            text_width = draw.textlength(cell_text, font=font_df3)
            text_position_x = dataframe_position[0] + j * cell_width_df + (cell_width_df - text_width) // 2
            text_position_y = dataframe_position[1] + (i + 1) * cell_height_df + (cell_height_df - font_df3.size) // 2
            draw.rectangle(
                [(dataframe_position[0] + j * cell_width_df, dataframe_position[1] + (i + 1) * cell_height_df),
                (dataframe_position[0] + (j + 1) * cell_width_df, dataframe_position[1] + (i + 2) * cell_height_df)],
                fill=background_color, outline="black"
            )
            draw.text((text_position_x, text_position_y), cell_text, fill="black", font=font_df3)

    return img  # Finalização e retorno da imagem modificada
