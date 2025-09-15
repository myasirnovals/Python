import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        print(f'Total number of pages: {num_pages}')

        page_obj = pdf_reader.pages[0]
        texts = page_obj.extract_text()
        print(texts)

file_path = 'sample.pdf'
extract_text_from_pdf(file_path)