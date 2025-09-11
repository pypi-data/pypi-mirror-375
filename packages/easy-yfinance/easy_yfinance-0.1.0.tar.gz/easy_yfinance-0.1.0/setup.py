from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_desc = fh.read()

setup(
    name="easy_yfinance",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "plotly"
    ],
    description="YFinance için kolay kullanım araçları (Plotly destekli)",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Arı Bilgi",
    url="https://github/aribilgiogr/easy_yfinance",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.10"
)
