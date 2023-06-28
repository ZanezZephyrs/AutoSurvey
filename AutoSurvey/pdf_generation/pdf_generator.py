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
    def generate_pdf(sections_data, output_file="file.pdf", pdf_options=options, with_subsections=False):
        if with_subsections:
            html=PDFGenerator.to_basic_html_with_subsections(sections_data)
        else:
            html=PDFGenerator.to_basic_html(sections_data)
        with open("file.html", "w") as fout:
            fout.write(html)

        pdfkit.from_file("file.html", output_file,options=pdf_options)        

    @staticmethod
    def to_basic_html(sections_data):
        theme=list(sections_data.keys())[0]
        html="<html>\n"
        html+=f"<h1>{theme}</h1>\n"

        sections=list(sections_data[theme].keys())
        for section in sections:
            html+=f"<h2>{section}</h2>\n"

            html+=f"<p>{sections_data[theme][section]['content']}</p>\n"

        html+="</html>"
        return html
    
    @staticmethod
    def to_basic_html_with_subsections(sections_data):
        theme=list(sections_data.keys())[0]

        html="<html>\n"
        html+=f"<h1>{theme}</h1>\n"

        bib="<h2>References</h2>\n"

        current_section=1
        sections=list(sections_data[theme].keys())
        for section in sections:
            html+=f"<h2> {current_section} - {section}</h2>\n"

            section_obj=sections_data[theme][section]
            if "content" in section_obj:
                content=sections_data[theme][section]['content'].replace('\n', '<br/> &emsp;')
                html+=f"<p> &emsp; {content}</p>\n"


            if "references" in section_obj:
                for i,reference in enumerate(sections_data[theme][section]["references"]):
                    bib+=f"<p> [{i+1}]-{reference}</p>\n"

            if "subsections" in section_obj:
                for subsection_number,subsection in enumerate(sections_data[theme][section]["subsections"]):
                    html+=f"<h3>{current_section}.{subsection_number+1} - {subsection}</h3>\n"
                    subsection_obj=sections_data[theme][section]["subsections"][subsection]
                    content=subsection_obj['content'].replace('\n', '<br/> &emsp;')

                    html+=f"<p> &emsp; {content}</p>\n"
                    if "references" in subsection_obj:
                        for i,reference in enumerate(sections_data[theme][section]["subsections"][subsection]["references"]):
                            bib+=f"<p> [{i+1}]-{reference}</p>\n" 

            current_section+=1           


        html+=bib

        html+="</html>"
        return html
    
    
    
