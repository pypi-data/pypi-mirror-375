#!/usr/bin/env python3
"""
Setup script for heartai - ECG/EKG signal processing and arrhythmia detection library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="heartai",
    version="0.1.0",
    author="AhmetXHero",
    author_email="ahmetxhero@gmail.com",
    description="AI-powered ECG/EKG signal processing and arrhythmia detection library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmetxhero/AhmetX-HeartAi.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "heartai=heartai.cli:main",
        ],
    },
    keywords="ecg ekg arrhythmia detection machine-learning healthcare biosignal",
    project_urls={
        "Bug Reports": "https://github.com/ahmetxhero/AhmetX-HeartAi/issues",
        "Source": "https://github.com/ahmetxhero/AhmetX-HeartAi",
        "Documentation": "https://heartai.readthedocs.io/",
    },
)
