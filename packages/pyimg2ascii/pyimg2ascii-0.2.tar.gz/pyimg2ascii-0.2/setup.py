from setuptools import setup, find_packages

setup(
    name="pyimg2ascii",
    version="0.2",
    packages=find_packages(),
    install_requires=["pillow"],
    description="Convert images to ASCII art",
    author="D.Abhiram",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="abhiramdevulapalli8@gmail.com",
    url="https://github.com/abhirammdh/pyimg2ascii",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
