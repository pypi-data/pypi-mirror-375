from setuptools import setup, find_packages

setup(
    name="armstrong-checker",
    version="0.1.4",
    description= "Library to check if a number is Armstrong",
    author="João Pedro Calaça Costa",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)