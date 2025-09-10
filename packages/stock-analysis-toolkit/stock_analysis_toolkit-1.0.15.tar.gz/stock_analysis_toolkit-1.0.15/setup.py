from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    # Metadata
    name="stock-analysis-toolkit",
    version="1.0.15",
    description="A comprehensive toolkit for stock market analysis and reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pranav Phalnikar",
    author_email="phalnikar.pranav@gmail.com",
    url="https://github.com/pranav87/stock_analysis",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "stock_analysis_toolkit": ["**/*.json", "**/*.html", "**/*.css"],
    },
    
    # Dependencies are managed in pyproject.toml
    python_requires=">=3.10",
    
    # Entry points
    entry_points={
        "console_scripts": [
            "stock-analyzer=stock_analysis_toolkit.main:main",
        ],
    },
    
    # Additional metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords=["stocks", "trading", "analysis", "finance", "investing"],
)
