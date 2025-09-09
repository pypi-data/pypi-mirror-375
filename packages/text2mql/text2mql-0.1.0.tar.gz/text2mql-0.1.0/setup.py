from setuptools import setup, find_packages

setup(
    name="text2mql",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Memory Query Language for text2memory ecosystem",
    long_description="text2mql (Memory Query Language) is a specialized language designed for querying memory within the text2memory ecosystem.",
    long_description_content_type="text/plain",
    url="https://github.com/yourusername/text2mql",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
