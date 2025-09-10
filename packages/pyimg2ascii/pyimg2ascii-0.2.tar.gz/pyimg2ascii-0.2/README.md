# pyimg2asciii  

Convert images into ASCII art with a simple Python library.  

---

##  Installation  

```bash
pip install pyimg2asciii
```

---

##  Usage  

### Example 1: Print ASCII art in terminal
```python
from pyimg2asciii import convert_image_to_ascii

# Convert image to ASCII
ascii_art = convert_image_to_ascii("input.jpg", new_width=80)

# Print result
print(ascii_art)
```

---

### Example 2: Save ASCII art to file
```python
from pyimg2asciii import convert_image_to_ascii

ascii_art = convert_image_to_ascii("input.jpg", new_width=100)

with open("ascii_output.txt", "w") as f:
    f.write(ascii_art)
```

---

##  Parameters  

- **`image_path`** *(str)* → Path to input image.  
- **`new_width`** *(int, optional)* → Width of ASCII art (default: 100).  

---

##  Example Output  

If you run the library on an image, you’ll get ASCII art like:  

```
@@@@@@@@@@%%%%###****
@@@@@@%%%%####***+++
@@@%%%####***++++=--
```

---

##  License  

MIT License © 2025  

Created by D.Abhiram