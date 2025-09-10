from setuptools import setup, find_packages

setup(
    name="BinStandard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["aiohttp", "uvloop"],
    entry_points={
        "console_scripts": [
            "binstandard=binstandard.cli:cli",
        ],
    },
    author="@Nactire",
    description="An Simple Library With Fetch Bin info With binlist.net, Fully Asyncio With Uvloop Power.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/BinStandard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

