from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read version from __init__.py
with open(os.path.join("resumeio_dl", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="resumeio-dl",
    version=version,
    description="Download resumes from resume.io as PDF files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Noreddine",
    author_email="your.email@example.com",  # Replace with your email
    url="https://github.com/yourusername/resumeio-dl",  # Replace with your GitHub repo
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
        "pytesseract>=0.3.9",
        "pypdf>=3.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "resumeio-dl=resumeio_dl.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
)
