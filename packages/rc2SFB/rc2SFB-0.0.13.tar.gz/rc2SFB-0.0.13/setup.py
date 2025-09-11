from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rc2SFB",
    version="0.0.13",
    author="Hakan Demir",
    author_email="h.demir@ruhr-uni-bochum.de",
    description=" Tools to read, scale and plot RC2 PIV and OF data  ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XXXXXXXXXX/XXX",
    packages=find_packages(),
    classifiers=[ 
        "Topic :: Scientific/Engineering", 
    ]
    
)
