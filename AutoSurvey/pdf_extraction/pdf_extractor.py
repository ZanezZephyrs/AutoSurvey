import fitz


def get_windows(input_text: str, window_size: int = 150, stride: int = 75):
    words = input_text.split()
    windows = []
    for i in range(0, len(words), stride):
        prefix = "..." if i != 0 else ""
        window_words = words[i : i + window_size]
        windows.append(prefix + " ".join(window_words))
        if window_size > len(window_words):
            break
    return windows

def get_pdf_windows(pdf_path: str, window_size: int = 150, stride: int = 75):
    pdf_doc = fitz.open(pdf_path)
    num_pages = pdf_doc.page_count
    content = ""
    for page_num in range(num_pages):
        page = pdf_doc.load_page(page_num)
        text = page.get_text()
        content += text + "\n"
    windows = get_windows(content, window_size, stride)
    return windows