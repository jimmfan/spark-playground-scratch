import fitz  # PyMuPDF

def extract_and_map_labels_to_rectangles(pdf_bytes):
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
        
        # For each rectangle, find all FreeText labels that are close to it
        for rectangle, rect in rectangles:
            # List to store all labels that will map to this rectangle
            labels_for_this_rectangle = []
            
            for label, label_rect in labels:
                # Check if the label is horizontally or vertically aligned with the rectangle
                if (abs(label_rect.y0 - rect.y0) <= 10 or abs(label_rect.y1 - rect.y1) <= 10 or
                    abs(label_rect.x0 - rect.x0) <= 10 or abs(label_rect.x1 - rect.x1) <= 10):
                    
                    # If aligned, add it to the list for this rectangle
                    labels_for_this_rectangle.append((label, label_rect))
            
            # If there are labels mapped to this rectangle, extract the text and associate them
            if labels_for_this_rectangle:
                text_inside_rect = page.get_text("text", clip=rect).strip()

                for label, label_rect in labels_for_this_rectangle:
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
