from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from all pages of a PDF.
    """

    reader = PdfReader(file_path)

    extracted_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text.append(text)

    return "\n".join(extracted_text).strip()