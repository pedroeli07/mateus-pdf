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
from image import generate_image

# Configura o título da aplicação Streamlit.
st.title("Processamento de Dados de Energia")

# Carrega os dados através de uma função personalizada.
df = load_data()

# Verifica se o DataFrame não está vazio e contém as colunas específicas.
if not df.empty:
    if 'Período' and 'Modalidade' in df.columns:
        # Permite ao usuário selecionar um período e a modalidade (loja) a partir de listas drop-down.
        available_dates = df['Período'].unique()
        data_desejada = st.selectbox("Selecione a data desejada:", available_dates, index=0, key="data_desejada_selectbox")
        available_inst = df['Modalidade'].unique()
        numero_instalacao = st.multiselect("Selecione a loja desejada:", available_inst, key="modalidade_selectbox")

    # Se a instalação e a data desejadas forem selecionadas, filtra o DataFrame com base nesses parâmetros.
    if numero_instalacao and data_desejada is not None:
        df_filtered2 = df[(df['Período'] == data_desejada) & (df['Modalidade'].isin(numero_instalacao))]

        # Filtra adicionalmente onde a coluna 'Geração' é diferente de zero e calcula a soma.
        if not df_filtered2.empty:
            df_filtered2 = df_filtered2[df_filtered2['Geração'] != 0]
            RECEBIDO = int(df_filtered2['Geração'].sum())

        # Botão para confirmar seleção de período e lojas, armazena seleção em sessão.
        if st.button('Confirmar Período e Lojas'):
            st.session_state.data_desejada = data_desejada
            st.session_state.numero_instalacao = numero_instalacao
            st.success('Período e lojas confirmados!')
        
        # Exibe os dados confirmados.
        if 'numero_instalacao' in st.session_state and 'data_desejada' in st.session_state:
            st.write(f"Período Referência selecionado: {st.session_state.data_desejada}")
            st.write(f"Lojas desejadas: {st.session_state.numero_instalacao}")
            st.write(f"RECEBIDO: {RECEBIDO} kWh")       
        
        # Se o período e a instalação foram confirmados, permite ao usuário ajustar os valores de KWh e desconto.
        if 'data_desejada' in st.session_state and 'numero_instalacao' in st.session_state:
            # Utiliza sliders e inputs para permitir ajustes nos valores de kWh da Cemig e percentual de desconto.
            VALOR_KWH_CEMIG= st.slider("Digite o valor do KWh da Cemig (R$):", min_value=0.1000, max_value=2.00, value=0.956, step=0.001, format="%.3f")
            VALOR_KWH_CEMIG = st.number_input("Digite o valor do KWh da Cemig (R$):", min_value=0.1000, max_value=2.00, value=VALOR_KWH_CEMIG, step=0.001, format="%.3f")
            DESCONTO  = st.slider("Digite o valor do desconto (%):", min_value=0, max_value=100, value=20, step=1)
            DESCONTO  = st.number_input("Digite o valor do desconto (%):", min_value=0, max_value=100, value=DESCONTO, step=1)

            # Botão para confirmar valores ajustados.
            if st.button('Confirmar Valores'):
                VALOR_KWH_CEMIG = VALOR_KWH_CEMIG
                DESCONTO = DESCONTO
            # Calcula o valor faturado com base no desconto.
            VALOR_KWH_FATURADO = VALOR_KWH_CEMIG - ((VALOR_KWH_CEMIG * DESCONTO) / 100)
            VALOR_KWH_FATURADO = round(VALOR_KWH_FATURADO, 3)
            VALOR_KWH_FATURADO = VALOR_KWH_FATURADO
            st.success('Valores confirmados!') 
            
            # Exibe os valores ajustados e calculados.
            st.write(f"Valor KWh Cemig confirmado: R${VALOR_KWH_CEMIG}")
            st.write(f"Desconto confirmado: {DESCONTO}%")
            st.write(f"Valor KWh faturado confirmado: R${VALOR_KWH_FATURADO}")

            # Calcula o valor a pagar com base na geração e no valor kWh faturado.
            VALOR_A_PAGAR = RECEBIDO * VALOR_KWH_FATURADO
            VALOR_A_PAGAR = round(VALOR_A_PAGAR, 2)
        
            st.write(f"Recebido: {(RECEBIDO)} kWH ")
            st.write(f"Valor a Pagar: R$ {VALOR_A_PAGAR}")

            # Processa os dados para o último mês e calcula o consumo e a geração mensal.
            df_last_month, ultimo_periodo = process_data(df, st.session_state.data_desejada, st.session_state.numero_instalacao)
        
            st.write("Dados do último mês processados:")
            st.dataframe(df_last_month)
            
            df_copy = df.copy()
            
            monthly_data = calculate_consumption_generation(df_copy)
            st.write("Consumo e geração mensal:")
            st.dataframe(monthly_data)
            
            df_copy02 = df.copy()
            df_copy02['Período'] = pd.to_datetime(df_copy02['Período'], format='%m/%Y')
            
            # Calcula a economia total e a emissão de carbono evitada.
            economia_total, carbono_economia = calculate_total_savings_and_carbon_emissions(df_copy02, data_desejada, VALOR_KWH_CEMIG, VALOR_KWH_FATURADO)
            
            st.write("Dados filtrados até a data selecionada:")
            st.dataframe(df_copy02[df_copy02['Período'] <= data_desejada])  # Mostra o DataFrame filtrado
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
                st.success('Cliente confirmado!')
            
            mes_referencia = data_desejada02.strftime("%m/%Y")

            vencimento02 = (data_desejada02 + timedelta(days=7)).strftime("%d/%m/%Y")

            # Gera a imagem com todos os dados processados e configurados.
            if len(ultimo_periodo) > 5:  
                ultimo_periodo = ultimo_periodo[:5]  
                ultimo_periodo = datetime.strptime(ultimo_periodo, '%m/%y')
                
            img = generate_image(df_last_month, monthly_data, RECEBIDO, VALOR_A_PAGAR, VALOR_KWH_CEMIG, DESCONTO, VALOR_KWH_FATURADO, economia_total, carbono_economia,  cliente_text, mes_referencia, vencimento02)

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
