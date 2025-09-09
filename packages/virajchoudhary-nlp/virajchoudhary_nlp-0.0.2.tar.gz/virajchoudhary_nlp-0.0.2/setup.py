import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="virajchoudhary-nlp",
    version="0.0.2",
    author="Viraj Choudhary",
    author_email="virajc188@gmail.com",
    description="A personal toolkit for NLP lab coursework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'nltk',
        'scikit-learn',
        'pandas',
        'requests',
        'beautifulsoup4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)