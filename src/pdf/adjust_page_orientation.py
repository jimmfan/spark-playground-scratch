# Get the page's rotation
rotation = page.rotation  # This gives 0, 90, 180, or 270

# Iterate through annotations and adjust the rect based on rotation
adjusted_rects = []
for annot in page.annots():
    if annot.type[0] == 4:
        annot_rect = annot.rect
        
        if rotation == 90:
            # Rotate the rectangle coordinates for a 90-degree rotated page
            adjusted_rect = fitz.Rect(
                page.rect.width - annot_rect.y1,  # new x0
                annot_rect.x0,                   # new y0
                page.rect.width - annot_rect.y0, # new x1
                annot_rect.x1                    # new y1
            )
        elif rotation == 180:
            # Rotate the rectangle coordinates for a 180-degree rotated page
            adjusted_rect = fitz.Rect(
                page.rect.width - annot_rect.x1,  # new x0
                page.rect.height - annot_rect.y1, # new y0
                page.rect.width - annot_rect.x0,  # new x1
                page.rect.height - annot_rect.y0  # new y1
            )
        elif rotation == 270:
            # Rotate the rectangle coordinates for a 270-degree rotated page
            adjusted_rect = fitz.Rect(
                annot_rect.y0,                   # new x0
                page.rect.height - annot_rect.x1, # new y0
                annot_rect.y1,                   # new x1
                page.rect.height - annot_rect.x0  # new y1
            )
        else:
            # No rotation; use the rect as is
            adjusted_rect = annot_rect
        
        adjusted_rects.append(adjusted_rect)

# Now use the adjusted rectangles for further processing
for rect in adjusted_rects:
    pix = page.get_pixmap(dpi=300, annots=False, clip=rect, alpha=False)
    # Continue with your processing here
