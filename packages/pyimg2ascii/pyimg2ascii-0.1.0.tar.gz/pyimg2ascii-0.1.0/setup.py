from setuptools import setup, find_packages

setup(
    name="pyimg2ascii",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pillow"],
    description="Convert images to ASCII art",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourname/image2ascii",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
