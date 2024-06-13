import pandas as pd
from PIL import Image
from io import BytesIO
import streamlit as st
from datetime import datetime, timedelta
from process_data import process_data
from savings_carbon import calculate_total_savings_and_carbon_emissions
from consumo import calculate_consumption_generation
from create_pdf import generate_pdf
from load_data import load_data
from image import generate_image, format_currency
from utils import ordenar_periodo

# Configura o título da aplicação Streamlit.
st.title("Processamento de Dados de Energia")

# Carrega os dados através de uma função personalizada.
df = load_data()

# Verifica se o DataFrame não está vazio e contém as colunas específicas.
if not df.empty and 'Período' in df.columns and 'Modalidade' in df.columns:
    # Permite ao usuário selecionar um período e a modalidade (loja) a partir de listas drop-down.
    available_dates = df['Período'].unique()
    data_desejada = st.selectbox("Selecione a data desejada:", available_dates, index=0, key="data_desejada_selectbox")
    available_inst = df['Modalidade'].unique()
    numero_instalacao = st.multiselect("Selecione a loja desejada:", available_inst, key="modalidade_selectbox")

    # Se a instalação e a data desejadas forem selecionadas, filtra o DataFrame com base nesses parâmetros.
    if numero_instalacao and data_desejada is not None:
        df_filtered2 = df[(df['Período'] == data_desejada) & (df['Modalidade'].isin(numero_instalacao))]
        df_filtered2 = df_filtered2[df_filtered2['Modalidade'] != 'Auto Consumo-Geradora']

        # Verificar os dados filtrados
        st.write("Dados Filtrados:", df_filtered2)

        # # Processar o DataFrame preprocessed_df
        # preprocessed_df = df_filtered2.copy()
        # preprocessed_df.drop(['Transferido', 'Geração'], axis=1, inplace=True)
        # preprocessed_df = preprocessed_df.query("Modalidade != 'Auto Consumo-Geradora'")

        # Verificar o DataFrame preprocessed_df
        # st.write("preprocessed_df:", preprocessed_df)

        # Calcula a soma das colunas 'Recebimento' e 'Compensação'
        RECEBIDO_RECEBIMENTO = int(df_filtered2['Recebimento'].sum())
        RECEBIDO_COMPENSACAO = int(df_filtered2['Compensação'].sum())

        # Botão para confirmar seleção de período e lojas, armazena seleção em sessão.
        if st.button('Confirmar Período e Lojas'):
            st.session_state.data_desejada = data_desejada
            st.session_state.numero_instalacao = numero_instalacao
            st.success('Período e lojas confirmados!')

        # Botões para selecionar o método de cálculo
        col1, col2 = st.columns(2)

        with col1:
            if st.button('Calcular por Recebimento'):
                st.session_state.RECEBIDO = RECEBIDO_RECEBIMENTO
                st.session_state.calculo_tipo = 'Recebimento'
                st.success('Cálculo selecionado: Recebimento')

        with col2:
            if st.button('Calcular por Compensação'):
                st.session_state.RECEBIDO = RECEBIDO_COMPENSACAO
                st.session_state.calculo_tipo = 'Compensação'
                st.success('Cálculo selecionado: Compensação')

        # Exibe os dados confirmados.
        if 'numero_instalacao' in st.session_state and 'data_desejada' in st.session_state:
            st.write(f"Período Referência selecionado: {st.session_state.data_desejada}")
            st.write(f"Lojas desejadas: {st.session_state.numero_instalacao}")
            if 'calculo_tipo' in st.session_state and 'RECEBIDO' in st.session_state:
                st.write(f"Cálculo selecionado: {st.session_state.calculo_tipo}")
                st.write(f"Qtde kWh faturado: {st.session_state.RECEBIDO} kWh")
            else:
                st.warning("Selecione o tipo de cálculo primeiro.")

        # Se o período e a instalação foram confirmados, permite ao usuário ajustar os valores de KWh e desconto.
        if 'data_desejada' in st.session_state and 'numero_instalacao' in st.session_state:
            # Definir valores padrão
            VALOR_KWH_CEMIG_PADRAO = 0.956
            DESCONTO_PADRAO = 20

            # Utiliza inputs para permitir ajustes nos valores de kWh da Cemig e percentual de desconto.
            VALOR_KWH_CEMIG = st.number_input("Digite o valor do KWh da Cemig (R$):", min_value=0.1000, max_value=2.00, value=VALOR_KWH_CEMIG_PADRAO, step=0.001, format="%.3f")
            DESCONTO = st.number_input("Digite o valor do desconto (%):", min_value=0, max_value=100, value=DESCONTO_PADRAO, step=1)

            # Botão para confirmar valores ajustados.
            if st.button('Confirmar Valores'):
                VALOR_KWH_CEMIG = VALOR_KWH_CEMIG
                DESCONTO = DESCONTO
                st.success('Valores confirmados!')

            # Calcula o valor faturado com base no desconto.
            VALOR_KWH_FATURADO = round(VALOR_KWH_CEMIG - ((VALOR_KWH_CEMIG * DESCONTO) / 100), 3)

            # Exibe os valores ajustados e calculados.
            st.write(f"Valor KWh Cemig confirmado: R${VALOR_KWH_CEMIG}")
            st.write(f"Desconto confirmado: {DESCONTO}%")
            st.write(f"Valor KWh faturado confirmado: R${VALOR_KWH_FATURADO}")

            # Calcula o valor a pagar com base na geração e no valor kWh faturado.
            if 'RECEBIDO' in st.session_state:
                RECEBIDO = st.session_state.RECEBIDO
                VALOR_A_PAGAR = round(RECEBIDO * VALOR_KWH_FATURADO, 2)
                st.write(f"Qtde kWh faturado: {RECEBIDO} kWh ")
                st.write(f"Valor a Pagar: R$ {VALOR_A_PAGAR}")

                # Processa os dados para o último mês e calcula o consumo e a geração mensal.
                df_last_month, ultimo_periodo = process_data(df, st.session_state.data_desejada, st.session_state.numero_instalacao)

                # Determinar o tipo de cálculo baseado na seleção do usuário
                calc_type = "Geração" if st.session_state.calculo_tipo == 'Recebimento' else "Compensação"
                df_copy = df.copy()
                monthly_data = calculate_consumption_generation(df_copy, calc_type)
                monthly_data = ordenar_periodo(monthly_data)

                st.write("Consumo e geração mensal:")
                st.dataframe(monthly_data)

                df_copy02 = df.copy()
                df_copy02['Período'] = pd.to_datetime(df_copy02['Período'], format='%m/%Y')

                # Calcula a economia total e a emissão de carbono evitada.
                economia_total, carbono_economia = calculate_total_savings_and_carbon_emissions(df_copy02, data_desejada, VALOR_KWH_CEMIG, VALOR_KWH_FATURADO)
               
                st.write(f'Total Economizado do começo dos dados ao mês selecionado: R$ {economia_total:.2f}')
                st.write(f'Total de Carbono não emitido do começo dos dados ao mês selecionado: {carbono_economia:.2f} kg')

                # Permite ao usuário selecionar ou digitar o nome do cliente.
                nomes_clientes = ['Gracie Barra BH', 'Cliente 2', 'Cliente 3']
                cliente_selecionado = st.selectbox("Selecione ou digite o nome do cliente:", nomes_clientes + ['Outro'])

                if cliente_selecionado == 'Outro':
                    cliente_text = st.text_input("Digite o nome do cliente:", value="", placeholder="Digite o nome do cliente aqui")
                else:
                    cliente_text = cliente_selecionado

                # Botão para confirmar o nome do cliente.
                if st.button('Confirmar Cliente'):
                    st.session_state.cliente_text = cliente_text
                    st.success('Cliente confirmado!')

                data_atual = datetime.now()
                data_desejada02 = st.date_input("Selecione a data desejada:", value=data_atual)

                # Botão para confirmar a data de upload.
                if st.button('Confirmar Data de Upload'):
                    st.session_state.data_desejada02 = data_desejada02
                    st.success('Data de upload confirmada!')

                # Calcular vencimento (7 dias após a data desejada)
                vencimento02 = (data_desejada02 + timedelta(days=7)).strftime("%d/%m/%Y")

                # Calcular o mês de referência como o mês anterior ao mês de data_desejada02
                mes_referencia = (data_desejada02.replace(day=1) - timedelta(days=1)).strftime("%m/%Y")

                # Gera a imagem com todos os dados processados e configurados
                if len(ultimo_periodo) > 5:
                    ultimo_periodo = ultimo_periodo[:5]
             
                    ultimo_periodo = datetime.strptime(ultimo_periodo, '%m/%y')
               

                # Processar o DataFrame preprocessed_df
                preprocessed_df = df_filtered2.copy()
                preprocessed_df.drop(['Transferido', 'Geração'], axis=1, inplace=True)
                preprocessed_df = preprocessed_df.query("Modalidade != 'Auto Consumo-Geradora'")

                # Arredondar os valores para uma casa decimal
                preprocessed_df = preprocessed_df.round(2)

                # Calcular o valor (R$) com base na seleção do usuário
                if st.session_state.calculo_tipo == 'Recebimento':
                    preprocessed_df['Valor (R$)'] = preprocessed_df['Recebimento'] * VALOR_KWH_FATURADO
                else:
                    preprocessed_df['Valor (R$)'] = preprocessed_df['Compensação'] * VALOR_KWH_FATURADO

                # Adicionar um multiselect para o usuário escolher as colunas a serem exibidas
                default_columns = ['Modalidade', 'Instalação', 'Período', 'Consumo', 'Compensação', 'Recebimento', 'Saldo Atual', 'Valor (R$)']
                selected_columns = st.multiselect("Selecione as colunas a serem exibidas:", default_columns, default=default_columns)

                # Verificar se alguma coluna foi selecionada
                if not selected_columns:
                    preprocessed_df_filtered = pd.DataFrame(columns=default_columns)
                else:
                    # Filtrar o DataFrame com as colunas selecionadas para exibição
                    preprocessed_df_filtered = preprocessed_df[selected_columns].copy()

                # Remover símbolos da coluna 'Valor (R$)' para somar
                preprocessed_df_filtered['Valor (R$)'] = preprocessed_df_filtered['Valor (R$)'].apply(lambda x: float(x.replace('R$', '').replace('.', '').replace(',', '.')) if isinstance(x, str) else x)

                # Adicionar linha de totais
                total_row = preprocessed_df_filtered.sum(numeric_only=True)
                total_row['Modalidade'] = 'Total'
                total_row['Valor (R$)'] = preprocessed_df_filtered['Valor (R$)'].sum()
                total_row['Valor (R$)'] = format_currency(total_row['Valor (R$)'])
                for col in preprocessed_df_filtered.select_dtypes(include=['object']).columns:
                    if col != 'Modalidade':
                        total_row[col] = ''  # Para as colunas de texto, preencher com strings vazias

                # Concatenar a linha de total ao DataFrame
                preprocessed_df_filtered = pd.concat([preprocessed_df_filtered, pd.DataFrame(total_row).T], ignore_index=True)

                # Formatar a coluna 'Valor (R$)' após a soma
                preprocessed_df_filtered['Valor (R$)'] = preprocessed_df_filtered['Valor (R$)'].apply(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)

                # Atualizar a chamada para a função que gera a imagem
                img = generate_image(preprocessed_df_filtered, monthly_data, selected_columns, default_columns, st.session_state.calculo_tipo, RECEBIDO, VALOR_A_PAGAR, VALOR_KWH_CEMIG, DESCONTO, VALOR_KWH_FATURADO, economia_total, carbono_economia, cliente_text, mes_referencia, vencimento02)

                st.image(img, caption="Imagem gerada")

                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(label="Baixar Imagem", data=buffer, file_name="imagem_processada.png", mime="image/png")

                # Carregar as imagens do QR Code e do código de barras
                qr_code_image_file = st.file_uploader("Upload Imagem QR Code", type=["png", "jpeg"])
                barcode_image_file = st.file_uploader("Upload Imagem Código de Barras", type=["png", "jpeg"])

                if qr_code_image_file and barcode_image_file:
                    qr_code_image = Image.open(qr_code_image_file)
                    barcode_image = Image.open(barcode_image_file)

                    # Redimensionar as imagens proporcionalmente para se ajustarem melhor ao boleto
                    proporcao_qr_code = 285 / max(qr_code_image.width, qr_code_image.height)
                    proporcao_codigo_barras = 1250 / max(barcode_image.width, barcode_image.height)

                    qr_code_image = qr_code_image.resize((int(qr_code_image.width * proporcao_qr_code), int(qr_code_image.height * proporcao_qr_code)))
                    barcode_image = barcode_image.resize((int(barcode_image.width * proporcao_codigo_barras), int(barcode_image.height * proporcao_codigo_barras)))

                    # Definir as novas posições onde os QR Code e o código de barras serão colados na imagem do boleto
                    posicao_x_qr_code = 1205
                    posicao_y_qr_code = 1200
                    posicao_x_codigo_barras = 225
                    posicao_y_codigo_barras = 1600

                    # Colar as imagens do QR Code e do código de barras na imagem do boleto
                    img.paste(qr_code_image, (posicao_x_qr_code, posicao_y_qr_code))
                    img.paste(barcode_image, (posicao_x_codigo_barras, posicao_y_codigo_barras))

                    # Salvar a imagem final com os QR Code e código de barras adicionados
                    img.save('boleto_com_qrcode01.png')

                    #Create buttons for image and PDF generation
                    generate_image_button = st.button("Gerar Imagem")
                    generate_pdf_button = st.button("Gerar PDF")

                    if generate_image_button:
                        st.image(img, caption='Imagem Gerada', use_column_width=True)
                    if generate_pdf_button:
                        # Gerar o PDF e exibir o link para download
                        pdf_output = generate_pdf(img)
                        st.download_button(label="Baixar PDF", data=pdf_output, file_name=f"{cliente_text}{VALOR_A_PAGAR}.pdf", mime="application/pdf")
