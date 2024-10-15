import fitz  # PyMuPDF

def extract_and_map_labels_to_rectangles(pdf_bytes):
    # Open the PDF from the byte array
    doc = fitz.open("pdf", pdf_bytes)
    
    # Dictionary to store the mapped labels and texts
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
        
        # Map each label to the closest rectangle
        for label, label_rect in labels:
            closest_rectangle = None
            min_distance = float('inf')
            text_inside_rect = ""

            for rectangle, rect in rectangles:
                # Calculate the distance if the label is horizontally or vertically aligned
                if (abs(label_rect.y0 - rect.y0) <= 10 or abs(label_rect.y1 - rect.y1) <= 10 or
                    abs(label_rect.x0 - rect.x0) <= 10 or abs(label_rect.x1 - rect.x1) <= 10):
                    
                    # Calculate the center-to-center distance between the label and the rectangle
                    label_center = (label_rect.x0 + label_rect.x1) / 2, (label_rect.y0 + label_rect.y1) / 2
                    rect_center = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
                    distance = ((label_center[0] - rect_center[0]) ** 2 + (label_center[1] - rect_center[1]) ** 2) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_rectangle = rect

            if closest_rectangle:
                # Extract text from the closest rectangle
                text_inside_rect = page.get_text("text", clip=closest_rectangle).strip()
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

mapped_labels = extract_and_map_labels_to_rectangles(pdf_bytes)
