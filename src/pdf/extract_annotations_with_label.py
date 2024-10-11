import fitz  # PyMuPDF

def extract_and_map_label_to_rectangle(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Dictionary to store the mapped labels and texts
    mapped_labels = []

    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Collect all FreeText annotations and Square annotations
        free_text_annots = []
        square_annots = []

        for annot in page.annots():
            annot_type = annot.type[0]
            
            if annot_type == 2:  # FreeText annotation (label)
                free_text_annots.append(annot)
            elif annot_type == 4:  # Square annotation
                square_annots.append(annot)
        
        # Map labels to rectangles based on proximity
        for square_annot in square_annots:
            square_rect = square_annot.rect
            
            # Extract text inside the square annotation
            text_inside_rect = page.get_text("text", clip=square_rect).strip()
            
            closest_label = None
            min_distance = float("inf")
            
            for label_annot in free_text_annots:
                label_rect = label_annot.rect
                label_text = label_annot.info.get("content", "").strip()
                
                # Calculate the distance between the center of the label and the square
                label_center = label_rect.tl + (label_rect.width / 2, label_rect.height / 2)
                square_center = square_rect.tl + (square_rect.width / 2, square_rect.height / 2)
                
                # Compute the Euclidean distance between the centers
                distance = ((label_center[0] - square_center[0]) ** 2 + (label_center[1] - square_center[1]) ** 2) ** 0.5
                
                # Check if this is the closest label
                if distance < min_distance:
                    min_distance = distance
                    closest_label = label_text
            
            if closest_label:
                mapped_labels.append({
                    "label": closest_label,
                    "text_inside_rect": text_inside_rect,
                    "page_number": page_number
                })
                print(f"Mapped Label: '{closest_label}' with Text: '{text_inside_rect}' on Page {page_number}")

    doc.close()
    return mapped_labels

# Example usage
with open("doc.pdf", "rb") as file:
    pdf_bytes = file.read()

mapped_labels = extract_and_map_label_to_rectangle(pdf_bytes)
