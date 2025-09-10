def slice_slides(content: str) -> list[str]:
    """Slice a markdown document into slides separated by --- markers."""
    if not content.strip():
        return ["No content available"]
    
    # Split by slide separators (---)
    slides = content.split("---")
    
    # Clean up each slide
    cleaned_slides = []
    for slide in slides:
        slide = slide.strip()
        if slide:  # Only add non-empty slides
            cleaned_slides.append(slide)
    
    # If no slides were found (no --- separators), treat entire content as one slide
    if not cleaned_slides:
        cleaned_slides = [content.strip()]
    
    return cleaned_slides


def validate_slide_content(content: str) -> bool:
    """Validate that slide content is properly formatted."""
    return bool(content.strip())


def get_slide_count(content: str) -> int:
    """Get the number of slides in the content."""
    return len(slice_slides(content))

