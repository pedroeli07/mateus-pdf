from io import BytesIO
from fpdf import FPDF
import tempfile

def generate_pdf(image):
    # Definir dimensões do PDF (8.28 x 11.69 inches em pontos)
    pdf = FPDF(unit='pt', format=[598.56, 845.28])
    pdf.add_page()
    
    # Cria um arquivo temporário para salvar a imagem
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        image.save(tmpfile, format='PNG')
        tmpfile_path = tmpfile.name

    # Adiciona a imagem ao PDF, ajustando ao tamanho da página
    pdf.image(tmpfile_path, x=0, y=0, w=598.56, h=845.28)

    # Prepara o PDF para ser retornado como um objeto BytesIO
    pdf_output = BytesIO()
   # pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf.output(dest='S').encode('latin1')) # Gera o PDF e o codifica em latin1
    pdf_output.seek(0) # Reposiciona o cursor no início do BytesIO


    return pdf_output


