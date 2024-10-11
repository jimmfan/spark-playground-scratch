import fitz  # PyMuPDF

def extract_text_and_map_labels(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Dictionary to store rectangle text mapped to label text
    annotation_map = {}

    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Extract all text on the page and split into words with their bounding boxes
        words = page.get_text("words")  # returns (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_type = annot.type[0]
            # Check if the annotation is a square or rectangle (type 4: Square)
            if annot_type == 4:  # 'Square'
                # Get the rectangle of the annotation
                annot_rect = annot.rect
                
                # Extract the text within this rectangle
                inside_text = page.get_text("text", clip=annot_rect).strip()
                
                # Find potential label text outside the rectangle, horizontally or vertically aligned
                label_text = None
                min_distance = float('inf')  # To find the closest label
                
                for word in words:
                    word_rect = fitz.Rect(word[0], word[1], word[2], word[3])
                    word_text = word[4]
                    
                    # Check horizontal alignment (same y-axis range, next to the rectangle)
                    if annot_rect.y0 <= word_rect.y0 <= annot_rect.y1 or annot_rect.y0 <= word_rect.y1 <= annot_rect.y1:
                        # If the label is on the left or right of the rectangle
                        if word_rect.x1 < annot_rect.x0 or word_rect.x0 > annot_rect.x1:
                            distance = min(abs(word_rect.x1 - annot_rect.x0), abs(word_rect.x0 - annot_rect.x1))
                            if distance < min_distance:
                                min_distance = distance
                                label_text = word_text

                    # Check vertical alignment (same x-axis range, above or below the rectangle)
                    if annot_rect.x0 <= word_rect.x0 <= annot_rect.x1 or annot_rect.x0 <= word_rect.x1 <= annot_rect.x1:
                        # If the label is above or below the rectangle
                        if word_rect.y1 < annot_rect.y0 or word_rect.y0 > annot_rect.y1:
                            distance = min(abs(word_rect.y1 - annot_rect.y0), abs(word_rect.y0 - annot_rect.y1))
                            if distance < min_distance:
                                min_distance = distance
                                label_text = word_text

                # Store the annotation text and its associated label
                if inside_text and label_text:
                    annotation_map[label_text] = inside_text
                    print(f"Page {page_number}: Label '{label_text}' mapped to text inside rectangle: '{inside_text}'")

    doc.close()
    return annotation_map

# Example usage
with open("financial_document.pdf", "rb") as file:
    pdf_bytes = file.read()

annotation_map = extract_text_and_map_labels(pdf_bytes)
print("Annotation Map:", annotation_map)
