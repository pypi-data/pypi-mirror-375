# image2ascii

Convert images into ASCII art 🎨➡️🔤

## Installation
```bash
pip install image2ascii
```

## Usage
```python
from image2ascii import convert_image_to_ascii

ascii_art = convert_image_to_ascii("input.jpg", new_width=80)
print(ascii_art)

with open("output.txt", "w") as f:
    f.write(ascii_art)
```
