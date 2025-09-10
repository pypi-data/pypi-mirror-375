from setuptools import setup, find_packages

setup(
    name="binlookup",  # Ye PyPI pe package ka naam hoga
    version="0.1.0",
    description="Python wrapper for binlist.net BIN lookup",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Yuvraj Singh",
    url="https://github.com/YOUR_GITHUB/binlookup",  # GitHub repo ka link daalna
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

