import json
import re
import pdfplumber


def is_symbol(text):
    # Check if text is a symbol
    return re.match(r"^[^a-zA-Z0-9]+$", text) is not None


def extract_sections(pdf_path, title_size: int = 16, skip_first_page: bool = True):
    with pdfplumber.open(pdf_path) as pdf:
        sections = []
        current_section = {"title": "", "content": ""}
        getting_section_title = False
        for page_number, page in enumerate(pdf.pages):
            if page_number == 0 and skip_first_page:
                continue
            for element in page.extract_words(extra_attrs=["size"], x_tolerance=1):
                element["text"] = element["text"].encode("utf-8").decode("utf-8")
                if element["size"] >= title_size:
                    if getting_section_title:
                        if not is_symbol(element["text"]):
                            current_section["title"] = current_section["title"] + " " + element["text"]
                    else:
                        if current_section["content"] != "":
                            sections.append(current_section)
                            current_section = {"title": "", "content": ""}
                        getting_section_title = True
                        if not is_symbol(element["text"]):
                            current_section["title"] = element["text"]
                else:
                    getting_section_title = False
                    current_section["content"] = current_section["content"] + " " + element["text"]
        if current_section["content"] != "":
            sections.append(current_section)
    return sections


def get_pdf_content(pdf_path, output_path, title_size: int = 16, skip_first_page: bool = True):
    sections = extract_sections(pdf_path, title_size, skip_first_page)
    parsed_sections = []
    for section in sections:
        if section["title"].strip() != "":
            parsed_sections.append(section)
        elif len(parsed_sections) > 0:
            parsed_sections[-1]["content"] = parsed_sections[-1]["content"] + "\n" + section["content"]
        else:
            parsed_sections.append(section)
    with open(output_path, "w", encoding="utf-8") as fout:
        json.dump(parsed_sections, fout, ensure_ascii=True, indent=4)

# Example usage
pdf_path = ""
get_pdf_content(pdf_path, "output.json", title_size=16, skip_first_page=False)