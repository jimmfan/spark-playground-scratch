import fitz  # PyMuPDF

def extract_and_map_labels_to_unique_rectangles(pdf_bytes):
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
        assigned_labels = set()  # To track assigned labels
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_type = annot.type[0]
            
            if annot_type == 2:  # FreeText (label)
                labels.append((annot, annot.rect))
            elif annot_type == 4:  # Square/Rectangle
                rectangles.append((annot, annot.rect))
        
        # For each rectangle, find the closest label that has not been assigned yet
        for rect_index, (rectangle, rect) in enumerate(rectangles):
            closest_label = None
            min_distance = float('inf')

            for label_index, (label, label_rect) in enumerate(labels):
                if label_index in assigned_labels:
                    continue  # Skip labels that have already been assigned
                
                # Calculate the center-to-center distance between the label and the rectangle
                label_center = (label_rect.x0 + label_rect.x1) / 2, (label_rect.y0 + label_rect.y1) / 2
                rect_center = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
                distance = ((label_center[0] - rect_center[0]) ** 2 + (label_center[1] - rect_center[1]) ** 2) ** 0.5
                
                # Update the closest label if the current one is closer
                if distance < min_distance:
                    min_distance = distance
                    closest_label = (label_index, label, label_rect)

            if closest_label:
                label_index, label, label_rect = closest_label
                # Mark the label as assigned
                assigned_labels.add(label_index)

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

mapped_labels = extract_and_map_labels_to_unique_rectangles(pdf_bytes)
