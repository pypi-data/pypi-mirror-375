from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README.md safely
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="axory",
    version="0.1.0",  # Increment this for future releases
    packages=find_packages(),  # Automatically find packages
    install_requires=[
        "requests>=2.30.0",  # Pin a minimum version
    ],
    author="AxoryAI",
    author_email="ayush.sahu@axory.ai",
    description="AxoryAI SDK for Deepfake Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    url="https://github.com/ayushmansahu601/detectifai_sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    include_package_data=True,  # Include non-Python files if needed
)
