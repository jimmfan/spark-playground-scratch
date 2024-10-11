import fitz  # PyMuPDF

def extract_and_map_rectangles_to_labels(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # List to store the mapped labels and texts
    mapped_labels = []

    # Iterate over each page
    for page_number in range(len(doc)):
        page = doc[page_number]
        
        # Lists to store FreeText (labels) and Rectangle annotations
        labels = []
        rectangles = []
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_type = annot.type[0]
            
            if annot_type == 2:  # FreeText (label)
                labels.append((annot, annot.rect))
            elif annot_type == 4:  # Square/Rectangle
                rectangles.append((annot, annot.rect))
        
        # For each rectangle, find the closest label(s)
        for rect_index, (rectangle, rect) in enumerate(rectangles):
            # List to store labels that are close to this rectangle
            closest_labels = []

            for label, label_rect in labels:
                # Calculate the center-to-center distance between the label and the rectangle
                label_center = (label_rect.x0 + label_rect.x1) / 2, (label_rect.y0 + label_rect.y1) / 2
                rect_center = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
                distance = ((label_center[0] - rect_center[0]) ** 2 + (label_center[1] - rect_center[1]) ** 2) ** 0.5
                
                # Check if the label is horizontally or vertically aligned with the rectangle within a margin
                if (abs(label_rect.y0 - rect.y0) <= 10 or abs(label_rect.y1 - rect.y1) <= 10 or
                    abs(label_rect.x0 - rect.x0) <= 10 or abs(label_rect.x1 - rect.x1) <= 10):
                    closest_labels.append((distance, label, label_rect))
            
            # If there are any labels associated with this rectangle, select the closest one
            if closest_labels:
                # Sort labels by distance and pick the closest one
                closest_labels.sort(key=lambda x: x[0])  # Sort by distance
                for _, label, label_rect in closest_labels:
                    # Extract text from the rectangle
                    text_inside_rect = page.get_text("text", clip=rect).strip()
                    label_text = label.info.get("content", "No Label Content")

                    mapped_labels.append({
                        "label": label_text,
                        "text_inside_rect": text_inside_rect,
                        "page_number": page_number
                    })

                    print(f"Label: '{label_text}' mapped to Text: '{text_inside_rect}' on Page {page_number}")
    
    doc.close()
    return mapped_labels

# Example usage
with open("doc.pdf", "rb") as file:
    pdf_bytes = file.read()

mapped_labels = extract_and_map_rectangles_to_labels(pdf_bytes)
