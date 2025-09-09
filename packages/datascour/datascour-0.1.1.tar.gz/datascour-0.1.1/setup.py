from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datascour",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered data cleaning and validation toolkit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiwariPratyush/datascour",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pandas>=1.0",
        "numpy>=1.18",
        "scikit-learn>=0.23",
        "scipy>=1.5",
        "matplotlib>=3.3",
        "seaborn>=0.11",
        "nltk>=3.5",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "check-manifest",
            "twine",
            "jupyter",
            "notebook"
        ],
    },
)
