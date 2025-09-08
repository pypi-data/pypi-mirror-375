from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="apicrusher",
    version="1.3.0",
    author="APICrusher",
    author_email="hello@apicrusher.com",
    description="Cut AI API costs by 63-99% with intelligent routing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/apicrusher",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "redis>=4.5.0",
    ],
)
