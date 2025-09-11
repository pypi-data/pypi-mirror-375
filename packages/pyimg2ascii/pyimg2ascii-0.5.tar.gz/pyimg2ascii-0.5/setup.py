from setuptools import setup, find_packages
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="pyimg2ascii",
    version="0.5",
    packages=find_packages(),
    install_requires=["pillow"],
    description="Convert images to ASCII art",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    author="Devulapalli Abhiram",
    author_email="abhiramdevulapalli8@gmail.com",
    url="https://github.com/abhirammdh/pyimg2ascii",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
