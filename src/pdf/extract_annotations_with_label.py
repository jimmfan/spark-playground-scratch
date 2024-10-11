import fitz  # PyMuPDF

def extract_and_map_labels_to_closest_rectangles(pdf_bytes):
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
        assigned_rectangles = set()  # To track assigned rectangles
        
        # Iterate through all annotations on the page
        for annot in page.annots():
            annot_type = annot.type[0]
            
            if annot_type == 2:  # FreeText (label)
                labels.append((annot, annot.rect))
            elif annot_type == 4:  # Square/Rectangle
                rectangles.append((annot, annot.rect))
        
        # Map each label to the closest available rectangle
        for label, label_rect in labels:
            closest_rectangle = None
            min_distance = float('inf')

            # Find the closest unassigned rectangle for each label
            for idx, (rectangle, rect) in enumerate(rectangles):
                if idx in assigned_rectangles:
                    continue  # Skip rectangles that have already been assigned
                
                # Calculate the center-to-center distance between the label and the rectangle
                label_center = (label_rect.x0 + label_rect.x1) / 2, (label_rect.y0 + label_rect.y1) / 2
                rect_center = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
                distance = ((label_center[0] - rect_center[0]) ** 2 + (label_center[1] - rect_center[1]) ** 2) ** 0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_rectangle = (idx, rect)

            if closest_rectangle:
                idx, closest_rect = closest_rectangle
                # Mark the rectangle as assigned
                assigned_rectangles.add(idx)

                # Extract text from the closest rectangle
                text_inside_rect = page.get_text("text", clip=closest_rect).strip()
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

mapped_labels = extract_and_map_labels_to_closest_rectangles(pdf_bytes)
