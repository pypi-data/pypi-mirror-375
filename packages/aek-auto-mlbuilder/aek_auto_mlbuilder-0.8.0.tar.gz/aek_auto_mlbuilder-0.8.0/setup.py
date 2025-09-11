from setuptools import setup, find_packages

setup(
    name="aek-auto-mlbuilder",        
    version="0.8.0",
    description="Automatic ML model builder in Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Alp Emre Karaahmet",
    author_email="alpemrekaraahmet@gmail.com",
    url="https://github.com/alpemre8/aek-auto-mlbuilder",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "scikit-learn>=1.0",
        "numpy>=1.23",
        "pandas>=1.5"
    ], 
)
