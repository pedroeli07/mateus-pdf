# **Processamento de Dados de Energia**

## **Descrição do Projeto**
Este projeto foi desenvolvido usando **Streamlit**, uma aplicação interativa que permite aos usuários carregar, processar, visualizar e exportar dados de energia. O sistema é capaz de calcular o consumo e a geração de energia, estimar economias financeiras e reduções de emissões de carbono, e produzir relatórios dinâmicos em forma de imagens e PDFs.

## **Funcionalidades**
- **Carregamento de Dados:** Suporte para carregar dados de energia através de arquivos CSV ou XLSX.
- **Filtragem de Dados:** Filtragem por período e modalidade específicos.
- **Cálculo de Consumo e Geração:** Cálculos detalhados de energia consumida e gerada.
- **Cálculo de Economia e Emissões de Carbono:** Calcula economias financeiras e redução de emissões de CO2.
- **Geração de Relatórios:** Produção de imagens detalhadas e PDFs para apresentação ou arquivo.

## **Tecnologias Utilizadas**
- **Python:** Linguagem de programação principal.
- **Pandas:** Para manipulação de dados.
- **Streamlit:** Para construção da interface do usuário.
- **Pillow (PIL):** Para manipulação de imagens.
- **FPDF:** Para geração de documentos em PDF.

## **Estrutura de Diretórios**


/mateus-pdf/
│
├── main.py                 # Arquivo principal do Streamlit
├── process_data.py         # Funções para processamento dos dados
├── savings_carbon.py       # Cálculos de economia e carbono
├── consumo.py              # Cálculos de consumo e geração de energia
├── create_pdf.py           # Geração de PDF
├── load_data.py            # Carregamento de dados
└── image.py                # Geração de imagens

## **Instalação e Execução**
Para instalar e executar o projeto:
1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/seuusuario/projeto-energia.git
   cd mateus-pdf

## **Instale as Dependências:**
```plaintext
pip install -r requirements.txt
'''
## **Execute a Aplicação:**
streamlit run main.py


## **Adicionando Novos Clientes e Instalações:**
Para adicionar novos clientes ao sistema:

Atualize o Código:
Em load_data.py, atualize o dicionário modalidade_map com o número de instalação e o nome correspondente do novo cliente.
Adicione o nome do novo cliente na lista nomes_clientes em app.py.
Carregue Novos Dados:
Use o st.file_uploader em load_data.py para carregar os dados do novo cliente em formato CSV ou XLSX.
