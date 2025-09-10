# setup.py

from setuptools import setup, find_packages

# Read your README.md using UTF-8 to avoid UnicodeDecodeError
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="MaxCleanerDB",
    version="3.0.8.8",
    author="henry",
    author_email="osas2henry@gmail.com",
    description="easy to set up alternative to SQl, bugs and leak proof by design and also support multiple console interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
    install_requires=[], 
)
