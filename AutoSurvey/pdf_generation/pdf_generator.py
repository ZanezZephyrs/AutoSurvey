import pdfkit

options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'cookie': [
        ('cookie-empty-value', '""'),
        ('cookie-name1', 'cookie-value1'),
        ('cookie-name2', 'cookie-value2'),
    ],
    'no-outline': None
}

class PDFGenerator():
    
    @staticmethod
    def generate_pdf( theme, sections_data, output_file="file.pdf", pdf_options=options):
        html=PDFGenerator.to_basic_html(theme, sections_data)
        with open("file.html", "w") as fout:
            fout.write(html)

        pdfkit.from_file("file.html", output_file,options=pdf_options)        

    @staticmethod
    def to_basic_html(theme, sections_data):
        html="<html>\n"
        html+=f"<h1>{theme}</h1>\n"

        sections=list(sections_data[theme].keys())
        for section in sections:
            html+=f"<h2>{section}</h2>\n"

            html+=f"<p>{sections_data[theme][section]['content']}</p>\n"

        html+="</html>"
        return html