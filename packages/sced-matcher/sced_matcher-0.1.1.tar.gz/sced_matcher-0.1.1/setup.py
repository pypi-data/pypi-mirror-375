from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sced-matcher",
    version="0.1.1",
    author="Leoson Hoay",
    author_email="leoson.public@gmail.com",
    description="A tool for matching K-12 course names and descriptions to standardized NCES SCED codes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MPL-2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai",
        "pandas",
        "python-dotenv",
    ],
    include_package_data=True,
    package_data={
        "sced_matcher": ["data/*"],
    },
)