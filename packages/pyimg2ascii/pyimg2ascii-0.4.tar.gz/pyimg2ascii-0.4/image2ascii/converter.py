from PIL import Image

ASCII_CHARS = "@%#*+=-:. "

def convert_image_to_ascii(path, new_width=100):
    """Convert an image file to ASCII art string."""
    try:
        image = Image.open(path)
    except:
        raise ValueError("❌ Cannot open image file")

    # Resize
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # adjust ratio
    image = image.resize((new_width, new_height))

    # Convert to grayscale
    image = image.convert("L")

    # Map pixels to ASCII chars
    pixels = image.getdata()
    chars = "".join([ASCII_CHARS[min(pixel // 25, len(ASCII_CHARS)-1)] for pixel in pixels])


    # Format ASCII string
    ascii_img = "\n".join(
        [chars[i:i+new_width] for i in range(0, len(chars), new_width)]
    )
    return ascii_img
