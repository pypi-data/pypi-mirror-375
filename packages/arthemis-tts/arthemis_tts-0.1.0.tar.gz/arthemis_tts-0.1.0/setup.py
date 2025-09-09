from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A simple transformer-based text-to-speech library"

setup(
    name="arthemis-tts",
    version="0.1.0",
    author="Harish Santhnakakshmi Ganesan",
    author_email="harishsg99@gmail.com",
    description="A simple transformer-based text-to-speech library",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/arthemis-tts",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "torch>=1.9.0",
        "torchaudio>=0.9.0",
        "numpy>=1.19.0",
        "pandas>=1.2.0",
        "tqdm>=4.60.0",
        "pydub>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    package_data={
        "arthemis_tts": ["*.pt", "models/*.pt"],
    },
    include_package_data=True,
    keywords="text-to-speech, tts, transformer, neural, speech synthesis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/arthemis-tts/issues",
        "Source": "https://github.com/yourusername/arthemis-tts",
        "Documentation": "https://github.com/yourusername/arthemis-tts#readme",
    },
) 