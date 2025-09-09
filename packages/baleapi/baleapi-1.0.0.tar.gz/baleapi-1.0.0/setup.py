from setuptools import setup, find_packages

setup(
    name="baleapi", 
    version="1.0.0",
    description="Python library for Bale Bot API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ali-Jafari",
    author_email="thealiapi@gmail.com",
    url="https://github.com/iTs-GoJo/bale", 
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
