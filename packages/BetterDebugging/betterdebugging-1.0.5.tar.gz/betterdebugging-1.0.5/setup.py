from setuptools import setup, find_packages
with open("README.md", "r") as f:
    long_description = f.read()
setup(
    name="BetterDebugging",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "colorama",
    ],
    extras_require={
        "dev": [
            "pytest",
            "twine",
        ],
    },
    author="Matthew Boyd",
    author_email="MatthewBoyd04@gmail.com",
    description="A utility plugin, allowing you to set custom logging levels with colors and microsecond precision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)