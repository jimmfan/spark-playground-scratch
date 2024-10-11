import fitz  # PyMuPDF

def extract_and_map_text_with_labels(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Dictionary to store the mapped labels and texts
    mapped_labels = []

    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_type = annot.type[0]
            
            # Check if the annotation is a FreeText (value 2)
            if annot_type == 2:
                # Get the rectangle of the annotation
                annot_rect = annot.rect
                
                # Extract the text within the annotation rectangle
                text_inside_rect = page.get_text("text", clip=annot_rect).strip()
                
                # Find nearby text that might serve as a label
                words = page.get_text("words")  # Get all words on the page
                possible_labels = []
                
                # Iterate through all words to find nearby labels
                for word in words:
                    x0, y0, x1, y1, word_text = word[:5]
                    word_rect = fitz.Rect(x0, y0, x1, y1)
                    
                    # Check if the word is close horizontally or vertically to the annotation rectangle
                    if (word_rect.y1 <= annot_rect.y1 + 10 and word_rect.y0 >= annot_rect.y0 - 10) or \
                       (word_rect.x1 <= annot_rect.x1 + 10 and word_rect.x0 >= annot_rect.x0 - 10):
                        # Add the nearby word as a possible label
                        possible_labels.append((word_text, word_rect))
                
                # Choose the closest label based on distance
                if possible_labels:
                    # Sort labels by proximity to the annotation rectangle
                    closest_label = min(possible_labels, key=lambda label: annot_rect.distance_to(label[1]))
                    mapped_labels.append({
                        "label": closest_label[0],
                        "text_inside_rect": text_inside_rect,
                        "page_number": page_number
                    })
                    print(f"Mapped Label: '{closest_label[0]}' with Text: '{text_inside_rect}' on Page {page_number}")
    
    doc.close()
    return mapped_labels

# Example usage
with open("financial_document.pdf", "rb") as file:
    pdf_bytes = file.read()

mapped_labels = extract_and_map_text_with_labels(pdf_bytes)
