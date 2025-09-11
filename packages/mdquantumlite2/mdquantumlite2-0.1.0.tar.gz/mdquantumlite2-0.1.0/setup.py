from setuptools import setup, find_packages

setup(
    name="mdquantumlite2",
    version="0.1.0",
    author="Parham Dehghan",
    author_email="dehghanparham6@gmail.com",
    description="A lightweight quantum-enhanced regression model based on LightGBM",
    long_description=open("README.md", encoding="utf-8").read(),  # اضافه کردن encoding='utf-8'
    long_description_content_type="text/markdown",
    url="https://github.com/Parham-Dehghan/MD_library",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20",
        "pandas>=1.3",
        "scikit-learn>=1.0",
        "scipy>=1.7",
        "lightgbm>=3.0",
    ],
    extras_require={
        "quantum": ["pennylane>=0.20"],
    },
)