import fitz  # PyMuPDF

ANNOTATION_TYPES = {
    0: "Text",
    1: "Link",
    2: "FreeText",
    3: "Line",
    4: "Square",
    5: "Circle",
    6: "Polygon",
    7: "Polyline",
    8: "Highlight",
    9: "Underline",
    10: "Squiggly",
    11: "StrikeOut",
    12: "Stamp",
    13: "Caret",
    14: "Ink",
    15: "Popup",
    16: "FileAttachment",
    17: "Sound",
    18: "Movie",
    19: "Widget",
    20: "Screen",
    21: "PrinterMark",
    22: "TrapNet",
    23: "Watermark",
    24: "3D"
}

def extract_annotations(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_info = {
                "page": page_number,
                "type": annot.type[0],  # Annotation type (e.g., text, highlight, etc.)
                "rect": annot.rect,  # The rectangle where the annotation is located
                "content": annot.info.get("content", ""),  # Any text content associated with the annotation
                "author": annot.info.get("title", "Unknown"),  # Author of the annotation if available
            }
            
            print(f"Annotation found on page {page_number}: {annot_info}")

    doc.close()

# Example usage
with open("financial_document.pdf", "rb") as file:
    pdf_bytes = file.read()

extract_annotations(pdf_bytes)