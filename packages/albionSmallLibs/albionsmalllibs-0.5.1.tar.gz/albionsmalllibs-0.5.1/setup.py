from setuptools import setup, find_packages

setup(
    name="albionSmallLibs",
    version="0.5.1",
    packages=find_packages(),
    install_requires=[],  # List dependencies here
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple example package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/albionSmallLibs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)