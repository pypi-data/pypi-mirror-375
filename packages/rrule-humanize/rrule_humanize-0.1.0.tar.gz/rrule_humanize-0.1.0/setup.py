from setuptools import setup, find_packages

setup(
    name="rrule-humanize",
    version="0.1.0",
    author="PeterS",
    author_email="eng.peter.habib@gmail.com",
    description="A Python library to convert RRULE strings to human-readable text",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/progpeter/rrule-humanize",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-dateutil>=2.8.0",
    ],
)